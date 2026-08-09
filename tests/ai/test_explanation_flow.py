"""
Flujo completo de la capa de IA, sin salir a la red.

    AnalysisResult -> ExplanationRequest -> [modelo] -> ExplanationDraft
                   -> validación -> AIExplanation -> informe

Se ejercita con dobles guionizados. Lo que se comprueba no es que el modelo
escriba bien, sino que TPIP se comporte igual de bien cuando escribe mal.
"""

import io

import pytest
from pypdf import PdfReader

from ai import claude_client
from ai.claude_client import (
    ClaudeUnavailable,
    explain_analysis,
    extract_text,
    parse_draft,
    request_explanation,
    resolve_api_key,
    resolve_model,
)
from ai.schemas import ExplanationRequest
from ai.validators import ExplanationRejected
from infrastructure.report.pdf_report import render_report_bytes
from tests.ai.mocks import (
    FENCED_VALID_RESPONSE,
    INVENTED_SOURCE_RESPONSE,
    MALFORMED_RESPONSE,
    UNEMITTED_NORM_RESPONSE,
    VALID_RESPONSE,
    VERDICT_CHANGE_RESPONSE,
    FakeAnthropic,
)
from tests.domain.conftest import make_transaction
from tp_domain.calculations.arm_length_range import calculate_arm_length_range
from tp_domain.models import AIExplanation


@pytest.fixture(scope="module")
def result(comparables):
    return calculate_arm_length_range(make_transaction("software", 12.0), comparables)


def _report_text(result) -> str:
    reader = PdfReader(io.BytesIO(render_report_bytes(result)))
    return "\n".join(page.extract_text() for page in reader.pages)


# ---------------------------------------------------------------------------
# Camino feliz
# ---------------------------------------------------------------------------

def test_valid_response_becomes_an_attached_explanation(result):
    client = FakeAnthropic(responses=[VALID_RESPONSE])
    explanation = request_explanation(result, client=client, model="modelo-x")

    assert isinstance(explanation, AIExplanation)
    assert explanation.model == "modelo-x"
    assert explanation.prompt_version == "explain_analysis_v1"
    assert client.call_count == 1

    enriched = result.model_copy(update={"ai_explanation": explanation})
    assert "percentil 90" in _report_text(enriched)


def test_prompt_and_payload_reach_the_api(result):
    client = FakeAnthropic()
    request_explanation(result, client=client, model="modelo-x")
    call = client.calls[0]

    assert "REGLAS INVIOLABLES" in call["system"]
    assert call["model"] == "modelo-x"
    payload = call["messages"][0]["content"]
    assert result.analysis_id in payload
    assert "Byteworks" not in payload  # los comparables no viajan


def test_fenced_json_is_tolerated(result):
    """Envolver el JSON en un bloque de código es el desliz más habitual."""
    client = FakeAnthropic(responses=[FENCED_VALID_RESPONSE])
    assert request_explanation(result, client=client, model="m").text


# ---------------------------------------------------------------------------
# Respuestas defectuosas
# ---------------------------------------------------------------------------

def test_invented_source_is_rejected(result):
    client = FakeAnthropic(responses=[INVENTED_SOURCE_RESPONSE] * 2)
    with pytest.raises(ExplanationRejected, match="no emitió"):
        request_explanation(result, client=client, model="m")


def test_unemitted_norm_in_prose_is_rejected(result):
    """
    Los ids citados son correctos; la prosa introduce el art. 16 RIS y la
    Directiva 2011/96/UE. Es el hueco que `sources_cited` no cubre.
    """
    client = FakeAnthropic(responses=[UNEMITTED_NORM_RESPONSE] * 2)
    with pytest.raises(ExplanationRejected, match="introduce normativa"):
        request_explanation(result, client=client, model="m")


def test_malformed_response_is_rejected(result):
    client = FakeAnthropic(responses=[MALFORMED_RESPONSE] * 2)
    with pytest.raises(ExplanationRejected, match="no es JSON"):
        request_explanation(result, client=client, model="m")


def test_verdict_change_is_not_machine_detectable(result):
    """
    LÍMITE CONOCIDO, documentado a propósito.

    Esta narrativa contradice al motor —dice que el tipo está dentro de rango
    cuando está por encima del P90— sin citar norma nueva. La validación NO la
    rechaza: detectarlo exigiría comprensión semántica, y perseguirlo con
    heurísticas produciría falsos positivos sobre paráfrasis legítimas.

    Lo que sí está garantizado es que esa prosa no puede alterar el análisis, y
    que el informe imprime la conclusión determinista del motor por encima de
    la sección de IA, donde la contradicción queda a la vista de quien revisa.
    """
    client = FakeAnthropic(responses=[VERDICT_CHANGE_RESPONSE])
    explanation = request_explanation(result, client=client, model="m")

    enriched = result.model_copy(update={"ai_explanation": explanation})
    text = _report_text(enriched)

    assert "dentro del rango" in explanation.text          # el modelo miente
    assert "Por encima del P90" in text                     # el motor manda
    assert "Riesgo alto" in text
    assert "10.1%" in text                                  # ajuste alemán intacto


# ---------------------------------------------------------------------------
# Reintento
# ---------------------------------------------------------------------------

def test_retry_recovers_from_a_first_bad_draft(result):
    client = FakeAnthropic(responses=[INVENTED_SOURCE_RESPONSE, VALID_RESPONSE])
    explanation = request_explanation(result, client=client, model="m")

    assert explanation.sources_cited == ["es-lis-art18-4", "de-astg-1-3a"]
    assert client.call_count == 2


def test_retry_carries_only_the_rejection_reasons(result):
    """
    El segundo intento no puede recibir información nueva del análisis: si la
    recibiera, podría decir en la corrección cosas que no podía decir antes.
    """
    client = FakeAnthropic(responses=[INVENTED_SOURCE_RESPONSE, VALID_RESPONSE])
    request_explanation(result, client=client, model="m")

    retry_message = client.calls[1]["messages"][-1]["content"]
    assert "rechazado por la validación" in retry_message
    assert "no emitió" in retry_message
    assert result.conclusion not in retry_message
    assert str(result.benchmark.percentile_90) not in retry_message


def test_only_one_retry(result):
    client = FakeAnthropic(responses=[INVENTED_SOURCE_RESPONSE] * 5)
    with pytest.raises(ExplanationRejected):
        request_explanation(result, client=client, model="m")
    assert client.call_count == 2


# ---------------------------------------------------------------------------
# Degradación: nada tumba el informe
# ---------------------------------------------------------------------------

def test_explain_analysis_returns_none_instead_of_raising(result):
    client = FakeAnthropic(responses=[INVENTED_SOURCE_RESPONSE] * 2)
    assert explain_analysis(result, client=client, model="m") is None


def test_api_failure_returns_none(result):
    client = FakeAnthropic(raises=RuntimeError("502 Bad Gateway"))
    assert explain_analysis(result, client=client, model="m") is None


def test_report_is_complete_without_an_api_key(result, monkeypatch):
    """
    Sin clave, la aplicación funciona igual y el PDF sale entero declarando la
    ausencia de la sección de IA.
    """
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(claude_client, "resolve_api_key", lambda: None)

    assert explain_analysis(result) is None

    text = _report_text(result)
    assert "sin asistencia de IA" in text
    assert "Resumen ejecutivo" in text
    assert "Anexo" in text


def test_build_client_without_key_is_explicit(monkeypatch):
    monkeypatch.setattr(claude_client, "resolve_api_key", lambda: None)
    with pytest.raises(ClaudeUnavailable, match="ANTHROPIC_API_KEY"):
        claude_client.build_client()


# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

def test_env_var_takes_precedence_over_dotenv(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "clave-de-entorno")
    assert resolve_api_key() == "clave-de-entorno"


def test_configured_model_wins(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_MODEL", "modelo-fijado-a-mano")
    assert resolve_model(FakeAnthropic()) == "modelo-fijado-a-mano"


def test_model_defaults_to_the_newest_available_sonnet(monkeypatch):
    """
    Sin ANTHROPIC_MODEL no se adivina un nombre: se pregunta al catálogo. El
    valor por defecto envejece solo en lugar de quedar clavado en el código.
    """
    monkeypatch.delenv("ANTHROPIC_MODEL", raising=False)
    assert resolve_model(FakeAnthropic()) == "claude-sonnet-test-2"


def test_model_resolution_fails_loudly_when_no_sonnet_exists(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_MODEL", raising=False)
    with pytest.raises(ClaudeUnavailable, match="ANTHROPIC_MODEL"):
        resolve_model(FakeAnthropic(catalogue=[]))


def test_resolved_model_id_is_recorded_for_reproducibility(result, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_MODEL", raising=False)
    client = FakeAnthropic()
    explanation = request_explanation(result, client=client)
    assert explanation.model == "claude-sonnet-test-2"
    assert client.calls[0]["model"] == "claude-sonnet-test-2"


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def test_extract_text_joins_text_blocks():
    from tests.ai.mocks import _Block, _Message

    assert extract_text(_Message(content=[_Block("uno "), _Block("dos")])) == "uno dos"


def test_parse_draft_rejects_a_json_array():
    with pytest.raises(ExplanationRejected, match="objeto JSON"):
        parse_draft("[1, 2, 3]")


def test_parse_draft_rejects_unexpected_keys():
    with pytest.raises(ExplanationRejected, match="esquema"):
        parse_draft('{"narrative": "x", "sources_cited": [], "verdict": "STRONG"}')


def test_request_projection_is_what_travels(result):
    """La entrada del modelo es la proyección, nunca el AnalysisResult."""
    payload = ExplanationRequest.from_result(result)
    assert set(payload.model_dump()) == {
        "analysis_id", "method", "method_rationale", "transaction", "benchmark",
        "position", "assessments", "risk_factors", "engine_conclusion",
        "allowed_sources",
    }
