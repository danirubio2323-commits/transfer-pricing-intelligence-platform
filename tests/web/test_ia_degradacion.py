"""La capa de IA puede caerse entera sin que el producto se entere.

Cinco caminos distintos llevan a «sin explicación», y los cinco tienen que
acabar igual: el análisis se completa, el caso se guarda y el informe sale
declarando la ausencia. **Ninguna de estas pruebas toca la red.**

La razón de cubrirlos por separado y no con un solo caso genérico: se parecen
desde fuera —todos dan un 302 y un caso sin explicación— pero se rompen por
motivos distintos, y el día que uno deje de degradar bien, los otros cuatro
seguirían pasando.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.test import override_settings
from django.urls import reverse

from apps.analisis.models import Caso
from apps.ia.models import LlamadaLLM

VALIDO = {
    "titulo": "",
    "description": "Canon por licencia de tecnología",
    "payer_country": "ES",
    "recipient_country": "DE",
    "transaction_type": "royalty",
    "industry": "software",
    "amount_eur": "1000000",
    "rate_percent": "8.0",
    "effective_date": "2026-01-01",
}


@pytest.fixture
def autenticado(client, usuario):
    client.force_login(usuario)
    return client


def _analizar(cliente):
    return cliente.post(reverse("analisis:crear"), VALIDO)


def _sin_explicacion(respuesta):
    """Lo que las cinco rutas comparten: el producto sigue en pie."""
    assert respuesta.status_code == 302
    caso = Caso.objects.get()
    assert caso.has_ai_explanation is False
    assert caso.payload.get("ai_explanation") is None
    return caso


# ---------------------------------------------------------------------------
# Ruta 1 — sin clave
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(ANTHROPIC_API_KEY=None, ANTHROPIC_MODEL="modelo-x")
def test_sin_clave_el_analisis_se_completa_igual(autenticado):
    _sin_explicacion(_analizar(autenticado))
    assert LlamadaLLM.objects.count() == 0


# ---------------------------------------------------------------------------
# Ruta 2 — con clave pero sin modelo
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(ANTHROPIC_API_KEY="clave-de-prueba", ANTHROPIC_MODEL=None)
def test_sin_modelo_no_se_adivina_ninguno(autenticado):
    """El modelo no se descubre en ejecución (paso 8): sin él, la capa se apaga.

    Y no es solo reproducibilidad: sin modelo tampoco hay tarifa, y sin tarifa no
    hay tope comprobable antes del gasto.
    """
    _sin_explicacion(_analizar(autenticado))
    assert LlamadaLLM.objects.count() == 0


# ---------------------------------------------------------------------------
# Ruta 3 — cuota agotada
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(ANTHROPIC_API_KEY="clave-de-prueba", ANTHROPIC_MODEL="modelo-x")
def test_con_la_cuota_agotada_no_se_llama_ni_se_registra_fila_nueva(autenticado, usuario):
    """El tope desactiva la sección de IA; nunca bloquea el producto."""
    from apps.ia.registro import registrar_llamada

    gastada = registrar_llamada(
        usuario=usuario,
        proposito="explicacion",
        modelo="modelo-x",
        prompt_version="v1",
        usage=None,
        latencia_ms=1,
    )
    LlamadaLLM.objects.filter(pk=gastada.pk).update(coste_eur=Decimal("5.00"))

    _sin_explicacion(_analizar(autenticado))

    assert LlamadaLLM.objects.count() == 1  # solo la que ya había


# ---------------------------------------------------------------------------
# Ruta 4 — el proveedor falla
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(ANTHROPIC_API_KEY="clave-de-prueba", ANTHROPIC_MODEL="modelo-x")
def test_si_el_proveedor_falla_se_registra_el_intento_con_coste_cero(autenticado, monkeypatch):
    """Hubo intento aunque no hubiera resultado: queda rastro y cuesta 0."""
    from ai import claude_client

    monkeypatch.setattr(claude_client, "explain_analysis", lambda *a, **k: None)

    _sin_explicacion(_analizar(autenticado))

    llamada = LlamadaLLM.objects.get()
    assert llamada.error
    assert llamada.coste_eur == Decimal("0")


# ---------------------------------------------------------------------------
# Ruta 5 — el borrador no pasa el validador
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(ANTHROPIC_API_KEY="clave-de-prueba", ANTHROPIC_MODEL="modelo-x")
def test_un_borrador_que_cita_lo_que_el_motor_no_emitio_no_llega_al_caso(autenticado, monkeypatch):
    """La salvaguarda central del producto, ejercitada en el circuito completo.

    Aquí NO se simula el resultado del validador: se inyecta un cliente falso que
    devuelve un borrador citando `es-rd634-2015-art16`, una fuente que el motor no
    emitió, y se deja que corra el validador de verdad. Si algún día alguien lo
    desconectara, esta prueba lo diría — simular su respuesta no lo haría.

    Es lo que impide que el modelo se invente un artículo que no existe, que en
    este terreno es el único fallo que destruye la credibilidad del informe.
    """
    from ai import claude_client
    from tests.ai.mocks import INVENTED_SOURCE_RESPONSE, FakeAnthropic

    # Se sustituye el constructor del cliente, no `explain_analysis`: así el
    # camino que se recorre es el real, validador incluido.
    monkeypatch.setattr(
        claude_client,
        "build_client",
        lambda: FakeAnthropic(responses=[INVENTED_SOURCE_RESPONSE] * 2),
    )

    caso = _sin_explicacion(_analizar(autenticado))

    assert caso.payload.get("ai_explanation") is None


# ---------------------------------------------------------------------------
# El camino feliz
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(
    ANTHROPIC_API_KEY="clave-de-prueba",
    ANTHROPIC_MODEL="modelo-x",
    PRECIO_ENTRADA_EUR_POR_MTOK="5",
    PRECIO_SALIDA_EUR_POR_MTOK="25",
)
def test_una_explicacion_valida_se_persiste_y_se_registra(autenticado, monkeypatch):
    from ai import claude_client
    from ai.claude_client import RespuestaIA
    from tp_domain.models import AIExplanation

    class Uso:
        input_tokens = 1200
        output_tokens = 300
        cache_creation_input_tokens = 0
        cache_read_input_tokens = 0

    explicacion = AIExplanation(
        text="El tipo se sitúa dentro del rango intercuartílico según el análisis del motor.",
        prompt_version="explain_analysis_v1",
        model="modelo-x",
        sources_cited=["es-lis-art18-4"],
    )
    monkeypatch.setattr(
        claude_client,
        "explain_analysis",
        lambda *a, **k: RespuestaIA(explicacion=explicacion, usage=Uso(), stop_reason="end_turn"),
    )

    respuesta = _analizar(autenticado)

    assert respuesta.status_code == 302
    caso = Caso.objects.get()
    assert caso.has_ai_explanation is True

    llamada = LlamadaLLM.objects.get()
    assert llamada.proposito == "explicacion"
    assert llamada.tokens_entrada == 1200
    assert llamada.tokens_salida == 300
    assert llamada.coste_eur > 0
    assert llamada.caso == caso
