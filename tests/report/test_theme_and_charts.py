"""
Tests del lenguaje visual compartido.

Solo se fija lo que tiene comportamiento: la geometría del rango y lo que el
gráfico dibuja. La estética no se prueba — se mira.

El punto que sí importa comprobar es la coherencia: pantalla e informe deben
partir de la misma geometría y de las mismas etiquetas, porque en cuanto
divergen dejan de parecer el mismo producto.
"""

import pytest

from infrastructure.charts import benchmark_range_svg
from infrastructure.theme import (
    POSITION_LABEL,
    REJECTION_LABEL,
    ROLE_LABEL,
    RULE_LABEL,
    range_geometry,
)
from tests.domain.conftest import make_transaction
from tp_domain.calculations.arm_length_range import calculate_arm_length_range
from tp_domain.models import (
    BenchmarkRange,
    PartyRole,
    RangePosition,
    RangeRule,
    RejectionReason,
)

BENCH = BenchmarkRange(
    percentile_10=6.88, percentile_25=8.35, percentile_50=10.1,
    percentile_75=11.2, percentile_90=11.9, count_accepted=19,
)


# ---------------------------------------------------------------------------
# Geometría
# ---------------------------------------------------------------------------

def test_percentiles_keep_their_order():
    g = range_geometry(BENCH, 10.0)
    assert g["p10"] < g["p25"] < g["p50"] < g["p75"] < g["p90"]


def test_everything_stays_inside_the_canvas():
    for rate in (1.0, 6.88, 10.0, 11.9, 40.0):
        g = range_geometry(BENCH, rate)
        assert all(0.0 <= g[k] <= 1.0 for k in ("p10", "p25", "p50", "p75", "p90", "rate"))


def test_rate_inside_the_iqr_lands_between_p25_and_p75():
    g = range_geometry(BENCH, 10.0)
    assert g["p25"] < g["rate"] < g["p75"]


def test_rate_above_p90_lands_to_the_right_of_p90():
    g = range_geometry(BENCH, 12.0)
    assert g["rate"] > g["p90"]


def test_scale_stretches_to_contain_a_distant_rate():
    """
    Un tipo muy alejado no se recorta contra el borde: se amplía la escala. Si
    se recortara, se ocultaría justo lo que hay que ver.
    """
    g = range_geometry(BENCH, 40.0)
    assert g["scale_max"] > 40.0
    assert g["rate"] < 1.0


def test_no_geometry_without_a_range():
    assert range_geometry(BenchmarkRange(count_accepted=0), 10.0) is None


# ---------------------------------------------------------------------------
# Gráfico
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def outside_result(comparables):
    return calculate_arm_length_range(make_transaction("software", 12.0), comparables)


@pytest.fixture(scope="module")
def inside_result(comparables):
    return calculate_arm_length_range(make_transaction("software", 10.0), comparables)


def test_chart_shows_every_percentile(outside_result):
    svg = benchmark_range_svg(outside_result)
    for label in ("P10", "P25", "Mediana", "P75", "P90"):
        assert f">{label}<" in svg
    for value in (6.88, 8.35, 10.1, 11.2, 11.9):
        assert f"{value}%" in svg


def test_chart_marks_the_tested_rate(outside_result):
    assert "Tipo analizado 12.0%" in benchmark_range_svg(outside_result)


def test_chart_states_the_sample_size(outside_result):
    assert "19 comparables" in benchmark_range_svg(outside_result)


def test_marker_colour_signals_inside_or_outside(inside_result, outside_result):
    """
    La lectura de dos segundos: verde dentro del rango intercuartílico, rojo
    fuera. El color confirma lo que ya dice la posición del marcador.
    """
    from infrastructure.theme import COLORS

    assert COLORS["ok"] in benchmark_range_svg(inside_result)
    assert COLORS["risk"] in benchmark_range_svg(outside_result)
    assert COLORS["risk"] not in benchmark_range_svg(inside_result)


def test_chart_is_valid_xml(outside_result):
    from xml.etree import ElementTree

    ElementTree.fromstring(benchmark_range_svg(outside_result))


def test_no_chart_without_comparables():
    result = calculate_arm_length_range(make_transaction("software", 10.0), [])
    assert benchmark_range_svg(result) is None


# ---------------------------------------------------------------------------
# Etiquetas: ni la pantalla ni el informe muestran valores crudos de enum
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("mapping,enum", [
    (POSITION_LABEL, RangePosition),
    (REJECTION_LABEL, RejectionReason),
    (ROLE_LABEL, PartyRole),
    (RULE_LABEL, RangeRule),
])
def test_every_enum_value_has_a_human_label(mapping, enum):
    assert set(mapping) == set(enum)
    for member, label in mapping.items():
        assert member.value not in label, f"{member} se muestra en crudo"
