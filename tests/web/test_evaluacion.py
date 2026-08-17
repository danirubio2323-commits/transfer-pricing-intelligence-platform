"""El arnés de evaluación. Con dobles, sin red.

Lo que se protege aquí es que **la puerta pueda fallar**. Un gate que nunca ha
fallado es indistinguible de uno que no puede fallar, y el segundo da la misma
tranquilidad sin ninguno de los beneficios.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.core.management import call_command

from apps.evaluacion.models import CasoEvaluacion, EjecucionEvaluacion
from apps.evaluacion.puntuadores import deterministas, lexicos, puntuar
from tp_domain.models import AIExplanation, AnalysisResult


@pytest.fixture
def dorado(db):
    call_command("reindexar_evaluacion")
    return CasoEvaluacion.objects.all()


def _resultado(caso) -> AnalysisResult:
    return AnalysisResult.model_validate(caso.entrada)


def _explicacion(texto: str, fuentes: list[str]) -> AIExplanation:
    return AIExplanation(
        text=texto, prompt_version="explain_analysis_v1", model="modelo-x", sources_cited=fuentes
    )


TEXTO_BASE = (
    "El tipo analizado se sitúa fuera del rango intercuartílico según el análisis "
    "del motor. El artículo 18.4 LIS no impone un ajuste automático, mientras que "
    "el §1.3a AStG sí lo impone como consecuencia por defecto, lo que eleva la "
    "exigencia de documentación soporte en la jurisdicción pagadora y obliga a "
    "sostener la posición con un análisis funcional suficiente y verificable."
)


# ---------------------------------------------------------------------------
# El índice
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_reindexar_el_conjunto_dorado_es_idempotente(dorado):
    primera = set(CasoEvaluacion.objects.values_list("id", flat=True))

    call_command("reindexar_evaluacion")

    assert set(CasoEvaluacion.objects.values_list("id", flat=True)) == primera


@pytest.mark.django_db
def test_el_conjunto_dorado_vive_en_control_de_versiones(dorado):
    """Un conjunto que solo existe en la base de datos no se revisa en un PR."""
    from pathlib import Path

    from django.conf import settings

    ficheros = list((Path(settings.BASE_DIR) / "evaluacion" / "casos").glob("*.json"))

    assert len(ficheros) == CasoEvaluacion.objects.count()


# ---------------------------------------------------------------------------
# Los puntuadores: baratos primero, y parando en el primero que decide
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_una_fuente_inventada_la_caza_la_capa_1(dorado):
    caso = CasoEvaluacion.objects.first()
    resultado = _resultado(caso)

    veredicto = puntuar(
        resultado, _explicacion(TEXTO_BASE, ["es-rd634-2015-art16"]), caso.propiedades_esperadas
    )

    assert veredicto.acierta is False
    assert veredicto.capa == "1"  # no ha hecho falta llegar más lejos


@pytest.mark.django_db
def test_una_cifra_inventada_la_caza_la_capa_1(dorado):
    """El modelo no puede escribir un percentil que el motor no emitió."""
    caso = CasoEvaluacion.objects.first()
    resultado = _resultado(caso)
    texto = TEXTO_BASE + " El percentil 75 se sitúa en el 99,99 %."

    veredicto = deterministas(resultado, _explicacion(texto, []), caso.propiedades_esperadas)

    assert veredicto.acierta is False
    assert "cifras" in veredicto.motivo


@pytest.mark.django_db
def test_no_citar_las_fuentes_esperadas_lo_caza_la_capa_2(dorado):
    caso = CasoEvaluacion.objects.get(pk="es-de-sobre-p75")
    resultado = _resultado(caso)

    veredicto = lexicos(resultado, _explicacion(TEXTO_BASE, []), caso.propiedades_esperadas)

    assert veredicto.acierta is False
    assert veredicto.capa == "2"


@pytest.mark.django_db
def test_un_caso_decidido_por_la_capa_1_no_llega_al_juez(dorado):
    """El orden es la política de coste: lo barato decide y se para."""
    caso = CasoEvaluacion.objects.first()
    llamadas_al_juez = []

    def juez(*args, **kwargs):
        llamadas_al_juez.append(1)
        raise AssertionError("no debería haberse llegado al juez")

    puntuar(
        _resultado(caso),
        _explicacion("corto", ["es-lis-art18-4"]),  # extensión fuera de rango
        caso.propiedades_esperadas,
        juez=juez,
    )

    assert llamadas_al_juez == []


@pytest.mark.django_db
def test_sin_juez_un_caso_indeciso_no_cuenta_como_acierto(dorado):
    """Un arnés que aprueba lo que no ha podido evaluar miente."""
    caso = CasoEvaluacion.objects.get(pk="es-de-dentro-del-rango")
    texto = "Una explicación larga y correcta " * 20  # sin referencias legales

    veredicto = puntuar(
        _resultado(caso), _explicacion(texto, ["es-lis-art18-4"]), caso.propiedades_esperadas
    )

    assert veredicto.acierta is not True


# ---------------------------------------------------------------------------
# La puerta
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_sin_linea_base_sale_con_2(dorado):
    """No es un aprobado ni un suspenso: la pregunta no se puede responder."""
    with pytest.raises(SystemExit) as salida:
        call_command("evaluar", "--contra-linea-base")

    assert salida.value.code == 2


@pytest.mark.django_db
def test_fijar_la_linea_base_deja_exactamente_una(dorado):
    call_command("evaluar", "--fijar-linea-base")
    call_command("evaluar", "--fijar-linea-base")

    assert EjecucionEvaluacion.objects.filter(es_linea_base=True).count() == 1


@pytest.mark.django_db
def test_igualar_la_linea_base_sale_con_0(dorado):
    call_command("evaluar", "--fijar-linea-base")

    call_command("evaluar", "--contra-linea-base")  # no lanza


@pytest.mark.django_db
def test_bajar_de_la_linea_base_sale_con_1_exactamente(dorado):
    """Exactamente 1, no «distinto de cero»: un error de uso también sale
    distinto de cero, y un gate escrito así pasaría en vacío para siempre."""
    call_command("evaluar", "--fijar-linea-base")
    EjecucionEvaluacion.objects.filter(es_linea_base=True).update(tasa_acierto=1.0)

    with pytest.raises(SystemExit) as salida:
        call_command("evaluar", "--contra-linea-base")

    assert salida.value.code == 1


@pytest.mark.django_db
def test_la_autocomprobacion_demuestra_que_la_puerta_puede_fallar(dorado):
    """Sin esto, un gate que nunca ha fallado parece uno que no puede fallar."""
    with pytest.raises(SystemExit) as salida:
        call_command("evaluar", "--autocomprobar-regresion")

    assert salida.value.code == 1


# ---------------------------------------------------------------------------
# Lo que se registra
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_la_ejecucion_guarda_coste_y_latencias_junto_a_la_tasa(dorado):
    """Una mejora que triplica el coste es una decisión, no una mejora."""
    call_command("evaluar")

    ejecucion = EjecucionEvaluacion.objects.first()

    assert ejecucion.sha_commit
    assert ejecucion.coste_total_eur == Decimal("0")  # sin clave, no hay gasto
    assert ejecucion.latencia_p50_ms is not None
    assert ejecucion.latencia_p95_ms is not None
    assert ejecucion.casos_totales == CasoEvaluacion.objects.count()


@pytest.mark.django_db
def test_el_detalle_dice_en_que_capa_se_decidio_cada_caso(dorado):
    call_command("evaluar")

    detalle = EjecucionEvaluacion.objects.first().detalle

    assert len(detalle) == CasoEvaluacion.objects.count()
    assert all("capa" in fila and "motivo" in fila for fila in detalle)
