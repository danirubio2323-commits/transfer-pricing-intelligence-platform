"""El único punto donde se juntan Django y el dominio, y Django y la capa de IA.

Aquí no hay nada de HTTP: ni `request`, ni `HttpResponse`, ni códigos de estado.
Esa frontera es lo que permite que este mismo código lo llame mañana un comando
de gestión o el arnés de evaluación sin arrastrar una petición web falsa.

**El principio rector, hecho código:** cuando se llama al modelo, el
`AnalysisResult` ya está calculado entero. La explicación se añade encima y no
puede modificar nada de lo anterior — no reescribe un percentil, no cambia un
veredicto, no añade una fuente. El motor calcula; el modelo explica.

`ai/` sigue sin importar Django. El modelo y la clave se le inyectan desde aquí,
que es el único sitio del proyecto que conoce las dos orillas.
"""

from __future__ import annotations

import time

import structlog
from django.conf import settings

from apps.analisis.models import Caso
from apps.comun.escrituras import crear_caso_de
from apps.ia.cuota import CuotaSuperada, comprobar_cuota
from apps.ia.registro import registrar_llamada
from tp_domain.calculations.arm_length_range import calculate_arm_length_range
from tp_domain.models import AnalysisResult, Transaction

logger = structlog.get_logger(__name__)

#: Motivos por los que la capa de IA puede quedarse fuera. Se registran para que
#: «no hubo explicación» sea diagnosticable y no un misterio silencioso.
SIN_CLAVE = "sin_clave"
SIN_MODELO = "sin_modelo"
CUOTA = "cuota_superada"
FALLO = "fallo_del_proveedor"
RECHAZADA = "borrador_rechazado"


def _explicar(usuario, resultado: AnalysisResult):
    """Devuelve `(respuesta, motivo)`. Nunca lanza y nunca modifica el resultado.

    El orden importa y está fijado: **primero la cuota, después el proveedor**.
    Invertirlo haría que el tope se comprobase con el gasto ya hecho.
    """
    try:
        comprobar_cuota(usuario)
    except CuotaSuperada:
        return None, CUOTA

    if not settings.ANTHROPIC_API_KEY:
        return None, SIN_CLAVE
    if not settings.ANTHROPIC_MODEL:
        # El modelo no se descubre en ejecución (paso 8): sin él, la capa se
        # desactiva en vez de adivinar, y así no hay gasto sin tarifa conocida.
        return None, SIN_MODELO

    from ai.claude_client import explain_analysis

    comenzado = time.monotonic()
    respuesta = explain_analysis(resultado, model=settings.ANTHROPIC_MODEL)
    latencia = int((time.monotonic() - comenzado) * 1000)

    if respuesta is None:
        # `explain_analysis` no lanza: agrupa el fallo del proveedor y el
        # borrador rechazado. Se registra la llamada igual —hubo gasto o hubo
        # intento— con coste 0 al no haber uso reportado.
        registrar_llamada(
            usuario=usuario,
            proposito="explicacion",
            modelo=settings.ANTHROPIC_MODEL,
            prompt_version="explain_analysis_v1",
            usage=None,
            latencia_ms=latencia,
            error=FALLO,
        )
        return None, FALLO

    return (respuesta, latencia), None


def crear_caso(usuario, transaction: Transaction, titulo: str) -> Caso:
    """Calcula, explica si se puede, persiste con propietario y devuelve el caso.

    El motor se ejecuta entero antes de tocar nada más: si el cálculo fallara, no
    queda una fila a medias. La capa de IA es **aditiva** — si no está
    disponible, el caso se guarda igual y el informe sale completo declarando su
    ausencia.
    """
    resultado = calculate_arm_length_range(transaction)

    explicada, motivo = _explicar(usuario, resultado)
    if explicada is not None:
        respuesta, latencia = explicada
        # La explicación se ADJUNTA al resultado ya calculado. `AnalysisResult`
        # no se reconstruye: si el borrador citara algo que el motor no emitió,
        # el validador ya lo habría rechazado antes de llegar aquí.
        resultado = resultado.model_copy(update={"ai_explanation": respuesta.explicacion})

    caso = crear_caso_de(usuario, titulo, resultado.model_dump(mode="json"))

    if explicada is not None:
        respuesta, latencia = explicada
        registrar_llamada(
            usuario=usuario,
            caso=caso,
            proposito="explicacion",
            modelo=respuesta.explicacion.model,
            prompt_version=respuesta.explicacion.prompt_version,
            usage=respuesta.usage,
            latencia_ms=latencia,
            razon_finalizacion=respuesta.stop_reason or "",
        )

    logger.info(
        "caso_creado",
        caso=str(caso.id),
        usuario=usuario.get_username(),
        pagadora=transaction.payer_country,
        perceptora=transaction.recipient_country,
        # La posición vive en cada veredicto por jurisdicción, no en el
        # resultado: el rango es uno, pero el Derecho aplicable es de cada país.
        posiciones={a.country: getattr(a.position, "value", None) for a in resultado.assessments},
        con_explicacion=explicada is not None,
        sin_explicacion_por=motivo,
    )
    return caso
