"""
Tests de la capa de reglas jurisdiccionales.

Lo que se fija aquí es la asimetría que sostiene el producto: el mismo tipo,
sobre el mismo rango, produce consecuencias distintas en España y Alemania.
"""

import pytest

from tp_domain.models import (
    BenchmarkRange,
    DefensibilityLevel,
    PartyRole,
    RangePosition,
    RangeRule,
)
from tp_domain.rules.statistical_rules import (
    JURISDICTION_RANGE_RULES,
    POSITION_SCORING,
    assess,
    classify_position,
    rule_for,
)

# Rango de software del dataset v1.
BENCH = BenchmarkRange(
    percentile_10=6.88, percentile_25=8.35, percentile_50=10.1,
    percentile_75=11.2, percentile_90=11.9, count_accepted=19,
)


# ---------------------------------------------------------------------------
# Mapa de jurisdicciones
# ---------------------------------------------------------------------------

def test_spain_has_no_statutory_statistical_rule():
    """Art. 18.4 LIS: la regla española es la ausencia de regla."""
    assert rule_for("ES") is RangeRule.NO_STATUTORY_RULE


def test_germany_imposes_median_adjustment():
    """§1.3a AStG."""
    assert rule_for("DE") is RangeRule.INTERQUARTILE_MEDIAN_ADJUSTMENT


def test_unmodelled_jurisdiction_is_not_assumed_to_follow_spain():
    """
    No se presume la regla de ningún Estado no estudiado. Decir 'no lo sé' es
    correcto; inventar Derecho comparado, no.
    """
    assert rule_for("LU") is RangeRule.NOT_MODELLED
    assert rule_for("XX") is RangeRule.NOT_MODELLED


def test_rule_lookup_is_case_insensitive():
    assert rule_for("de") is rule_for("DE")


def test_only_studied_jurisdictions_are_mapped():
    assert set(JURISDICTION_RANGE_RULES) == {"ES", "DE"}


# ---------------------------------------------------------------------------
# Posición en el rango
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("rate,expected", [
    (5.0, RangePosition.BELOW_P10),
    (7.5, RangePosition.P10_TO_P25),
    (10.0, RangePosition.WITHIN_IQR),
    (11.5, RangePosition.P75_TO_P90),
    (12.0, RangePosition.ABOVE_P90),
])
def test_position_classification(rate, expected):
    assert classify_position(rate, BENCH) is expected


@pytest.mark.parametrize("rate", [8.35, 11.2])
def test_iqr_boundaries_are_inclusive(rate):
    assert classify_position(rate, BENCH) is RangePosition.WITHIN_IQR


@pytest.mark.parametrize("rate", [6.88, 11.9])
def test_p10_and_p90_boundaries_stay_inside_the_moderate_band(rate):
    assert classify_position(rate, BENCH) in {
        RangePosition.P10_TO_P25, RangePosition.P75_TO_P90,
    }


# ---------------------------------------------------------------------------
# Puntuación
# ---------------------------------------------------------------------------

def test_scoring_table_covers_every_position():
    assert set(POSITION_SCORING) == set(RangePosition)


@pytest.mark.parametrize("position,level,score", [
    (RangePosition.WITHIN_IQR, DefensibilityLevel.STRONG, 9),
    (RangePosition.P10_TO_P25, DefensibilityLevel.MODERATE, 6),
    (RangePosition.P75_TO_P90, DefensibilityLevel.MODERATE, 6),
    (RangePosition.BELOW_P10, DefensibilityLevel.WEAK, 2),
    (RangePosition.ABOVE_P90, DefensibilityLevel.WEAK, 2),
])
def test_score_is_derived_from_position(position, level, score):
    assert POSITION_SCORING[position] == (level, score)


# ---------------------------------------------------------------------------
# Veredicto completo
# ---------------------------------------------------------------------------

def test_germany_adjusts_to_median_when_rate_is_outside_the_range():
    a = assess("DE", PartyRole.RECIPIENT, 12.0, BENCH)
    assert a.adjusted_rate == BENCH.percentile_50 == 10.1
    assert "mediana" in a.consequence
    assert "de-astg-1-3a" in a.source_ids


def test_germany_does_not_adjust_when_rate_is_inside_the_range():
    a = assess("DE", PartyRole.RECIPIENT, 10.0, BENCH)
    assert a.adjusted_rate is None
    assert a.defensibility_level is DefensibilityLevel.STRONG


def test_spain_never_adjusts_automatically():
    """Aunque el tipo esté fuera de rango: el Art. 18.4 LIS no lo impone."""
    a = assess("ES", PartyRole.PAYER, 12.0, BENCH)
    assert a.adjusted_rate is None
    assert "no impone ajuste automático" in a.consequence
    assert "es-lis-art18-4" in a.source_ids


def test_same_rate_same_range_different_consequence():
    """La asimetría que justifica el producto entero."""
    es = assess("ES", PartyRole.PAYER, 12.0, BENCH)
    de = assess("DE", PartyRole.RECIPIENT, 12.0, BENCH)

    assert es.position == de.position          # el rango es un hecho de mercado
    assert es.defensibility_score == de.defensibility_score
    assert es.adjusted_rate is None            # la consecuencia, no
    assert de.adjusted_rate == 10.1
    assert es.consequence != de.consequence


def test_unmodelled_jurisdiction_says_so_and_does_not_adjust():
    a = assess("LU", PartyRole.RECIPIENT, 12.0, BENCH)
    assert a.range_rule is RangeRule.NOT_MODELLED
    assert a.adjusted_rate is None
    assert "no modelada" in a.consequence


def test_assessment_always_cites_at_least_one_source():
    for country in ("ES", "DE", "LU"):
        assert assess(country, PartyRole.PAYER, 12.0, BENCH).source_ids
