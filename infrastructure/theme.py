"""
Lenguaje visual compartido entre la interfaz y el informe.

Existe por una razón concreta: que la pantalla y el PDF parezcan el mismo
producto. Antes de este módulo, la paleta vivía dentro del generador de PDF y
la interfaz usaba los colores por defecto de Streamlit; las etiquetas
humanizadas ("Pagadora", "Sector no coincidente") existían solo en el informe y
la pantalla mostraba los valores crudos del enum.

Aquí viven tres cosas y ninguna más:

- la paleta, en hexadecimal neutro (cada renderizador la convierte a su tipo);
- las etiquetas legibles de cada enum del dominio;
- la geometría del rango, normalizada a fracciones 0-1.

La geometría es la pieza que garantiza que el gráfico de la pantalla y el del
informe representen exactamente lo mismo: ambos parten de estas fracciones y
solo cambian el sistema de coordenadas al que las proyectan.

No hay lógica fiscal en este módulo. Traduce y coloca; no decide.
"""

from __future__ import annotations

from typing import Dict, Optional

from tp_domain.models import (
    BenchmarkRange,
    DefensibilityLevel,
    PartyRole,
    RangePosition,
    RangeRule,
    RejectionReason,
    Severity,
    VerificationConfidence,
)

# ---------------------------------------------------------------------------
# Paleta
#
# Sobria a propósito: gris tinta para el texto, azules apagados para el rango y
# tres acentos desaturados para el veredicto. Nada decorativo. El color solo
# aparece donde comunica algo.
# ---------------------------------------------------------------------------

COLORS: Dict[str, str] = {
    "ink": "#1A1A1A",
    "muted": "#5A5A5A",
    "rule": "#C8C8C8",
    "surface": "#F7F8FA",
    "band_outer": "#DCE3EC",   # P10-P90
    "band_inner": "#9FB3C8",   # P25-P75, rango intercuartílico
    "median": "#334E68",
    "ok": "#2E6B4F",
    "warn": "#8A6D1F",
    "risk": "#8C2F2F",
}

LEVEL_COLOR: Dict[DefensibilityLevel, str] = {
    DefensibilityLevel.STRONG: COLORS["ok"],
    DefensibilityLevel.MODERATE: COLORS["warn"],
    DefensibilityLevel.WEAK: COLORS["risk"],
}


# ---------------------------------------------------------------------------
# Etiquetas
#
# Un enum es vocabulario de código. "industry_mismatch" no se le enseña a un
# revisor de precios de transferencia.
# ---------------------------------------------------------------------------

LEVEL_LABEL: Dict[DefensibilityLevel, str] = {
    DefensibilityLevel.STRONG: "Defendible",
    DefensibilityLevel.MODERATE: "Moderado",
    DefensibilityLevel.WEAK: "Riesgo alto",
}

SEVERITY_LABEL: Dict[Severity, str] = {
    Severity.INFO: "Información",
    Severity.WARNING: "Advertencia",
    Severity.CRITICAL: "Crítico",
}

REJECTION_LABEL: Dict[RejectionReason, str] = {
    RejectionReason.INDUSTRY_MISMATCH: "Sector no coincidente",
    RejectionReason.STALE_YEAR: "Ejercicio fuera de ventana",
    RejectionReason.NO_RATE_DATA: "Sin dato de canon",
}

POSITION_LABEL: Dict[RangePosition, str] = {
    RangePosition.BELOW_P10: "Por debajo del P10",
    RangePosition.P10_TO_P25: "Entre P10 y P25",
    RangePosition.WITHIN_IQR: "Dentro del rango intercuartílico",
    RangePosition.P75_TO_P90: "Entre P75 y P90",
    RangePosition.ABOVE_P90: "Por encima del P90",
}

ROLE_LABEL: Dict[PartyRole, str] = {
    PartyRole.PAYER: "Pagadora",
    PartyRole.RECIPIENT: "Perceptora",
}

RULE_LABEL: Dict[RangeRule, str] = {
    RangeRule.NO_STATUTORY_RULE: "Sin regla estadística legal",
    RangeRule.INTERQUARTILE_MEDIAN_ADJUSTMENT:
        "Rango intercuartílico con ajuste obligatorio a la mediana",
    RangeRule.NOT_MODELLED: "Jurisdicción no modelada en esta versión",
}

#: Versión corta para cabeceras de tarjeta, donde la larga no cabe.
RULE_LABEL_SHORT: Dict[RangeRule, str] = {
    RangeRule.NO_STATUTORY_RULE: "Sin regla estadística",
    RangeRule.INTERQUARTILE_MEDIAN_ADJUSTMENT: "Ajuste a la mediana",
    RangeRule.NOT_MODELLED: "No modelada",
}

#: Distingue una fuente confirmada contra su texto primario de una leída de
#: forma dirigida — una fecha de verificación sola no debe sugerir el mismo
#: grado de certeza en ambos casos (Fase 1, campo `Source.verification_confidence`).
VERIFICATION_CONFIDENCE_LABEL: Dict[VerificationConfidence, str] = {
    VerificationConfidence.PRIMARY_SOURCE_VERIFIED: "Verificado contra fuente primaria",
    VerificationConfidence.DIRECTED_READING: "Lectura dirigida, no exhaustiva",
}


# ---------------------------------------------------------------------------
# Geometría del rango
# ---------------------------------------------------------------------------

#: Aire a cada lado, como fracción del recorrido representado.
_PADDING = 0.12
_MIN_PADDING = 0.4


def range_geometry(
    benchmark: BenchmarkRange,
    rate: float,
) -> Optional[Dict[str, float]]:
    """
    Posiciones normalizadas (0-1) de los percentiles y del tipo analizado.

    Devuelve `None` si el benchmark no tiene datos: dibujar un rango vacío
    sería peor que no dibujar nada.

    La escala se estira para incluir siempre el tipo analizado, aunque caiga
    lejos del rango. Recortarlo contra el borde ocultaría precisamente lo que
    hay que ver.
    """
    values = (
        benchmark.percentile_10, benchmark.percentile_25, benchmark.percentile_50,
        benchmark.percentile_75, benchmark.percentile_90,
    )
    if any(v is None for v in values):
        return None

    p10, p25, p50, p75, p90 = values
    low, high = min(p10, rate), max(p90, rate)
    pad = max((high - low) * _PADDING, _MIN_PADDING)
    low, high = low - pad, high + pad
    span = (high - low) or 1.0

    def fraction(value: float) -> float:
        return (value - low) / span

    return {
        "p10": fraction(p10),
        "p25": fraction(p25),
        "p50": fraction(p50),
        "p75": fraction(p75),
        "p90": fraction(p90),
        "rate": fraction(rate),
        "scale_min": low,
        "scale_max": high,
    }
