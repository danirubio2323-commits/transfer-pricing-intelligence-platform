"""
Tests del informe PDF.

No se comprueba el aspecto: se comprueba que el documento contiene la
información que un informe de precios de transferencia debe contener y que se
genera íntegro sin llamar a ninguna API.

El texto se extrae del PDF ya construido, no de las estructuras de datos: lo
que importa es lo que un revisor va a leer en el papel.
"""

import datetime as dt
from decimal import Decimal

import pytest
from pypdf import PdfReader

from tests.domain.conftest import REF_DATE, make_transaction
from tp_domain.calculations.arm_length_range import calculate_arm_length_range
from tp_domain.models import AIExplanation, Comparable, Industry
from infrastructure.report.pdf_report import build_report, render_report_bytes


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def result(comparables):
    """Caso de demostración: canon de software al 12%, España -> Alemania."""
    return calculate_arm_length_range(make_transaction("software", 12.0), comparables)


@pytest.fixture(scope="module")
def result_with_ai(result):
    return result.model_copy(update={"ai_explanation": AIExplanation(
        text=(
            "El canon propuesto supera el percentil 90 de la muestra sectorial. "
            "La consecuencia difiere por jurisdicción."
        ),
        prompt_version="explain_analysis_v1",
        model="claude-test",
        sources_cited=["de-astg-1-3a", "es-lis-art18-4"],
    )})


def _text(result) -> str:
    import io
    reader = PdfReader(io.BytesIO(render_report_bytes(result)))
    return "\n".join(page.extract_text() for page in reader.pages)


# ---------------------------------------------------------------------------
# Generación
# ---------------------------------------------------------------------------

def test_report_is_generated_without_any_api_call(result):
    """
    El informe no depende de la capa de IA. Sin clave, sin red, sale completo.
    """
    assert result.ai_explanation is None
    assert render_report_bytes(result).startswith(b"%PDF")


def test_report_writes_to_disk(result, tmp_path):
    path = build_report(result, tmp_path / "informe.pdf")
    assert path.exists() and path.stat().st_size > 5_000


def test_report_has_all_sections(result):
    text = _text(result)
    for heading in (
        "Resumen ejecutivo",
        "Análisis de benchmark",
        "Fundamento y consecuencias por jurisdicción",
        "Análisis asistido por inteligencia artificial",
        "Anexo",
    ):
        assert heading in text, f"falta la sección: {heading}"


# ---------------------------------------------------------------------------
# 1. Portada
# ---------------------------------------------------------------------------

def test_cover_identifies_the_analysis_and_its_versions(result):
    text = _text(result)
    assert "TPIP" in text
    assert result.analysis_id in text
    assert result.engine_version in text
    assert result.dataset_version in text


def test_cover_discloses_the_synthetic_dataset(result):
    """
    Callar el origen de los comparables en un portfolio se lee como aparentar
    datos reales. El disclaimer va en portada, no en una nota al pie.
    """
    text = _text(result)
    assert "DATOS SINTÉTICOS" in text
    assert "Orbis" in text  # la advertencia nombra las bases que NO se usan


def test_every_page_carries_the_synthetic_data_footer(result):
    import io
    reader = PdfReader(io.BytesIO(render_report_bytes(result)))
    for page in reader.pages:
        assert "Datos sintéticos" in page.extract_text()


# ---------------------------------------------------------------------------
# 2. Resumen ejecutivo
# ---------------------------------------------------------------------------

def test_executive_summary_states_the_range_and_the_position(result):
    text = _text(result)
    assert f"{result.benchmark.percentile_25}%" in text
    assert f"{result.benchmark.percentile_75}%" in text
    assert "Por encima del P90" in text


def test_executive_summary_shows_both_jurisdictions(result):
    text = _text(result)
    assert "Pagadora" in text and "Perceptora" in text
    for assessment in result.assessments:
        assert assessment.country in text


def test_executive_summary_shows_the_german_adjustment(result):
    """El ajuste de oficio a la mediana es la conclusión que vende la demo."""
    text = _text(result)
    assert "10.1%" in text
    assert "No automático" in text  # España, en la misma tabla


# ---------------------------------------------------------------------------
# 3. Benchmark
# ---------------------------------------------------------------------------

def test_benchmark_section_documents_the_methodology(result):
    text = _text(result)
    assert result.benchmark.percentile_method in text
    assert "CUP" in text
    assert str(result.benchmark.count_accepted) in text


def test_benchmark_section_lists_the_risk_factors(result):
    text = _text(result)
    assert "Crítico" in text  # el ajuste obligatorio alemán
    for factor in result.risk_factors:
        assert factor.message[:40] in text


# ---------------------------------------------------------------------------
# 4. Fundamento y fuentes
# ---------------------------------------------------------------------------

def test_sources_section_lists_every_emitted_source(result):
    text = _text(result)
    for source in result.sources:
        assert source.citation in text


def test_legal_basis_is_stated_per_jurisdiction(result):
    text = _text(result)
    assert "Art. 18.4" in text
    assert "1.3a" in text
    assert "Sin regla estadística legal" in text
    assert "ajuste obligatorio a la mediana" in text


# ---------------------------------------------------------------------------
# 5. Sección IA
# ---------------------------------------------------------------------------

def test_ai_section_declares_absence_instead_of_leaving_a_gap(result):
    text = _text(result)
    assert "sin asistencia de IA" in text
    assert "no afecta a la validez" in text


def test_ai_section_renders_the_explanation_and_its_traceability(result_with_ai):
    text = _text(result_with_ai)
    assert "supera el percentil 90" in text
    assert "explain_analysis_v1" in text
    assert "claude-test" in text


def test_ai_section_lists_only_sources_emitted_by_the_engine(result_with_ai):
    text = _text(result_with_ai)
    assert "Außensteuergesetz" in text
    assert "la validación es estructural" in text


# ---------------------------------------------------------------------------
# 6. Anexo de comparables
# ---------------------------------------------------------------------------

def test_annex_lists_every_accepted_comparable(result):
    """Sin el conjunto completo no hay estudio de benchmarking que contrastar."""
    text = _text(result)
    assert len(result.comparables_accepted) == 19
    for comparable in result.comparables_accepted:
        assert comparable.company_name in text


def test_annex_lists_rejected_comparables_with_their_reason(result):
    text = _text(result)
    assert len(result.comparables_rejected) == 36
    assert "Sector no coincidente" in text
    for rejected in result.comparables_rejected[:5]:
        assert rejected.company_name in text


def test_annex_does_not_hide_the_filter(result):
    text = _text(result)
    assert f"Comparables aceptados ({len(result.comparables_accepted)})" in text
    assert f"Comparables rechazados ({len(result.comparables_rejected)})" in text


# ---------------------------------------------------------------------------
# Robustez
# ---------------------------------------------------------------------------

def test_xml_hostile_text_survives_intact():
    """
    ReportLab interpreta marcado XML dentro de un Paragraph: un '&' en el
    nombre de una compañía rompería la maquetación si no se escapara.
    """
    comps = [
        Comparable(
            id=f"c{i}",
            company_name="Smith & Wesson <Holdings> SL" if i == 0 else f"Comparable {i}",
            country="DE", industry=Industry.SOFTWARE,
            royalty_rate=8.0 + i * 0.4, data_year=2025, source="unit-test",
        )
        for i in range(8)
    ]
    transaction = make_transaction("software", 9.5).model_copy(
        update={"description": "Canon & licencia <tecnología>"}
    )
    text = _text(calculate_arm_length_range(transaction, comps))

    assert "Smith & Wesson <Holdings> SL" in text
    assert "Canon & licencia <tecnología>" in text
    assert "&amp;" not in text


def test_report_without_comparables_still_builds():
    """La rama sin datos no puede dejar el informe a medias ni reventar."""
    result = calculate_arm_length_range(make_transaction("software", 10.0), [])
    text = _text(result)
    assert "Resumen ejecutivo" in text
    assert "no permite construir un rango" in text


def test_report_is_multi_page(result):
    import io
    reader = PdfReader(io.BytesIO(render_report_bytes(result)))
    assert len(reader.pages) >= 5
