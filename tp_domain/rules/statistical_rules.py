"""
Regla estadística del rango de plena competencia, por jurisdicción.

Fuente del criterio:
    documentation/tax-research/jurisdictions/spain/art18-lis-operaciones-vinculadas.md
    documentation/tax-research/jurisdictions/germany/astg-rango-intercuartilico-ajuste-mediana.md
Fuentes primarias:
    Ley 27/2014 (LIS), Art. 18.4  ·  Außensteuergesetz (AStG), §1.3a

El rango es un hecho de mercado y no tiene nacionalidad. Lo que cambia por país
es la CONSECUENCIA de caer fuera de él, y esa asimetría es el núcleo del
producto: el mismo canon, con los mismos comparables, recibe tratamiento
distinto en España y en Alemania.

Nota deliberada: una jurisdicción no modelada devuelve `NOT_MODELLED`, no la
regla española por defecto. Asumir "sin regla" para un país que no se ha
estudiado sería inventar Derecho comparado.
"""

from typing import Dict, List, Optional, Tuple

from tp_domain.models import (
    BenchmarkRange,
    DefensibilityLevel,
    JurisdictionAssessment,
    PartyRole,
    RangePosition,
    RangeRule,
)

#: Mapa jurisdicción -> regla. Crece ficha a ficha, nunca por analogía.
JURISDICTION_RANGE_RULES: Dict[str, RangeRule] = {
    "ES": RangeRule.NO_STATUTORY_RULE,
    "DE": RangeRule.INTERQUARTILE_MEDIAN_ADJUSTMENT,
}

#: Fuentes que justifican cada regla.
_RULE_SOURCES: Dict[RangeRule, List[str]] = {
    RangeRule.NO_STATUTORY_RULE: ["es-lis-art18-4", "oecd-tpg-2022-cap3"],
    RangeRule.INTERQUARTILE_MEDIAN_ADJUSTMENT: ["de-astg-1-3a", "oecd-tpg-2022-cap3"],
    RangeRule.NOT_MODELLED: ["oecd-tpg-2022-cap3"],
}

#: Posición -> (nivel, puntuación).
#:
#: Tres niveles con etiqueta numérica, no una escala continua de 1 a 10. Se
#: documenta así a propósito: la puntuación se deriva de una frontera que
#: existe (P10 y P90 calculados sobre la muestra), no de un multiplicador
#: arbitrario. Cualquier explicación de esta cifra cabe en una frase.
POSITION_SCORING: Dict[RangePosition, Tuple[DefensibilityLevel, int]] = {
    RangePosition.WITHIN_IQR: (DefensibilityLevel.STRONG, 9),
    RangePosition.P10_TO_P25: (DefensibilityLevel.MODERATE, 6),
    RangePosition.P75_TO_P90: (DefensibilityLevel.MODERATE, 6),
    RangePosition.BELOW_P10: (DefensibilityLevel.WEAK, 2),
    RangePosition.ABOVE_P90: (DefensibilityLevel.WEAK, 2),
}


def rule_for(country: str) -> RangeRule:
    """Devuelve la regla estadística de una jurisdicción."""
    return JURISDICTION_RANGE_RULES.get(country.upper(), RangeRule.NOT_MODELLED)


def classify_position(rate: float, benchmark: BenchmarkRange) -> RangePosition:
    """
    Sitúa el tipo propuesto en el rango. Los límites P25 y P75 son inclusivos.

    Requiere un benchmark con datos; comprobarlo es responsabilidad del motor.
    """
    p10 = benchmark.percentile_10
    p25 = benchmark.percentile_25
    p75 = benchmark.percentile_75
    p90 = benchmark.percentile_90

    if p25 <= rate <= p75:
        return RangePosition.WITHIN_IQR
    if rate < p10:
        return RangePosition.BELOW_P10
    if rate > p90:
        return RangePosition.ABOVE_P90
    if rate < p25:
        return RangePosition.P10_TO_P25
    return RangePosition.P75_TO_P90


def _consequence(
    country: str,
    rule: RangeRule,
    position: RangePosition,
    benchmark: BenchmarkRange,
    adjusted_rate: Optional[float],
) -> str:
    """Redacción determinista. El informe se genera sin IA."""
    inside = position is RangePosition.WITHIN_IQR
    p25, p50, p75 = (
        benchmark.percentile_25,
        benchmark.percentile_50,
        benchmark.percentile_75,
    )

    if rule is RangeRule.INTERQUARTILE_MEDIAN_ADJUSTMENT:
        if inside:
            return (
                f"{country}: el tipo se sitúa dentro del rango intercuartílico "
                f"({p25}%-{p75}%). El §1.3a AStG no habilita ajuste."
            )
        return (
            f"{country}: el tipo queda fuera del rango intercuartílico "
            f"({p25}%-{p75}%). El §1.3a AStG impone el ajuste a la mediana "
            f"({adjusted_rate}%) como consecuencia por defecto, salvo que el "
            f"contribuyente acredite de forma verosímil que otro punto del "
            f"rango se ajusta mejor al principio de plena competencia."
        )

    if rule is RangeRule.NO_STATUTORY_RULE:
        if inside:
            return (
                f"{country}: el tipo se sitúa dentro del rango intercuartílico "
                f"({p25}%-{p75}%). El Art. 18.4 LIS no impone regla estadística; "
                f"la posición es defendible con la documentación del método."
            )
        return (
            f"{country}: el tipo queda fuera del rango intercuartílico "
            f"({p25}%-{p75}%). El Art. 18.4 LIS no impone ajuste automático a la "
            f"mediana ({p50}%): la corrección valorativa depende de la "
            f"valoración caso por caso de la Inspección, lo que eleva la "
            f"exigencia de documentación soporte."
        )

    return (
        f"{country}: jurisdicción no modelada en esta versión de TPIP. No se "
        f"presume la regla de ningún otro Estado. Referencia de mercado: "
        f"{p25}%-{p75}%."
    )


def assess(
    country: str,
    role: PartyRole,
    rate: float,
    benchmark: BenchmarkRange,
) -> JurisdictionAssessment:
    """Construye el veredicto de UNA jurisdicción sobre la operación."""
    rule = rule_for(country)
    position = classify_position(rate, benchmark)
    level, score = POSITION_SCORING[position]

    adjusted_rate = None
    if (
        rule is RangeRule.INTERQUARTILE_MEDIAN_ADJUSTMENT
        and position is not RangePosition.WITHIN_IQR
    ):
        adjusted_rate = benchmark.percentile_50

    return JurisdictionAssessment(
        country=country.upper(),
        role=role,
        range_rule=rule,
        position=position,
        defensibility_level=level,
        defensibility_score=score,
        adjusted_rate=adjusted_rate,
        consequence=_consequence(country.upper(), rule, position, benchmark, adjusted_rate),
        source_ids=list(_RULE_SOURCES[rule]),
    )
