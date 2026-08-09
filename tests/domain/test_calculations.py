"""
Tests del motor de rango de plena competencia.

Cada test fija una conducta que las capas de informe PDF y de IA van a
consumir. Si uno se rompe, se rompe el entregable, no solo el cálculo.
"""

import datetime as dt

import pytest

from tests.domain.conftest import REF_DATE, make_comparable, make_transaction
from tp_domain.calculations.arm_length_range import (
    MIN_RECOMMENDED_SAMPLE,
    calculate_arm_length_range,
    calculate_percentiles,
    filter_comparables,
    load_dataset,
)
from tp_domain.models import (
    DefensibilityLevel,
    Industry,
    RangePosition,
    RangeRule,
    RejectionReason,
    RiskCode,
    Severity,
    TPMethod,
)


# ---------------------------------------------------------------------------
# Percentiles
# ---------------------------------------------------------------------------

def test_percentiles_basic():
    r = calculate_percentiles([3, 5, 7, 9, 11])
    assert (r["p25"], r["p50"], r["p75"], r["count"]) == (5, 7, 9, 5)


def test_percentiles_project_spec_example():
    """Ejemplo de las instrucciones del proyecto (§11): 5, 6, 8, 10 -> mediana 7."""
    assert calculate_percentiles([5, 6, 8, 10])["p50"] == 7


def test_percentiles_include_real_p10_and_p90():
    """
    Hasta la v0.1 el tramo intermedio se aproximaba con p25*0,7 y p75*1,3.
    Esos multiplicadores no correspondían a ningún percentil y no había forma
    de explicarlos en un informe.
    """
    r = calculate_percentiles(list(range(1, 101)))
    assert r["p10"] == pytest.approx(10.9, abs=0.05)
    assert r["p90"] == pytest.approx(90.1, abs=0.05)


def test_percentiles_unsorted_input():
    assert calculate_percentiles([11, 3, 9, 5, 7]) == calculate_percentiles([3, 5, 7, 9, 11])


def test_percentiles_empty_list():
    r = calculate_percentiles([])
    assert r == {"p10": None, "p25": None, "p50": None, "p75": None, "p90": None, "count": 0}


def test_percentiles_rounded_to_two_decimals():
    r = calculate_percentiles([2.0, 2.3, 3.1, 4.0, 4.5])
    for key in ("p10", "p25", "p50", "p75", "p90"):
        assert r[key] == round(r[key], 2)


# ---------------------------------------------------------------------------
# Dataset y filtrado
# ---------------------------------------------------------------------------

def test_dataset_loads_with_its_version(dataset):
    assert dataset.version == "1.0"
    assert len(dataset.comparables) == 55


def test_filter_returns_only_matching_industry(comparables):
    accepted, rejected = filter_comparables(make_transaction("software"), comparables)
    assert len(accepted) == 19
    assert len(rejected) == 36
    assert {c.industry for c in accepted} == {Industry.SOFTWARE}


@pytest.mark.parametrize("industry,expected", [
    ("pharmaceutical", 18), ("software", 19), ("manufacturing", 18),
])
def test_filter_counts_per_industry(comparables, industry, expected):
    accepted, _ = filter_comparables(make_transaction(industry), comparables)
    assert len(accepted) == expected


def test_every_rejection_records_a_reason(comparables):
    _, rejected = filter_comparables(make_transaction("software"), comparables)
    assert all(r.reason is RejectionReason.INDUSTRY_MISMATCH for r in rejected)
    assert all(r.detail for r in rejected)


def test_accepted_plus_rejected_equals_the_whole_dataset(comparables):
    """El anexo del informe debe cuadrar: ningún comparable se pierde."""
    accepted, rejected = filter_comparables(make_transaction("software"), comparables)
    assert len(accepted) + len(rejected) == len(comparables)


def test_stale_comparables_are_rejected_with_their_reason():
    old = [make_comparable("old_1", year=2019)]
    accepted, rejected = filter_comparables(make_transaction("software"), old)
    assert accepted == []
    assert rejected[0].reason is RejectionReason.STALE_YEAR


def test_comparable_without_rate_is_rejected_with_its_reason():
    comp = make_comparable("no_rate")
    comp.royalty_rate = None
    accepted, rejected = filter_comparables(make_transaction("software"), [comp])
    assert accepted == []
    assert rejected[0].reason is RejectionReason.NO_RATE_DATA


def test_recent_comparable_is_accepted():
    accepted, _ = filter_comparables(make_transaction("software"), [make_comparable("new_1")])
    assert len(accepted) == 1


# ---------------------------------------------------------------------------
# Resultado completo
# ---------------------------------------------------------------------------

def test_result_is_self_contained(comparables):
    """El PDF y la IA no consultan nada fuera del resultado."""
    r = calculate_arm_length_range(make_transaction("software", 10.0), comparables)
    assert r.analysis_id.startswith("TPIP-")
    assert r.engine_version and r.dataset_version
    assert r.transaction.rate_percent == 10
    assert r.sources and r.conclusion


def test_method_is_cup_with_an_explicit_rationale(comparables):
    """
    Fase 1 documenta el método como CUP-based royalty benchmarking: se compara
    precio contra precio. TNMM queda para la expansión.
    """
    r = calculate_arm_length_range(make_transaction("software", 10.0), comparables)
    assert r.method_applied is TPMethod.CUP
    assert "CUP-based royalty benchmarking" in r.method_rationale
    assert "TNMM no procede" in r.method_rationale


def test_comparables_are_not_truncated(comparables):
    """
    El truncado a 5 de la v0.1 era una decisión de UI dentro del dominio. El
    anexo de un estudio de benchmarking necesita el conjunto completo.
    """
    r = calculate_arm_length_range(make_transaction("software", 10.0), comparables)
    assert len(r.comparables_accepted) == 19
    assert len(r.comparables_rejected) == 36


def test_dataset_is_always_disclosed_as_synthetic(comparables):
    """Callarlo en un portfolio se lee como aparentar datos reales."""
    r = calculate_arm_length_range(make_transaction("software", 10.0), comparables)
    codes = {f.code for f in r.risk_factors}
    assert RiskCode.SYNTHETIC_DATA in codes
    assert "tpip-dataset-v1" in {s.id for s in r.sources}


def test_every_cited_source_id_resolves(comparables):
    """Integridad del registro: ninguna cita huérfana llega al informe."""
    r = calculate_arm_length_range(make_transaction("software", 12.0), comparables)
    emitted = {s.id for s in r.sources}
    for item in list(r.assessments) + list(r.risk_factors):
        assert set(item.source_ids) <= emitted


def test_one_assessment_per_jurisdiction(comparables):
    r = calculate_arm_length_range(make_transaction("software", 10.0), comparables)
    assert [a.country for a in r.assessments] == ["ES", "DE"]


def test_thin_sample_is_flagged():
    comps = [make_comparable(f"c{i}", rate=9.0 + i * 0.1) for i in range(3)]
    r = calculate_arm_length_range(make_transaction("software", 9.1), comps)
    assert any(f.code is RiskCode.THIN_SAMPLE for f in r.risk_factors)
    assert r.benchmark.count_accepted < MIN_RECOMMENDED_SAMPLE


# ---------------------------------------------------------------------------
# Caso de demostración: España -> Alemania, canon de software al 12%
# ---------------------------------------------------------------------------

def test_demo_case_produces_asymmetric_treatment(comparables):
    """
    El caso que vende el proyecto. Si esto se rompe, se rompe la demo.

    Mismo canon, mismos comparables: Alemania ajusta de oficio a la mediana,
    España remite a valoración caso por caso.
    """
    r = calculate_arm_length_range(make_transaction("software", 12.0), comparables)
    es, de = r.assessments

    assert r.benchmark.percentile_25 == 8.35
    assert r.benchmark.percentile_50 == 10.1
    assert r.benchmark.percentile_75 == 11.2

    assert es.position is de.position is RangePosition.ABOVE_P90
    assert es.range_rule is RangeRule.NO_STATUTORY_RULE
    assert de.range_rule is RangeRule.INTERQUARTILE_MEDIAN_ADJUSTMENT
    assert es.adjusted_rate is None
    assert de.adjusted_rate == 10.1

    assert any(
        f.code is RiskCode.MANDATORY_ADJUSTMENT and f.severity is Severity.CRITICAL
        for f in r.risk_factors
    )
    assert "asimétrico" in r.conclusion


@pytest.mark.parametrize("industry,rate,p25,p75", [
    ("software", 10.0, 8.35, 11.2),
    ("manufacturing", 3.0, 2.23, 4.0),
    ("pharmaceutical", 6.0, 4.62, 6.45),
])
def test_in_range_cases_are_strong_in_both_jurisdictions(comparables, industry, rate, p25, p75):
    r = calculate_arm_length_range(make_transaction(industry, rate), comparables)
    assert (r.benchmark.percentile_25, r.benchmark.percentile_75) == (p25, p75)
    assert all(a.defensibility_level is DefensibilityLevel.STRONG for a in r.assessments)
    assert all(a.adjusted_rate is None for a in r.assessments)


def test_industry_filter_actually_changes_the_verdict(comparables):
    """
    Regresión de la Fase 1b: sin filtro de industria el rango mezcla
    manufacturing (2-5%) con software (6-14%) y el veredicto cambia.
    """
    r = calculate_arm_length_range(make_transaction("software", 10.0), comparables)
    todos = calculate_percentiles([c.royalty_rate for c in comparables])

    assert all(a.defensibility_level is DefensibilityLevel.STRONG for a in r.assessments)
    assert not (todos["p25"] <= 10.0 <= todos["p75"])


# ---------------------------------------------------------------------------
# Casos borde
# ---------------------------------------------------------------------------

def test_no_comparables_returns_a_clean_result_not_an_exception():
    r = calculate_arm_length_range(make_transaction("software", 10.0), [])
    assert r.benchmark.percentile_25 is None
    assert r.benchmark.count_accepted == 0
    assert r.assessments == []
    assert any(f.code is RiskCode.NO_COMPARABLES for f in r.risk_factors)
    assert "Sin comparables" in r.conclusion


def test_unmodelled_recipient_is_flagged(comparables):
    r = calculate_arm_length_range(
        make_transaction("software", 10.0, recipient="LU"), comparables
    )
    assert any(f.code is RiskCode.JURISDICTION_NOT_MODELLED for f in r.risk_factors)


def test_analysis_is_deterministic_for_a_fixed_date(comparables):
    """Sin `datetime.now()` en el filtro: dos ejecuciones dan el mismo rango."""
    t = make_transaction("software", 10.0, effective_date=dt.date(2026, 6, 30))
    a = calculate_arm_length_range(t, comparables)
    b = calculate_arm_length_range(t, comparables)
    assert a.benchmark == b.benchmark
    assert a.conclusion == b.conclusion
