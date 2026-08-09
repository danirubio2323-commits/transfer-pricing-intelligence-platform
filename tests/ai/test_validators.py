"""
Tests de la capa de IA. Ninguno llama a la API.

Lo que se fija aquí es la frontera: qué puede y qué no puede salir del modelo
hacia un informe firmado. Los casos de rechazo importan más que los de
aceptación, porque son los que impiden que TPIP publique una cita inventada.
"""

import pytest

from ai.schemas import ExplanationDraft, ExplanationRequest
from ai.validators import (
    ExplanationRejected,
    allowed_references,
    extract_legal_references,
    validate_draft,
)
from tests.domain.conftest import make_transaction
from tp_domain.calculations.arm_length_range import calculate_arm_length_range
from tp_domain.models import AIExplanation, AnalysisResult

MODEL = "claude-test"

GOOD_NARRATIVE = (
    "El tipo propuesto para el canon se sitúa por encima del percentil 90 de la "
    "muestra sectorial empleada, formada por diecinueve observaciones del sector "
    "del software. El rango intercuartílico de esa muestra va del 8,35% al 11,2%, "
    "con una mediana del 10,1%.\n\n"
    "Las dos jurisdicciones implicadas atribuyen consecuencias distintas a esa "
    "misma posición. En España, el Art. 18.4 LIS no contiene una regla "
    "estadística que imponga un ajuste automático, de modo que la eventual "
    "corrección valorativa queda sujeta a la apreciación caso por caso de la "
    "Inspección y eleva la exigencia de documentación soporte.\n\n"
    "En Alemania, el §1.3a AStG determina el ajuste del valor declarado a la "
    "mediana del rango cuando este queda fuera, salvo que el contribuyente "
    "acredite de forma verosímil que otro punto se ajusta mejor al principio de "
    "plena competencia. La consecuencia por defecto es, por tanto, un tipo del "
    "10,1% en sede alemana."
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def result(comparables) -> AnalysisResult:
    return calculate_arm_length_range(make_transaction("software", 12.0), comparables)


@pytest.fixture(scope="module")
def request_payload(result) -> ExplanationRequest:
    return ExplanationRequest.from_result(result)


def draft(narrative=GOOD_NARRATIVE, sources=("es-lis-art18-4", "de-astg-1-3a")):
    return ExplanationDraft(narrative=narrative, sources_cited=list(sources))


# ---------------------------------------------------------------------------
# Proyección de entrada: qué ve el modelo y qué no
# ---------------------------------------------------------------------------

def test_request_carries_the_calculated_analysis(request_payload, result):
    assert request_payload.analysis_id == result.analysis_id
    assert request_payload.benchmark.percentile_50 == result.benchmark.percentile_50
    assert request_payload.engine_conclusion == result.conclusion
    assert len(request_payload.assessments) == 2


def test_request_hides_the_comparables(request_payload):
    """
    El modelo no ve el listado: no le hace falta para redactar y le daría
    material para inventar observaciones concretas.
    """
    payload = request_payload.model_dump_json()
    assert "Byteworks" not in payload
    assert request_payload.benchmark.count_accepted == 19
    assert request_payload.benchmark.count_rejected == 36


def test_request_hides_internal_repository_paths(request_payload):
    payload = request_payload.model_dump_json()
    assert "documentation/tax-research" not in payload


def test_allowed_sources_mirror_the_engine_registry(request_payload, result):
    assert request_payload.allowed_source_ids == {s.id for s in result.sources}


# ---------------------------------------------------------------------------
# Aceptación
# ---------------------------------------------------------------------------

def test_valid_draft_is_promoted_to_an_explanation(request_payload):
    explanation = validate_draft(draft(), request_payload, model=MODEL)
    assert isinstance(explanation, AIExplanation)
    assert explanation.model == MODEL
    assert explanation.prompt_version == "explain_analysis_v1"
    assert explanation.sources_cited == ["es-lis-art18-4", "de-astg-1-3a"]


def test_promoted_explanation_can_be_attached_to_the_result(result, request_payload):
    """La validación de la capa IA y la del dominio deben coincidir."""
    explanation = validate_draft(draft(), request_payload, model=MODEL)
    attached = result.model_copy(update={"ai_explanation": explanation})
    assert attached.ai_explanation is explanation


def test_less_specific_citation_is_accepted(request_payload):
    """
    "el artículo 18 de la LIS" es menos preciso que "Art. 18.4", pero no
    inventa nada. Rechazarlo sería un falso positivo.
    """
    narrative = GOOD_NARRATIVE.replace("Art. 18.4 LIS", "artículo 18 de la LIS")
    validate_draft(draft(narrative=narrative), request_payload, model=MODEL)


# ---------------------------------------------------------------------------
# Rechazo: fuentes no emitidas
# ---------------------------------------------------------------------------

def test_draft_citing_an_unemitted_source_id_is_rejected(request_payload):
    with pytest.raises(ExplanationRejected, match="no emitió"):
        validate_draft(
            draft(sources=("es-lis-art18-4", "es-lis-art18-13")),
            request_payload, model=MODEL,
        )


def test_rejection_names_the_offending_source(request_payload):
    with pytest.raises(ExplanationRejected) as exc:
        validate_draft(draft(sources=("inventada",)), request_payload, model=MODEL)
    assert "inventada" in str(exc.value)


def test_draft_without_any_citation_is_rejected(request_payload):
    with pytest.raises(ExplanationRejected, match="no cita ninguna fuente"):
        validate_draft(draft(sources=()), request_payload, model=MODEL)


# ---------------------------------------------------------------------------
# Rechazo: normativa introducida en la prosa
#
# Este es el hueco que `sources_cited` no cubre: el modelo puede devolver ids
# impecables y aun así citar una norma nueva en el cuerpo del texto.
# ---------------------------------------------------------------------------

def test_narrative_introducing_a_new_article_is_rejected(request_payload):
    narrative = GOOD_NARRATIVE + (
        "\n\nConviene atender además al artículo 16 del Reglamento del Impuesto "
        "sobre Sociedades."
    )
    with pytest.raises(ExplanationRejected, match="introduce normativa"):
        validate_draft(draft(narrative=narrative), request_payload, model=MODEL)


def test_narrative_introducing_a_new_directive_is_rejected(request_payload):
    narrative = GOOD_NARRATIVE + (
        "\n\nLa Directiva 2011/96/UE resulta igualmente relevante en este caso."
    )
    with pytest.raises(ExplanationRejected, match="introduce normativa"):
        validate_draft(draft(narrative=narrative), request_payload, model=MODEL)


def test_narrative_inventing_a_subsection_is_rejected(request_payload):
    """Más preciso que la fuente emitida es inventarse un apartado."""
    narrative = GOOD_NARRATIVE.replace("Art. 18.4 LIS", "Art. 18.4.b) LIS")
    with pytest.raises(ExplanationRejected, match="introduce normativa"):
        validate_draft(draft(narrative=narrative), request_payload, model=MODEL)


def test_narrative_citing_a_sibling_article_is_rejected(request_payload):
    """
    El Art. 18.13 LIS (régimen sancionador) existe y es pertinente, pero el
    motor no lo emitió en este análisis. Pertinente no es lo mismo que emitido.
    """
    narrative = GOOD_NARRATIVE + (
        "\n\nEl Art. 18.13 LIS prevé además un régimen sancionador específico."
    )
    with pytest.raises(ExplanationRejected, match="18.13"):
        validate_draft(draft(narrative=narrative), request_payload, model=MODEL)


def test_narrative_citing_case_law_is_rejected(request_payload):
    narrative = GOOD_NARRATIVE + (
        "\n\nEn el mismo sentido se pronunció el TEAC en su resolución RG 7833/2023."
    )
    with pytest.raises(ExplanationRejected, match="introduce normativa"):
        validate_draft(draft(narrative=narrative), request_payload, model=MODEL)


# ---------------------------------------------------------------------------
# Rechazo: formato y extensión
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("narrative", [
    "## Resumen\n\n" + GOOD_NARRATIVE,
    GOOD_NARRATIVE + "\n\n- Primer punto\n- Segundo punto",
    GOOD_NARRATIVE + "\n\n1. Primer punto",
])
def test_markdown_is_rejected(request_payload, narrative):
    with pytest.raises(ExplanationRejected, match="markdown"):
        validate_draft(draft(narrative=narrative), request_payload, model=MODEL)


def test_too_short_is_rejected(request_payload):
    with pytest.raises(ExplanationRejected, match="extensión"):
        validate_draft(draft(narrative="El tipo está fuera de rango."),
                       request_payload, model=MODEL)


def test_too_long_is_rejected(request_payload):
    with pytest.raises(ExplanationRejected, match="extensión"):
        validate_draft(draft(narrative="palabra " * 800), request_payload, model=MODEL)


def test_all_failures_are_reported_together(request_payload):
    """El cliente necesita todos los motivos para poder reintentar una vez."""
    with pytest.raises(ExplanationRejected) as exc:
        validate_draft(
            ExplanationDraft(narrative="Corto.", sources_cited=["inventada"]),
            request_payload, model=MODEL,
        )
    assert len(exc.value.reasons) >= 2


# ---------------------------------------------------------------------------
# Extracción de referencias
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("Según el Art. 18.4 LIS", "art 18.4"),
    ("según el artículo 18.4 de la LIS", "art 18.4"),
    ("el §1.3a AStG dispone", "art 1.3a"),
    ("véase el párr. 6.34", "parr 6.34"),
    ("Cap. III de las Directrices", "cap iii"),
    ("la Ley 27/2014", "ley 27/2014"),
])
def test_reference_extraction_normalises_citation_forms(text, expected):
    assert expected in extract_legal_references(text)


def test_prose_without_references_extracts_nothing():
    assert extract_legal_references(
        "El tipo se sitúa por encima del rango intercuartílico de la muestra."
    ) == set()


def test_allowed_references_come_from_the_emitted_registry(request_payload):
    allowed = allowed_references(request_payload)
    assert "art 18.4" in allowed
    assert "art 1.3a" in allowed
    assert "art 18.13" not in allowed


# ---------------------------------------------------------------------------
# El prompt está versionado y vinculado al código
# ---------------------------------------------------------------------------

def test_prompt_file_matches_the_declared_version():
    """
    Si alguien cambia PROMPT_VERSION sin crear el fichero, los informes
    quedarían citando una versión de prompt que no existe.
    """
    from pathlib import Path

    from ai.schemas import PROMPT_VERSION

    path = Path("ai/prompts") / f"{PROMPT_VERSION}.md"
    assert path.exists(), f"falta el prompt {path}"
    assert "REGLAS INVIOLABLES" in path.read_text(encoding="utf-8")
