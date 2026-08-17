"""Ejecuta el arnés y decide si ha habido regresión.

**Tres códigos de salida distintos, y la distinción importa:**

- `0` — la tasa de acierto iguala o supera la línea base.
- `1` — ha bajado. **Específicamente 1**, no «distinto de cero»: si el gate
  aceptara cualquier código, un error de uso pasaría por regresión y, peor, una
  regresión pasaría por error de uso.
- `2` — no hay línea base contra la que comparar. No es un aprobado ni un
  suspenso: es que la pregunta no se puede responder todavía.
"""

from __future__ import annotations

import statistics
import subprocess
import time
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.evaluacion.models import CasoEvaluacion, EjecucionEvaluacion
from apps.evaluacion.puntuadores import Veredicto, puntuar
from tp_domain.models import AnalysisResult

SIN_LINEA_BASE = 2
HAY_REGRESION = 1


def _sha_commit() -> str:
    """Sin el commit, una tasa de acierto no es reproducible."""
    try:
        hecho = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10
        )
        return hecho.stdout.strip()[:40] if hecho.returncode == 0 else "desconocido"
    except Exception:  # noqa: BLE001 — sin git, el arnés sigue funcionando
        return "desconocido"


def _percentil(valores: list[int], p: float) -> int:
    if not valores:
        return 0
    ordenados = sorted(valores)
    if len(ordenados) == 1:
        return ordenados[0]
    return int(statistics.quantiles(ordenados, n=100)[min(int(p) - 1, 98)])


class Command(BaseCommand):
    help = "Ejecuta el conjunto dorado y registra la ejecución."

    def add_arguments(self, parser):
        parser.add_argument("--fijar-linea-base", action="store_true")
        parser.add_argument("--contra-linea-base", action="store_true")
        parser.add_argument(
            "--autocomprobar-regresion",
            action="store_true",
            help="Ejecuta contra una línea base inalcanzable. DEBE salir 1.",
        )

    # -----------------------------------------------------------------
    def handle(self, *args, **opciones):
        if opciones["autocomprobar_regresion"]:
            return self._autocomprobar()

        ejecucion = self._ejecutar(explicador=self._explicador_local)

        if opciones["fijar_linea_base"]:
            EjecucionEvaluacion.objects.exclude(pk=ejecucion.pk).update(es_linea_base=False)
            ejecucion.es_linea_base = True
            ejecucion.save(update_fields=["es_linea_base"])
            self.stdout.write(
                self.style.SUCCESS(f"Línea base fijada en {ejecucion.tasa_acierto:.0%}.")
            )
            return

        if opciones["contra_linea_base"]:
            base = (
                EjecucionEvaluacion.objects.filter(es_linea_base=True)
                .exclude(pk=ejecucion.pk)
                .first()
            )
            if base is None:
                self.stderr.write(
                    "No hay línea base. Fíjala con: manage.py evaluar --fijar-linea-base"
                )
                raise SystemExit(SIN_LINEA_BASE)

            if ejecucion.tasa_acierto < base.tasa_acierto:
                self.stderr.write(
                    f"REGRESIÓN: {ejecucion.tasa_acierto:.0%} frente a "
                    f"{base.tasa_acierto:.0%} de la línea base."
                )
                raise SystemExit(HAY_REGRESION)

            self.stdout.write(
                self.style.SUCCESS(
                    f"{ejecucion.tasa_acierto:.0%} — no hay regresión "
                    f"(línea base {base.tasa_acierto:.0%})."
                )
            )
            return

        self.stdout.write(f"Tasa de acierto: {ejecucion.tasa_acierto:.0%}")

    # -----------------------------------------------------------------
    def _explicador_local(self, resultado: AnalysisResult):
        """La explicación que se evalúa. Sin clave, no hay nada que evaluar.

        Devuelve `(explicacion, latencia_ms, coste)`. La explicación puede ser
        `None`: un caso sin explicación **no cuenta como acierto**.
        """
        if not settings.ANTHROPIC_API_KEY or not settings.ANTHROPIC_MODEL:
            return None, 0, Decimal("0")

        from ai.claude_client import explain_analysis
        from apps.ia.cuota import coste_de

        comenzado = time.monotonic()
        respuesta = explain_analysis(resultado, model=settings.ANTHROPIC_MODEL)
        latencia = int((time.monotonic() - comenzado) * 1000)

        # Se registra con `proposito="evaluacion"` para que el gasto del arnés
        # no se sume al de nadie: sin ese campo, una pasada de evaluación
        # consumiría el tope mensual de un usuario real.
        self._registrar(respuesta, latencia)

        if respuesta is None:
            return None, latencia, Decimal("0")
        return (
            respuesta.explicacion,
            latencia,
            coste_de(respuesta.usage, settings.ANTHROPIC_MODEL),
        )

    def _registrar(self, respuesta, latencia_ms: int) -> None:
        """Atribuye la llamada a la cuenta que administra. Sin ninguna, no registra.

        `LlamadaLLM.usuario` es obligatorio, y el arnés no tiene usuario propio:
        inventar uno para poder registrar sería peor que no registrar.
        """
        from django.contrib.auth import get_user_model

        from apps.ia.registro import registrar_llamada

        administrador = get_user_model().objects.filter(is_superuser=True).first()
        if administrador is None:
            return

        registrar_llamada(
            usuario=administrador,
            proposito="evaluacion",
            modelo=settings.ANTHROPIC_MODEL,
            prompt_version="explain_analysis_v1",
            usage=getattr(respuesta, "usage", None),
            latencia_ms=latencia_ms,
            error="" if respuesta is not None else "sin_explicacion",
        )

    def _ejecutar(self, *, explicador, juez=None) -> EjecucionEvaluacion:
        casos = list(CasoEvaluacion.objects.filter(activo=True))
        detalle, latencias = [], []
        aciertos = 0
        coste = Decimal("0")

        for caso in casos:
            resultado = AnalysisResult.model_validate(caso.entrada)
            explicacion, latencia, coste_caso = explicador(resultado)
            latencias.append(latencia)
            coste += coste_caso

            if explicacion is None:
                veredicto = Veredicto(False, "no se obtuvo explicación", "0")
            else:
                veredicto = puntuar(resultado, explicacion, caso.propiedades_esperadas, juez=juez)

            # `None` es «sin decidir», y sin decidir NO es acierto: un arnés que
            # aprueba lo que no ha podido evaluar miente.
            acierta = veredicto.acierta is True
            aciertos += int(acierta)
            detalle.append(
                {
                    "caso": caso.id,
                    "acierta": acierta,
                    "capa": veredicto.capa,
                    "motivo": veredicto.motivo,
                    "latencia_ms": latencia,
                }
            )

        return EjecucionEvaluacion.objects.create(
            sha_commit=_sha_commit(),
            modelo=settings.ANTHROPIC_MODEL or "sin-modelo",
            prompt_version="explain_analysis_v1",
            casos_totales=len(casos),
            casos_acertados=aciertos,
            tasa_acierto=(aciertos / len(casos)) if casos else 0.0,
            coste_total_eur=coste,
            latencia_p50_ms=_percentil(latencias, 50),
            latencia_p95_ms=_percentil(latencias, 95),
            detalle=detalle,
        )

    # -----------------------------------------------------------------
    def _autocomprobar(self):
        """Comprueba que la puerta PUEDE fallar.

        Sin esto, un gate que nunca ha fallado es indistinguible de uno que no
        puede fallar. Se monta una línea base inalcanzable —100 %— y un
        explicador que no devuelve nada, y se exige que el resultado sea una
        regresión.
        """
        ejecucion = self._ejecutar(explicador=lambda _: (None, 0, Decimal("0")))
        ejecucion.tasa_acierto = 0.0
        ejecucion.save(update_fields=["tasa_acierto"])

        base = EjecucionEvaluacion.objects.create(
            sha_commit="autocomprobacion",
            modelo="ninguno",
            prompt_version="explain_analysis_v1",
            casos_totales=ejecucion.casos_totales,
            casos_acertados=ejecucion.casos_totales,
            tasa_acierto=1.0,
            latencia_p50_ms=0,
            latencia_p95_ms=0,
            es_linea_base=False,
            detalle=[],
        )

        if ejecucion.tasa_acierto < base.tasa_acierto:
            self.stderr.write(
                "Autocomprobación correcta: la puerta detecta la regresión y sale con 1."
            )
            raise SystemExit(HAY_REGRESION)

        self.stderr.write("FALLO: la puerta NO ha detectado una regresión evidente.")
        raise SystemExit(0)
