"""El tope de gasto, comprobado **antes** de llamar.

La prueba central de este fichero usa un doble de cliente que **lanza si alguien
lo llama**. Si la cuota funciona, ese doble no se toca nunca — y esa es la forma
de comprobar «antes de cualquier llamada al proveedor» en el medio donde la
propiedad es observable. Comprobar que la llamada no se produjo mirando el
resultado es imposible: un rechazo posterior se parece mucho a uno anterior.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.test import override_settings

from apps.ia.cuota import CuotaSuperada, comprobar_cuota, coste_de, gasto_del_mes
from apps.ia.models import LlamadaLLM
from apps.ia.registro import registrar_llamada


class ClienteQueNoDebeLlamarse:
    """Si la cuota corta a tiempo, este objeto nunca se toca."""

    def __getattr__(self, nombre):
        raise AssertionError(f"se ha llamado al proveedor ({nombre}) pese a tener la cuota agotada")


class Uso:
    """Doble del objeto `usage` que devuelve el proveedor."""

    def __init__(self, entrada=1000, salida=500, cache_escritura=0, cache_lectura=0):
        self.input_tokens = entrada
        self.output_tokens = salida
        self.cache_creation_input_tokens = cache_escritura
        self.cache_read_input_tokens = cache_lectura


def _gastar(usuario, importe: str, **extra):
    llamada = registrar_llamada(
        usuario=usuario,
        proposito="explicacion",
        modelo="modelo-de-prueba",
        prompt_version="v1",
        usage=None,
        latencia_ms=100,
        **extra,
    )
    LlamadaLLM.objects.filter(pk=llamada.pk).update(coste_eur=Decimal(importe))
    return llamada


# ---------------------------------------------------------------------------
# El freno
# ---------------------------------------------------------------------------


def _explicar(usuario, cliente):
    """Reproduce el orden que el paso 17 tendrá que respetar en `services.py`.

    Primero el freno, después el motor. Si alguien invirtiera estas dos líneas,
    el doble lo diría — y esa es toda la propiedad que se quiere fijar aquí.
    """
    comprobar_cuota(usuario)
    return cliente.messages.create(model="x")


@pytest.mark.django_db
def test_con_la_cuota_agotada_no_se_llega_a_llamar_al_proveedor(usuario):
    """La prueba central del paso.

    El doble lanza `AssertionError` en cuanto alguien le toca un atributo. Como
    lo que se espera es `CuotaSuperada`, si el orden se invirtiera esta prueba
    fallaría con el error del doble en vez de pasar: la diferencia entre las dos
    excepciones **es** la comprobación.
    """
    _gastar(usuario, "5.00")  # el tope por defecto son 5,00 €

    with pytest.raises(CuotaSuperada):
        _explicar(usuario, ClienteQueNoDebeLlamarse())

    assert LlamadaLLM.objects.count() == 1  # ninguna fila nueva


@pytest.mark.django_db
def test_el_doble_de_cliente_si_puede_fallar(usuario):
    """Comprobación de la comprobación: sin freno delante, el doble revienta.

    Sin esto, la prueba anterior pasaría igual aunque el doble fuera inofensivo,
    y no estaría comprobando nada.
    """
    with pytest.raises(AssertionError, match="se ha llamado al proveedor"):
        ClienteQueNoDebeLlamarse().messages.create(model="x")


@pytest.mark.django_db
def test_justo_por_debajo_del_tope_se_permite(usuario):
    _gastar(usuario, "4.99")

    comprobar_cuota(usuario)  # no lanza


@pytest.mark.django_db
def test_justo_en_el_tope_se_rechaza(usuario):
    """El límite es inclusivo por el lado del rechazo.

    Un tope que solo actúa al superarse deja pasar siempre una llamada más, y esa
    es justo la que no estaba presupuestada.
    """
    _gastar(usuario, "5.00")

    with pytest.raises(CuotaSuperada):
        comprobar_cuota(usuario)


# ---------------------------------------------------------------------------
# El contador
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_el_gasto_es_de_cada_uno(usuario, otro_usuario):
    _gastar(usuario, "1.00")
    _gastar(otro_usuario, "4.00")

    assert gasto_del_mes(usuario) == Decimal("1.00")


@pytest.mark.django_db
def test_solo_cuenta_el_mes_en_curso(usuario):
    from django.utils import timezone

    antigua = _gastar(usuario, "3.00")
    LlamadaLLM.objects.filter(pk=antigua.pk).update(
        creada_el=timezone.now() - timezone.timedelta(days=70)
    )
    _gastar(usuario, "1.00")

    assert gasto_del_mes(usuario) == Decimal("1.00")


@pytest.mark.django_db
def test_sin_llamadas_el_gasto_es_cero_y_no_none(usuario):
    assert gasto_del_mes(usuario) == Decimal("0")


# ---------------------------------------------------------------------------
# El coste
# ---------------------------------------------------------------------------


@override_settings(PRECIO_ENTRADA_EUR_POR_MTOK="5", PRECIO_SALIDA_EUR_POR_MTOK="25")
def test_el_coste_sale_del_uso_reportado():
    """1000 de entrada a 5 €/Mtok más 500 de salida a 25 €/Mtok."""
    coste = coste_de(Uso(entrada=1000, salida=500), "modelo-x")

    assert coste == Decimal("0.0175")


@override_settings(PRECIO_ENTRADA_EUR_POR_MTOK=0, PRECIO_SALIDA_EUR_POR_MTOK=0)
def test_sin_tarifas_configuradas_el_coste_es_cero_y_no_revienta():
    """Se registra el uso aunque no se pueda imputar el gasto."""
    assert coste_de(Uso(), "modelo-x") == Decimal("0")


def test_sin_uso_reportado_el_coste_es_cero():
    assert coste_de(None, "modelo-x") == Decimal("0")


@pytest.mark.django_db
@override_settings(PRECIO_ENTRADA_EUR_POR_MTOK="5", PRECIO_SALIDA_EUR_POR_MTOK="25")
def test_los_cuatro_contadores_vienen_del_proveedor(usuario):
    llamada = registrar_llamada(
        usuario=usuario,
        proposito="explicacion",
        modelo="modelo-x",
        prompt_version="v1",
        usage=Uso(entrada=1200, salida=300, cache_escritura=100, cache_lectura=50),
        latencia_ms=842,
    )

    assert llamada.tokens_entrada == 1200
    assert llamada.tokens_salida == 300
    assert llamada.tokens_cache_escritura == 100
    assert llamada.tokens_cache_lectura == 50
    assert llamada.coste_eur > 0
