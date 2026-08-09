"""
Informe profesional de precios de transferencia en PDF.

Esta capa RENDERIZA: no calcula, no interpreta y no decide. Recibe un
`AnalysisResult` ya cerrado y lo maqueta. Cualquier aritmética que apareciera
aquí sería lógica fiscal fuera de `tp_domain/`.

El informe se genera íntegro sin llamar a ninguna API. La explicación de IA es
una sección aditiva: si no existe, el documento sigue estando completo y se
declara como tal en lugar de dejar un hueco silencioso.

Estructura:
    1. Portada          — identificación, versiones, disclaimer del dataset
    2. Resumen ejecutivo — operación, rango, posición, veredicto por jurisdicción
    3. Benchmark        — gráfico del rango, metodología, muestra
    4. Fundamento       — consecuencias por jurisdicción y fuentes citadas
    5. Análisis asistido por IA — presente o declarado ausente
    6. Anexo            — comparables aceptados y rechazados, con motivo
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import List, Optional, Union
from xml.sax.saxutils import escape

from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from tp_domain.models import (
    AnalysisResult,
    DefensibilityLevel,
    RangePosition,
    RangeRule,
    RejectionReason,
    Severity,
)

# ---------------------------------------------------------------------------
# Paleta y tipografía
#
# Deliberadamente sobria y sin dependencias de fuentes externas: el acabado
# visual se aborda en el pase de presentación, no aquí. Lo que se fija ahora es
# la estructura fiscal del documento.
# ---------------------------------------------------------------------------

INK = colors.HexColor("#1A1A1A")
MUTED = colors.HexColor("#5A5A5A")
RULE = colors.HexColor("#C8C8C8")
BAND_OUTER = colors.HexColor("#DCE3EC")   # P10-P90
BAND_INNER = colors.HexColor("#9FB3C8")   # P25-P75 (rango intercuartílico)
MEDIAN = colors.HexColor("#334E68")
ACCENT_OK = colors.HexColor("#2E6B4F")
ACCENT_WARN = colors.HexColor("#8A6D1F")
ACCENT_RISK = colors.HexColor("#8C2F2F")

_LEVEL_COLOR = {
    DefensibilityLevel.STRONG: ACCENT_OK,
    DefensibilityLevel.MODERATE: ACCENT_WARN,
    DefensibilityLevel.WEAK: ACCENT_RISK,
}
_LEVEL_LABEL = {
    DefensibilityLevel.STRONG: "Defendible",
    DefensibilityLevel.MODERATE: "Moderado",
    DefensibilityLevel.WEAK: "Riesgo alto",
}
_SEVERITY_LABEL = {
    Severity.INFO: "Información",
    Severity.WARNING: "Advertencia",
    Severity.CRITICAL: "Crítico",
}
_REJECTION_LABEL = {
    RejectionReason.INDUSTRY_MISMATCH: "Sector no coincidente",
    RejectionReason.STALE_YEAR: "Ejercicio fuera de ventana",
    RejectionReason.NO_RATE_DATA: "Sin dato de canon",
}
_POSITION_LABEL = {
    RangePosition.BELOW_P10: "Por debajo del P10",
    RangePosition.P10_TO_P25: "Entre P10 y P25",
    RangePosition.WITHIN_IQR: "Dentro del rango intercuartílico",
    RangePosition.P75_TO_P90: "Entre P75 y P90",
    RangePosition.ABOVE_P90: "Por encima del P90",
}

def _safe(text: str) -> str:
    """
    Escapa el texto que va dentro de un `Paragraph`.

    ReportLab interpreta marcado XML en los párrafos: un `&` o un `<` en un
    nombre de compañía o en el texto de una fuente rompería la maquetación o,
    peor, se tragaría contenido sin avisar. Todo texto procedente del dominio
    pasa por aquí.

    No hace falta sustituir glifos: las fuentes base de ReportLab 4 dibujan
    correctamente los caracteres tipográficos que usa el motor (flechas, §,
    acentos, comillas).
    """
    return escape(str(text))


def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "TpipTitle", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=24, leading=28, textColor=INK, alignment=0, spaceAfter=2,
        ),
        "subtitle": ParagraphStyle(
            "TpipSubtitle", parent=base["Normal"], fontName="Helvetica",
            fontSize=11.5, leading=16, textColor=MUTED, spaceAfter=18,
        ),
        "h1": ParagraphStyle(
            "TpipH1", parent=base["Heading1"], fontName="Helvetica-Bold",
            fontSize=14, leading=18, textColor=INK, spaceBefore=16, spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "TpipH2", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=11, leading=15, textColor=INK, spaceBefore=12, spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "TpipBody", parent=base["BodyText"], fontName="Helvetica",
            fontSize=9.5, leading=14, textColor=INK, alignment=TA_JUSTIFY,
            spaceAfter=7,
        ),
        "small": ParagraphStyle(
            "TpipSmall", parent=base["Normal"], fontName="Helvetica",
            fontSize=8, leading=11, textColor=MUTED, spaceAfter=4,
        ),
        "cell": ParagraphStyle(
            "TpipCell", parent=base["Normal"], fontName="Helvetica",
            fontSize=7.5, leading=10, textColor=INK,
        ),
        "disclaimer": ParagraphStyle(
            "TpipDisclaimer", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=9, leading=13, textColor=ACCENT_RISK, alignment=TA_JUSTIFY,
        ),
    }


# ---------------------------------------------------------------------------
# Gráfico del rango
# ---------------------------------------------------------------------------

def _range_chart(result: AnalysisResult, width: float = 460, height: float = 120) -> Drawing:
    """
    Rango de plena competencia con el tipo analizado situado sobre él.

    Es el gráfico que aparece en cualquier estudio de benchmarking real: banda
    P10-P90, banda intercuartílica P25-P75 destacada, mediana y tested rate.
    """
    b = result.benchmark
    rate = float(result.transaction.rate_percent)
    p10, p25, p50, p75, p90 = (
        b.percentile_10, b.percentile_25, b.percentile_50,
        b.percentile_75, b.percentile_90,
    )

    drawing = Drawing(width, height)

    left, right = 46.0, width - 26.0
    axis_y, band_h = 42.0, 26.0

    lo, hi = min(p10, rate), max(p90, rate)
    pad = max((hi - lo) * 0.12, 0.4)
    lo, hi = lo - pad, hi + pad
    span = hi - lo or 1.0

    def x(value: float) -> float:
        return left + (value - lo) / span * (right - left)

    # Bandas
    drawing.add(Rect(x(p10), axis_y, x(p90) - x(p10), band_h,
                     fillColor=BAND_OUTER, strokeColor=None))
    drawing.add(Rect(x(p25), axis_y, x(p75) - x(p25), band_h,
                     fillColor=BAND_INNER, strokeColor=None))
    drawing.add(Line(x(p50), axis_y - 3, x(p50), axis_y + band_h + 3,
                     strokeColor=MEDIAN, strokeWidth=1.6))

    # Eje
    drawing.add(Line(left, axis_y - 6, right, axis_y - 6,
                     strokeColor=RULE, strokeWidth=0.7))

    # Marcas de percentil
    for value, label in ((p10, "P10"), (p25, "P25"), (p50, "Mediana"),
                         (p75, "P75"), (p90, "P90")):
        drawing.add(Line(x(value), axis_y - 9, x(value), axis_y - 6,
                         strokeColor=RULE, strokeWidth=0.7))
        drawing.add(String(x(value), axis_y - 20, label,
                           fontName="Helvetica", fontSize=6.5,
                           fillColor=MUTED, textAnchor="middle"))
        drawing.add(String(x(value), axis_y - 29, f"{value}%",
                           fontName="Helvetica-Bold", fontSize=7,
                           fillColor=INK, textAnchor="middle"))

    # Tipo analizado
    marker_x, top = x(rate), axis_y + band_h
    inside = p25 <= rate <= p75
    marker_color = ACCENT_OK if inside else ACCENT_RISK
    drawing.add(Polygon(
        [marker_x, top + 4, marker_x - 5, top + 13, marker_x + 5, top + 13],
        fillColor=marker_color, strokeColor=None,
    ))
    drawing.add(String(marker_x, top + 18, f"Tipo analizado {rate}%",
                       fontName="Helvetica-Bold", fontSize=8.5,
                       fillColor=marker_color, textAnchor="middle"))

    drawing.add(String(right, 6, f"n = {b.count_accepted} comparables aceptados",
                       fontName="Helvetica", fontSize=7, fillColor=MUTED,
                       textAnchor="end"))
    return drawing


# ---------------------------------------------------------------------------
# Utilidades de maquetación
# ---------------------------------------------------------------------------

_KV_VALUE_STYLE = ParagraphStyle(
    "TpipKvValue", fontName="Helvetica", fontSize=8.5, leading=11.5, textColor=INK,
)

def _kv_table(rows: List[tuple], widths=(52 * mm, 108 * mm), style_cell=None) -> Table:
    # El valor va en Paragraph para que los textos largos (criterios, notas)
    # hagan salto de línea en vez de desbordar el margen derecho.
    value_style = style_cell or _KV_VALUE_STYLE
    table = Table(
        # La clave es una celda de texto plano (sin XML); el valor va en
        # Paragraph para que haga salto de línea, y por eso sí se escapa.
        [[str(k), Paragraph(_safe(str(v)), value_style)] for k, v in rows],
        colWidths=widths,
    )
    table.setStyle(TableStyle([
        ("FONT", (0, 0), (0, -1), "Helvetica-Bold", 8.5),
        ("TEXTCOLOR", (0, 0), (0, -1), MUTED),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LINEBELOW", (0, 0), (-1, -2), 0.25, RULE),
    ]))
    return table


def _data_table(header: List[str], rows: List[List[str]], widths, style_cell) -> Table:
    data = [[Paragraph(f"<b>{_safe(h)}</b>", style_cell) for h in header]]
    data += [[Paragraph(_safe(str(c)), style_cell) for c in row] for row in rows]
    table = Table(data, colWidths=widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EFF2F6")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.25, RULE),
    ]))
    return table


# ---------------------------------------------------------------------------
# Secciones
# ---------------------------------------------------------------------------

def _cover(result: AnalysisResult, st) -> list:
    t = result.transaction
    dataset_source = next((s for s in result.sources if s.id == "tpip-dataset-v1"), None)

    story = [
        Spacer(1, 26 * mm),
        Paragraph("TPIP", st["title"]),
        Paragraph(
            "Transfer Pricing Intelligence Platform<br/>"
            "Informe de análisis de plena competencia",
            st["subtitle"],
        ),
        Spacer(1, 4 * mm),
        _kv_table([
            ("Referencia del análisis", result.analysis_id),
            ("Fecha de emisión", f"{result.created_at:%d/%m/%Y %H:%M}"),
            ("Operación", t.description),
            ("Corredor", f"{t.payer_country} -> {t.recipient_country}"),
            ("Tipo de operación", t.transaction_type.value),
            ("Sector", t.industry.value),
            ("Fecha de efecto", f"{t.effective_date:%d/%m/%Y}"),
            ("Método aplicado", result.method_applied.value.upper()),
            ("Versión del motor", result.engine_version),
            ("Versión del dataset", result.dataset_version),
        ]),
        Spacer(1, 12 * mm),
        Paragraph("Advertencia sobre los datos", st["h2"]),
    ]

    if dataset_source and dataset_source.disclaimer:
        story.append(Paragraph(_safe(dataset_source.disclaimer), st["disclaimer"]))

    story += [
        Spacer(1, 6 * mm),
        Paragraph(
            "Este documento se genera automáticamente a partir de un motor de "
            "cálculo determinista. No constituye asesoramiento fiscal y requiere "
            "revisión profesional antes de cualquier uso.",
            st["small"],
        ),
        PageBreak(),
    ]
    return story


def _executive_summary(result: AnalysisResult, st) -> list:
    t = result.transaction
    b = result.benchmark
    position = result.assessments[0].position if result.assessments else None

    story = [
        Paragraph("1. Resumen ejecutivo", st["h1"]),
        Paragraph(_safe(result.conclusion), st["body"]),
        Spacer(1, 2 * mm),
        Paragraph("Operación analizada", st["h2"]),
        _kv_table([
            ("Descripción", t.description),
            ("Importe", f"{t.amount_eur:,.2f} EUR".replace(",", " ")),
            ("Tipo propuesto", f"{float(t.rate_percent)}%"),
            ("Jurisdicción pagadora", t.payer_country),
            ("Jurisdicción perceptora", t.recipient_country),
        ]),
        Spacer(1, 4 * mm),
        Paragraph("Rango de plena competencia", st["h2"]),
        _kv_table([
            ("Rango intercuartílico (P25-P75)", f"{b.percentile_25}% - {b.percentile_75}%"),
            ("Mediana", f"{b.percentile_50}%"),
            ("Rango ampliado (P10-P90)", f"{b.percentile_10}% - {b.percentile_90}%"),
            ("Posición del tipo analizado",
             _POSITION_LABEL[position] if position else "no determinable"),
            ("Comparables aceptados", b.count_accepted),
        ]),
        Spacer(1, 4 * mm),
        Paragraph("Evaluación por jurisdicción", st["h2"]),
    ]

    if result.assessments:
        rows = []
        for a in result.assessments:
            rows.append([
                a.country,
                "Pagadora" if a.role.value == "payer" else "Perceptora",
                _LEVEL_LABEL[a.defensibility_level],
                f"{a.defensibility_score}/10" if a.defensibility_score else "-",
                f"{a.adjusted_rate}%" if a.adjusted_rate is not None else "No automático",
            ])
        story.append(_data_table(
            ["Jurisdicción", "Rol", "Valoración", "Puntuación", "Ajuste de oficio"],
            rows,
            (26 * mm, 24 * mm, 32 * mm, 24 * mm, 54 * mm),
            st["cell"],
        ))
    else:
        story.append(Paragraph(
            "No ha sido posible emitir evaluación jurisdiccional: la muestra de "
            "comparables no permite construir un rango.", st["body"]))

    return story


def _benchmark_section(result: AnalysisResult, st) -> list:
    b = result.benchmark
    story = [
        PageBreak(),
        Paragraph("2. Análisis de benchmark", st["h1"]),
        Paragraph(_safe(result.method_rationale), st["body"]),
        Spacer(1, 3 * mm),
    ]
    if b.count_accepted:
        story.append(KeepTogether(_range_chart(result)))
    story += [
        Spacer(1, 4 * mm),
        Paragraph("Metodología", st["h2"]),
        _kv_table([
            ("Método de precios de transferencia", result.method_applied.value.upper()),
            ("Cálculo de percentiles", b.percentile_method),
            ("Comparables aceptados", b.count_accepted),
            ("Comparables rechazados", len(result.comparables_rejected)),
            ("Criterios de aceptación",
             "Coincidencia exacta de sector, antigüedad máxima de 2 ejercicios "
             "y disponibilidad de tipo de canon"),
        ]),
        Spacer(1, 4 * mm),
        Paragraph("Factores de riesgo identificados", st["h2"]),
    ]

    rows = [[_SEVERITY_LABEL[f.severity], f.message] for f in result.risk_factors]
    story.append(_data_table(
        ["Severidad", "Descripción"], rows, (26 * mm, 134 * mm), st["cell"],
    ))
    return story


def _basis_section(result: AnalysisResult, st) -> list:
    story = [
        PageBreak(),
        Paragraph("3. Fundamento y consecuencias por jurisdicción", st["h1"]),
    ]

    for a in result.assessments:
        rule_label = {
            RangeRule.NO_STATUTORY_RULE: "Sin regla estadística legal",
            RangeRule.INTERQUARTILE_MEDIAN_ADJUSTMENT:
                "Rango intercuartílico con ajuste obligatorio a la mediana",
            RangeRule.NOT_MODELLED: "Jurisdicción no modelada en esta versión",
        }[a.range_rule]

        cited = [s for s in result.sources if s.id in a.source_ids]
        story += [
            Paragraph(f"{a.country} — {rule_label}", st["h2"]),
            Paragraph(_safe(a.consequence), st["body"]),
            Paragraph(
                "Fuentes: " + "; ".join(
                    s.citation + (f" ({s.pinpoint})" if s.pinpoint else "") for s in cited
                ),
                st["small"],
            ),
            Spacer(1, 2 * mm),
        ]

    story += [
        Spacer(1, 2 * mm),
        Paragraph("Fuentes utilizadas en este análisis", st["h1"]),
        Paragraph(
            "El motor solo puede citar fuentes de un registro cerrado. Toda "
            "afirmación de este informe, incluida la redactada con asistencia de "
            "IA, procede de las entradas siguientes.",
            st["body"],
        ),
    ]

    rows = []
    for s in result.sources:
        detail = s.citation
        if s.pinpoint:
            detail += f" — {s.pinpoint}"
        if s.official_ref:
            detail += f" [{s.official_ref}]"
        rows.append([s.kind.value, detail, s.disclaimer or "-"])

    story.append(_data_table(
        ["Tipo", "Referencia", "Nota"], rows,
        (22 * mm, 68 * mm, 70 * mm), st["cell"],
    ))
    return story


def _ai_section(result: AnalysisResult, st) -> list:
    story = [
        PageBreak(),
        Paragraph("4. Análisis asistido por inteligencia artificial", st["h1"]),
    ]
    explanation = result.ai_explanation

    if explanation is None:
        story += [
            Paragraph(
                "Este informe se ha generado sin asistencia de IA. Todo su "
                "contenido procede del motor de cálculo determinista y de las "
                "fuentes citadas en el apartado anterior.",
                st["body"],
            ),
            Paragraph(
                "La explicación asistida por IA es una sección aditiva: su "
                "ausencia no afecta a la validez ni a la integridad del análisis.",
                st["small"],
            ),
        ]
        return story

    cited = [s for s in result.sources if s.id in explanation.sources_cited]
    story += [
        Paragraph(_safe(explanation.text), st["body"]),
        Spacer(1, 3 * mm),
        Paragraph("Trazabilidad de la explicación", st["h2"]),
        _kv_table([
            ("Modelo", explanation.model),
            ("Versión del prompt", explanation.prompt_version),
            ("Generada el", f"{explanation.generated_at:%d/%m/%Y %H:%M}"),
            ("Fuentes citadas",
             "; ".join(s.citation for s in cited) if cited else "ninguna"),
        ]),
        Paragraph(
            "La IA explica un resultado ya calculado. No determina precios, no "
            "selecciona comparables y no puede citar fuentes distintas de las "
            "emitidas por el motor: la validación es estructural.",
            st["small"],
        ),
    ]
    return story


def _annex(result: AnalysisResult, st) -> list:
    story = [
        PageBreak(),
        Paragraph("5. Anexo — conjunto de comparables", st["h1"]),
        Paragraph(
            "Se detalla el conjunto completo de comparables examinados, con el "
            "motivo de descarte de cada observación rechazada. La trazabilidad "
            "del filtro forma parte del estudio: sin ella no es posible "
            "contrastar la selección.",
            st["body"],
        ),
        Paragraph(
            f"Anexo I — Comparables aceptados ({len(result.comparables_accepted)})",
            st["h2"],
        ),
    ]

    rows = [
        [c.id, c.company_name, c.country, c.industry.value,
         f"{c.royalty_rate}%", c.data_year]
        for c in result.comparables_accepted
    ]
    story.append(_data_table(
        ["ID", "Compañía", "País", "Sector", "Canon", "Ejercicio"],
        rows or [["-", "Ninguno", "-", "-", "-", "-"]],
        (20 * mm, 58 * mm, 15 * mm, 30 * mm, 18 * mm, 19 * mm),
        st["cell"],
    ))

    story += [
        Spacer(1, 5 * mm),
        Paragraph(
            f"Anexo II — Comparables rechazados ({len(result.comparables_rejected)})",
            st["h2"],
        ),
    ]
    rows = [
        [r.comparable_id, r.company_name, _REJECTION_LABEL[r.reason], r.detail]
        for r in result.comparables_rejected
    ]
    story.append(_data_table(
        ["ID", "Compañía", "Motivo", "Detalle"],
        rows or [["-", "Ninguno", "-", "-"]],
        (18 * mm, 44 * mm, 30 * mm, 68 * mm),
        st["cell"],
    ))
    return story


# ---------------------------------------------------------------------------
# Documento
# ---------------------------------------------------------------------------

def _page_furniture(result: AnalysisResult):
    def draw(canvas, doc):
        canvas.saveState()
        width, height = A4
        if doc.page > 1:
            canvas.setFont("Helvetica", 7)
            canvas.setFillColor(MUTED)
            canvas.drawString(
                20 * mm, height - 12 * mm,
                f"TPIP — Informe de plena competencia · {result.analysis_id}",
            )
            canvas.setStrokeColor(RULE)
            canvas.setLineWidth(0.4)
            canvas.line(20 * mm, height - 14 * mm, width - 20 * mm, height - 14 * mm)

        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(MUTED)
        canvas.drawString(
            20 * mm, 12 * mm,
            "Datos sintéticos — documento de demostración, no constituye "
            "asesoramiento fiscal",
        )
        canvas.drawRightString(width - 20 * mm, 12 * mm, f"Página {doc.page}")
        canvas.restoreState()

    return draw


def render_report_bytes(result: AnalysisResult) -> bytes:
    """Devuelve el informe como bytes, sin tocar disco."""
    buffer = io.BytesIO()
    st = _styles()

    doc = BaseDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20 * mm, rightMargin=20 * mm,
        topMargin=20 * mm, bottomMargin=18 * mm,
        title=f"TPIP — Informe {result.analysis_id}",
        author="Transfer Pricing Intelligence Platform",
        subject="Análisis de plena competencia",
    )
    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, doc.height, id="body",
    )
    doc.addPageTemplates([
        PageTemplate(id="tpip", frames=[frame], onPage=_page_furniture(result))
    ])

    story: list = []
    story += _cover(result, st)
    story += _executive_summary(result, st)
    story += _benchmark_section(result, st)
    story += _basis_section(result, st)
    story += _ai_section(result, st)
    story += _annex(result, st)

    doc.build(story)
    return buffer.getvalue()


def build_report(
    result: AnalysisResult,
    output_path: Optional[Union[str, Path]] = None,
) -> Path:
    """Escribe el informe en disco y devuelve la ruta."""
    path = Path(output_path) if output_path else Path(f"{result.analysis_id}.pdf")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(render_report_bytes(result))
    return path
