"""
Gráfico del rango de plena competencia para la interfaz, en SVG.

Sin dependencia de Streamlit a propósito: así se puede probar sin levantar la
aplicación. La interfaz se limita a incrustar la cadena que devuelve.

Comparte geometría y paleta con el gráfico del informe (`infrastructure.theme`),
de modo que pantalla y PDF representan el mismo rango con las mismas
proporciones. Si divergen, es un fallo.
"""

from __future__ import annotations

from typing import Optional
from xml.sax.saxutils import escape

from infrastructure.theme import COLORS, range_geometry
from tp_domain.models import AnalysisResult, RangePosition

# Lienzo lógico. El SVG se escala al ancho disponible; las proporciones se
# mantienen.
_WIDTH = 1000.0
_HEIGHT = 210.0
_LEFT = 56.0
_RIGHT = _WIDTH - 56.0
_BAND_TOP = 96.0
_BAND_HEIGHT = 46.0


def benchmark_range_svg(result: AnalysisResult) -> Optional[str]:
    """
    Banda P10-P90, rango intercuartílico destacado, mediana y tipo analizado.

    Devuelve `None` si no hay rango que dibujar.

    El objetivo de lectura es de dos segundos: el marcador cae dentro de la
    banda oscura o fuera de ella, y su color lo confirma.
    """
    benchmark = result.benchmark
    rate = float(result.transaction.rate_percent)
    geometry = range_geometry(benchmark, rate)
    if geometry is None:
        return None

    def x(key: str) -> float:
        return _LEFT + geometry[key] * (_RIGHT - _LEFT)

    position = result.assessments[0].position if result.assessments else None
    inside = position is RangePosition.WITHIN_IQR
    marker_color = COLORS["ok"] if inside else COLORS["risk"]
    band_bottom = _BAND_TOP + _BAND_HEIGHT

    parts = [
        f'<svg viewBox="0 0 {_WIDTH:.0f} {_HEIGHT:.0f}" width="100%" '
        f'role="img" aria-label="Rango de plena competencia" '
        f'xmlns="http://www.w3.org/2000/svg" '
        f'style="font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif">',

        # El <title> es lo que anuncia un lector de pantalla. Dice en texto lo
        # mismo que el gráfico muestra: sin él, la imagen es un hueco mudo.
        f'<title>Rango de plena competencia: P10 {benchmark.percentile_10}%, '
        f'mediana {benchmark.percentile_50}%, P90 {benchmark.percentile_90}%. '
        f'El tipo analizado, {rate}%, queda '
        f'{"dentro" if inside else "fuera"} del rango intercuartílico.</title>',

        # Banda P10-P90
        f'<rect x="{x("p10"):.1f}" y="{_BAND_TOP}" '
        f'width="{x("p90") - x("p10"):.1f}" height="{_BAND_HEIGHT}" '
        f'fill="{COLORS["band_outer"]}"/>',

        # Rango intercuartílico
        f'<rect x="{x("p25"):.1f}" y="{_BAND_TOP}" '
        f'width="{x("p75") - x("p25"):.1f}" height="{_BAND_HEIGHT}" '
        f'fill="{COLORS["band_inner"]}"/>',

        # Mediana
        f'<line x1="{x("p50"):.1f}" y1="{_BAND_TOP - 6}" '
        f'x2="{x("p50"):.1f}" y2="{band_bottom + 6}" '
        f'stroke="{COLORS["median"]}" stroke-width="2.5"/>',

        # Eje
        f'<line x1="{_LEFT}" y1="{band_bottom + 12}" '
        f'x2="{_RIGHT}" y2="{band_bottom + 12}" '
        f'stroke="{COLORS["rule"]}" stroke-width="1"/>',
    ]

    ticks = (
        ("p10", benchmark.percentile_10, "P10"),
        ("p25", benchmark.percentile_25, "P25"),
        ("p50", benchmark.percentile_50, "Mediana"),
        ("p75", benchmark.percentile_75, "P75"),
        ("p90", benchmark.percentile_90, "P90"),
    )
    for key, value, label in ticks:
        pos = x(key)
        parts.append(
            f'<line x1="{pos:.1f}" y1="{band_bottom + 12}" '
            f'x2="{pos:.1f}" y2="{band_bottom + 20}" '
            f'stroke="{COLORS["rule"]}" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{pos:.1f}" y="{band_bottom + 38}" text-anchor="middle" '
            f'font-size="15" fill="{COLORS["muted"]}">{escape(label)}</text>'
        )
        parts.append(
            f'<text x="{pos:.1f}" y="{band_bottom + 58}" text-anchor="middle" '
            f'font-size="17" font-weight="600" fill="{COLORS["ink"]}">'
            f'{value}%</text>'
        )

    # Tipo analizado: etiqueta, triángulo y línea de plomada hasta la banda.
    marker_x = x("rate")
    parts += [
        f'<line x1="{marker_x:.1f}" y1="{_BAND_TOP - 4}" '
        f'x2="{marker_x:.1f}" y2="{band_bottom}" '
        f'stroke="{marker_color}" stroke-width="2.5"/>',

        f'<polygon points="{marker_x:.1f},{_BAND_TOP - 6} '
        f'{marker_x - 9:.1f},{_BAND_TOP - 24} {marker_x + 9:.1f},{_BAND_TOP - 24}" '
        f'fill="{marker_color}"/>',

        f'<text x="{marker_x:.1f}" y="{_BAND_TOP - 34}" text-anchor="middle" '
        f'font-size="20" font-weight="700" fill="{marker_color}">'
        f'Tipo analizado {rate}%</text>',

        f'<text x="{_LEFT}" y="26" font-size="15" fill="{COLORS["muted"]}">'
        f'Rango de plena competencia — {benchmark.count_accepted} comparables '
        f'aceptados</text>',

        "</svg>",
    ]
    return "".join(parts)
