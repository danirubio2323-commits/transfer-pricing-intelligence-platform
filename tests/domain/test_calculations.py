"""
Domain tests for the arm's length range engine.

Safety net before Phase 2A (jurisdiction rules). Every test here pins a
behaviour that the jurisdiction layer must not silently break.

Dates are hardcoded (never datetime.now()) so the suite does not start
failing on 1 January of any future year.
"""

import datetime as dt

import pytest

from tp_domain.models import (
    Transaction, Comparable, DefensibilityLevel, TPMethod,
)
from tp_domain.calculations.arm_length_range import (
    load_comparables,
    filter_comparables,
    calculate_percentiles,
    calculate_defensibility_score,
    calculate_arm_length_range,
)

# Fecha fija de referencia para todas las transacciones de test.
# El filtro de año conserva comparables con data_year >= 2024.
REF_DATE = dt.date(2026, 1, 1)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def comparables():
    return load_comparables()


def make_transaction(industry: str, rate: float, ttype: str = "royalty",
                     effective_date: dt.date = REF_DATE) -> Transaction:
    return Transaction(
        description="Test transaction",
        from_country="ES",
        to_country="LU",
        transaction_type=ttype,
        industry=industry,
        amount_eur=1_000_000,
        rate_percent=rate,
        effective_date=effective_date,
    )


def make_comparable(cid: str, industry: str, rate: float,
                    year: int = 2025, country: str = "DE") -> Comparable:
    return Comparable(
        id=cid,
        company_name=f"Test {cid}",
        country=country,
        industry=industry,
        royalty_rate=rate,
        gross_margin=50.0,
        operating_margin=15.0,
        data_year=year,
        source="unit-test",
    )


# ---------------------------------------------------------------------------
# Test 1: Percentile calculation
# ---------------------------------------------------------------------------

def test_percentiles_basic():
    """Input [3, 5, 7, 9, 11] -> P25=5, P50=7, P75=9."""
    result = calculate_percentiles([3, 5, 7, 9, 11])
    assert result["p25"] == 5
    assert result["p50"] == 7
    assert result["p75"] == 9
    assert result["count"] == 5


def test_percentiles_project_spec_example():
    """Ejemplo de las instrucciones del proyecto (§11): 5, 6, 8, 10 -> mediana 7."""
    assert calculate_percentiles([5, 6, 8, 10])["p50"] == 7


def test_percentiles_unsorted_input():
    """El orden de entrada no debe alterar el resultado."""
    assert calculate_percentiles([11, 3, 9, 5, 7]) == calculate_percentiles([3, 5, 7, 9, 11])


def test_percentiles_empty_list():
    """Lista vacía -> None en los tres percentiles, count 0. No debe lanzar."""
    result = calculate_percentiles([])
    assert result == {"p25": None, "p50": None, "p75": None, "count": 0}


def test_percentiles_rounded_to_two_decimals():
    """Sin redondeo esto daría 2.2249999999999996. Evita artefactos de float en la UI."""
    result = calculate_percentiles([2.0, 2.3, 3.1, 4.0, 4.5])
    for key in ("p25", "p50", "p75"):
        assert result[key] == round(result[key], 2)


# ---------------------------------------------------------------------------
# Test 2: Industry filtering
# ---------------------------------------------------------------------------

def test_dataset_loads():
    """El dataset se carga ignorando el bloque _metadata."""
    comps = load_comparables()
    assert len(comps) == 55
    assert all(isinstance(c, Comparable) for c in comps)


def test_filter_returns_only_matching_industry(comparables):
    """Software -> devuelve los 19 de software, descarta los otros 36."""
    transaction = make_transaction("software", 10.0)
    filtered = filter_comparables(transaction, comparables)

    assert len(filtered) == 19
    assert len(comparables) - len(filtered) == 36
    assert {c.industry for c in filtered} == {"software"}


@pytest.mark.parametrize("industry,expected", [
    ("pharmaceutical", 18),
    ("software", 19),
    ("manufacturing", 18),
])
def test_filter_counts_per_industry(comparables, industry, expected):
    assert len(filter_comparables(make_transaction(industry, 5.0), comparables)) == expected


def test_filter_unknown_industry_returns_empty(comparables):
    """Una industria fuera del dataset no debe colarse en el rango."""
    assert filter_comparables(make_transaction("biotech", 5.0), comparables) == []


def test_filter_drops_stale_years(comparables):
    """El filtro conserva data_year >= effective_date.year - 2."""
    old = [make_comparable("old_1", "software", 9.0, year=2019)]
    recent = [make_comparable("new_1", "software", 9.0, year=2025)]
    transaction = make_transaction("software", 10.0)

    assert filter_comparables(transaction, old) == []
    assert len(filter_comparables(transaction, recent)) == 1


def test_filter_skips_comparables_without_royalty_rate():
    """Para royalties, un comparable sin royalty_rate no aporta y debe descartarse."""
    comp = make_comparable("no_rate", "software", 9.0)
    comp.royalty_rate = None
    assert filter_comparables(make_transaction("software", 10.0), [comp]) == []


# ---------------------------------------------------------------------------
# Test 3: Defensibility scoring
# ---------------------------------------------------------------------------

def test_score_within_range_is_strong():
    """rate=10%, P25=8.35, P75=11.2 -> score 9."""
    assert calculate_defensibility_score(10.0, 8.35, 10.1, 11.2) == 9


def test_score_far_below_range_is_weak():
    assert calculate_defensibility_score(1.0, 8.35, 10.1, 11.2) == 2


def test_score_far_above_range_is_weak():
    assert calculate_defensibility_score(25.0, 8.35, 10.1, 11.2) == 2


def test_score_just_outside_range_is_moderate():
    """Zona P10-P90 aproximada (P25*0.7 a P75*1.3)."""
    assert calculate_defensibility_score(12.0, 8.35, 10.1, 11.2) == 6
    assert calculate_defensibility_score(7.0, 8.35, 10.1, 11.2) == 6


def test_score_at_range_boundaries_is_strong():
    """Los límites P25 y P75 son inclusivos."""
    assert calculate_defensibility_score(8.35, 8.35, 10.1, 11.2) == 9
    assert calculate_defensibility_score(11.2, 8.35, 10.1, 11.2) == 9


def test_low_rate_conclusion_says_below():
    result = calculate_arm_length_range(make_transaction("software", 1.0))
    assert result.defensibility_level == DefensibilityLevel.WEAK
    assert result.defensibility_score == 2
    assert "BELOW" in result.conclusion
    assert "EXCEEDS" not in result.conclusion


def test_high_rate_conclusion_says_exceeds():
    result = calculate_arm_length_range(make_transaction("software", 25.0))
    assert result.defensibility_level == DefensibilityLevel.WEAK
    assert result.defensibility_score == 2
    assert "EXCEEDS" in result.conclusion
    assert "BELOW" not in result.conclusion


def test_low_rate_flagged_as_below_p25():
    result = calculate_arm_length_range(make_transaction("software", 1.0))
    assert any("below P25" in factor for factor in result.risk_factors)


def test_thin_sample_is_flagged():
    """Menos de 5 comparables debe avisar, aunque el rate caiga dentro."""
    comps = [make_comparable(f"c{i}", "software", 9.0 + i * 0.1) for i in range(3)]
    result = calculate_arm_length_range(make_transaction("software", 9.1), comps)
    assert any("minimum 5 recommended" in factor for factor in result.risk_factors)


# ---------------------------------------------------------------------------
# Test 4: Edge cases
# ---------------------------------------------------------------------------

def test_no_comparables_returns_none_not_exception():
    """La rama sin datos debe devolver None limpiamente, no lanzar ValidationError."""
    result = calculate_arm_length_range(make_transaction("biotech", 5.0))

    assert result.benchmark_range.percentile_25 is None
    assert result.benchmark_range.percentile_50 is None
    assert result.benchmark_range.percentile_75 is None
    assert result.benchmark_range.count_comparables == 0
    assert result.defensibility_score is None
    assert result.defensibility_level == DefensibilityLevel.WEAK
    assert result.comparables_used == []
    assert "Insufficient data" in result.conclusion


def test_empty_comparables_list_returns_none():
    result = calculate_arm_length_range(make_transaction("software", 10.0), [])
    assert result.benchmark_range.percentile_25 is None
    assert result.defensibility_score is None


def test_comparables_used_capped_at_five(comparables):
    """La UI muestra como mucho 5 comparables."""
    result = calculate_arm_length_range(make_transaction("software", 10.0), comparables)
    assert len(result.comparables_used) <= 5


def test_non_royalty_uses_operating_margin(comparables):
    """management_fee no usa royalty_rate, usa operating_margin."""
    result = calculate_arm_length_range(
        make_transaction("software", 20.0, ttype="management_fee"), comparables
    )
    margins = [c.operating_margin for c in comparables if c.industry == "software"]
    expected = calculate_percentiles(margins)
    assert result.benchmark_range.percentile_50 == expected["p50"]


def test_method_recommended_is_cup(comparables):
    """Hoy el motor siempre propone CUP. Fijado para detectar cambios no intencionados."""
    result = calculate_arm_length_range(make_transaction("software", 10.0), comparables)
    assert result.method_recommended == TPMethod.CUP


def test_proposed_rate_is_echoed_back(comparables):
    result = calculate_arm_length_range(make_transaction("software", 10.0), comparables)
    assert result.proposed_rate == 10.0


def test_transaction_rejects_invalid_input():
    """Los validadores de Pydantic siguen activos."""
    with pytest.raises(ValueError):
        make_transaction("software", 150.0)   # rate > 100
    with pytest.raises(ValueError):
        Transaction(
            description="x", from_country="ES", to_country="LU",
            transaction_type="royalty", industry="software",
            amount_eur=0, rate_percent=10.0, effective_date=REF_DATE,
        )


# ---------------------------------------------------------------------------
# Test 5: Real 3-case validation (los casos de la demo)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("industry,rate,p25,p75", [
    ("software",       10.0, 8.35, 11.2),
    ("manufacturing",   3.0, 2.23, 4.0),
    ("pharmaceutical",  6.0, 4.62, 6.45),
])
def test_demo_cases_are_strong(comparables, industry, rate, p25, p75):
    """Los 3 escenarios de la demo. Si uno se rompe, la demo se rompe."""
    result = calculate_arm_length_range(make_transaction(industry, rate), comparables)

    assert result.benchmark_range.percentile_25 == p25
    assert result.benchmark_range.percentile_75 == p75
    assert result.defensibility_score == 9
    assert result.defensibility_level == DefensibilityLevel.STRONG
    assert "DEFENSIBLE" in result.conclusion
    assert result.risk_factors == []


def test_industry_filter_actually_changes_the_verdict(comparables):
    """
    Regresión del bug de Fase 1b: sin filtro de industria el rango mezcla
    manufacturing (2-5%) con software (6-14%) y da un veredicto distinto.
    """
    transaction = make_transaction("software", 10.0)

    con_filtro = calculate_arm_length_range(transaction, comparables)
    todos = calculate_percentiles([c.royalty_rate for c in comparables])

    assert con_filtro.defensibility_level == DefensibilityLevel.STRONG
    assert not (todos["p25"] <= 10.0 <= todos["p75"]), (
        "Mezclando industrias, un 10% caería fuera del rango: por eso el filtro es obligatorio"
    )
