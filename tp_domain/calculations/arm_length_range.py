"""
Motor de rango de plena competencia.

Flujo: cargar dataset -> filtrar comparables (con log de rechazos) ->
percentiles -> un veredicto por jurisdicción implicada -> factores de riesgo ->
conclusión determinista.

Alcance de Fase 1: cánones sobre intangibles. El método aplicado es un
benchmarking de tipos de canon comparables, es decir CUP; TNMM queda para la
expansión a servicios y a operaciones con margen neto (Fase 2).
"""

import json
import uuid
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np

from tp_domain import sources as source_registry
from tp_domain.models import (
    AnalysisResult,
    BenchmarkRange,
    Comparable,
    ComparableDataset,
    DefensibilityLevel,
    PartyRole,
    RangePosition,
    RangeRule,
    RejectedComparable,
    RejectionReason,
    RiskCode,
    RiskFactor,
    Severity,
    TPMethod,
    Transaction,
)
from tp_domain.rules import statistical_rules

#: Años de antigüedad máxima admitidos para un comparable.
MAX_COMPARABLE_AGE_YEARS = 2
#: Por debajo de esta muestra, el rango se marca como poco robusto.
MIN_RECOMMENDED_SAMPLE = 5

_DATASET_PATH = Path(__file__).resolve().parent.parent / "comparables.json"

METHOD_RATIONALE_ROYALTY = (
    "CUP-based royalty benchmarking: el tipo de canon propuesto se contrasta "
    "con tipos de canon observados en operaciones comparables del mismo sector. "
    "Al comparar precio contra precio, el método aplicado es el de precio libre "
    "comparable (CUP). TNMM no procede aquí: exigiría contrastar el margen neto "
    "de una parte analizada, no el tipo de la operación."
)


# ---------------------------------------------------------------------------
# Carga del dataset
# ---------------------------------------------------------------------------

def load_dataset(path: Optional[Path] = None) -> ComparableDataset:
    """Carga el dataset con su versión, para que el análisis sea reproducible."""
    with open(path or _DATASET_PATH, encoding="utf-8") as fh:
        raw = json.load(fh)

    if isinstance(raw, dict) and "comparables" in raw:
        version = str(raw.get("_metadata", {}).get("version", "unknown"))
        items = raw["comparables"]
    else:  # dataset plano (formato antiguo)
        version, items = "unknown", raw

    return ComparableDataset(
        version=version,
        comparables=[Comparable(**item) for item in items],
    )


def load_comparables(path: Optional[Path] = None) -> List[Comparable]:
    """Atajo para quien solo necesita los comparables."""
    return load_dataset(path).comparables


# ---------------------------------------------------------------------------
# Filtrado
# ---------------------------------------------------------------------------

def filter_comparables(
    transaction: Transaction,
    comparables: List[Comparable],
) -> Tuple[List[Comparable], List[RejectedComparable]]:
    """
    Separa comparables aceptados de rechazados, registrando el motivo.

    La coincidencia de industria es obligatoria: sin ella el rango mezcla
    sectores con rangos de canon incompatibles y el veredicto cambia.
    """
    accepted: List[Comparable] = []
    rejected: List[RejectedComparable] = []
    min_year = transaction.effective_date.year - MAX_COMPARABLE_AGE_YEARS

    for comp in comparables:
        if comp.industry != transaction.industry:
            rejected.append(RejectedComparable(
                comparable_id=comp.id,
                company_name=comp.company_name,
                reason=RejectionReason.INDUSTRY_MISMATCH,
                detail=(
                    f"Industria '{comp.industry.value}' distinta de la operación "
                    f"analizada ('{transaction.industry.value}')."
                ),
            ))
            continue

        if comp.data_year < min_year:
            rejected.append(RejectedComparable(
                comparable_id=comp.id,
                company_name=comp.company_name,
                reason=RejectionReason.STALE_YEAR,
                detail=(
                    f"Ejercicio {comp.data_year} anterior al mínimo admitido "
                    f"({min_year}, {MAX_COMPARABLE_AGE_YEARS} años)."
                ),
            ))
            continue

        if comp.royalty_rate is None:
            rejected.append(RejectedComparable(
                comparable_id=comp.id,
                company_name=comp.company_name,
                reason=RejectionReason.NO_RATE_DATA,
                detail="Sin tipo de canon informado.",
            ))
            continue

        accepted.append(comp)

    return accepted, rejected


# ---------------------------------------------------------------------------
# Estadística
# ---------------------------------------------------------------------------

def calculate_percentiles(values: List[float]) -> dict:
    """
    P10, P25, P50, P75 y P90 redondeados a 2 decimales.

    P10 y P90 se calculan de verdad; hasta la v0.2.0 el tramo intermedio se
    aproximaba con multiplicadores (p25*0,7) que no correspondían a ningún
    percentil real y no se podían explicar en un informe.
    """
    if not values:
        return {"p10": None, "p25": None, "p50": None, "p75": None, "p90": None, "count": 0}

    arr = np.asarray(sorted(values), dtype=float)
    return {
        "p10": round(float(np.percentile(arr, 10)), 2),
        "p25": round(float(np.percentile(arr, 25)), 2),
        "p50": round(float(np.percentile(arr, 50)), 2),
        "p75": round(float(np.percentile(arr, 75)), 2),
        "p90": round(float(np.percentile(arr, 90)), 2),
        "count": len(values),
    }


def calculate_defensibility_score(position: RangePosition) -> int:
    """Puntuación 1-10 derivada de la posición en el rango. Ver POSITION_SCORING."""
    return statistical_rules.POSITION_SCORING[position][1]


# ---------------------------------------------------------------------------
# Motor
# ---------------------------------------------------------------------------

def _risk_factors(
    transaction: Transaction,
    benchmark: BenchmarkRange,
    assessments: List,
) -> List[RiskFactor]:
    rate = float(transaction.rate_percent)
    factors: List[RiskFactor] = [
        RiskFactor(
            code=RiskCode.SYNTHETIC_DATA,
            severity=Severity.INFO,
            message=(
                "Los comparables empleados son sintéticos. Este análisis "
                "demuestra el funcionamiento del motor y no constituye un "
                "estudio de benchmarking oponible ante una administración."
            ),
            source_ids=["tpip-dataset-v1"],
        )
    ]

    if benchmark.percentile_75 is not None and rate > benchmark.percentile_75:
        factors.append(RiskFactor(
            code=RiskCode.RATE_ABOVE_RANGE,
            severity=Severity.WARNING,
            message=(
                f"El tipo propuesto ({rate}%) supera el P75 del rango "
                f"({benchmark.percentile_75}%)."
            ),
            source_ids=["oecd-tpg-2022-cap3"],
        ))

    if benchmark.percentile_25 is not None and rate < benchmark.percentile_25:
        factors.append(RiskFactor(
            code=RiskCode.RATE_BELOW_RANGE,
            severity=Severity.WARNING,
            message=(
                f"El tipo propuesto ({rate}%) está por debajo del P25 del rango "
                f"({benchmark.percentile_25}%)."
            ),
            source_ids=["oecd-tpg-2022-cap3"],
        ))

    if 0 < benchmark.count_accepted < MIN_RECOMMENDED_SAMPLE:
        factors.append(RiskFactor(
            code=RiskCode.THIN_SAMPLE,
            severity=Severity.WARNING,
            message=(
                f"Solo {benchmark.count_accepted} comparables aceptados "
                f"(mínimo recomendado: {MIN_RECOMMENDED_SAMPLE})."
            ),
            source_ids=["oecd-tpg-2022-cap3"],
        ))

    for assessment in assessments:
        if assessment.adjusted_rate is not None:
            factors.append(RiskFactor(
                code=RiskCode.MANDATORY_ADJUSTMENT,
                severity=Severity.CRITICAL,
                message=(
                    f"{assessment.country} ajustaría el tipo de oficio a la "
                    f"mediana ({assessment.adjusted_rate}%)."
                ),
                source_ids=list(assessment.source_ids),
            ))
        if assessment.range_rule is RangeRule.NOT_MODELLED:
            factors.append(RiskFactor(
                code=RiskCode.JURISDICTION_NOT_MODELLED,
                severity=Severity.WARNING,
                message=(
                    f"La regla estadística de {assessment.country} no está "
                    f"modelada en esta versión. Su tratamiento no se ha evaluado."
                ),
            ))

    return factors


def _conclusion(transaction: Transaction, assessments: List) -> str:
    rate = float(transaction.rate_percent)
    head = (
        f"Canon del {rate}% ({transaction.industry.value}), "
        f"{transaction.payer_country} → {transaction.recipient_country}."
    )
    if not assessments:
        return head + " Sin comparables suficientes para emitir veredicto."

    levels = {a.defensibility_level for a in assessments}
    if levels == {DefensibilityLevel.STRONG}:
        verdict = "Posición defendible en ambas jurisdicciones analizadas."
    elif any(a.adjusted_rate is not None for a in assessments):
        verdict = (
            "Tratamiento asimétrico: al menos una jurisdicción impone ajuste "
            "de oficio y otra remite a valoración caso por caso."
        )
    else:
        verdict = "Posición fuera del rango intercuartílico; requiere documentación soporte."

    detail = " ".join(a.consequence for a in assessments)
    return f"{head} {verdict} {detail}"


def calculate_arm_length_range(
    transaction: Transaction,
    comparables: Optional[List[Comparable]] = None,
    dataset_version: Optional[str] = None,
) -> AnalysisResult:
    """
    Analiza si un canon se sitúa en plena competencia, jurisdicción a jurisdicción.

    El rango es un hecho de mercado y se calcula una sola vez; el veredicto se
    emite tantas veces como jurisdicciones intervienen en la operación.
    """
    if comparables is None:
        dataset = load_dataset()
        comparables = dataset.comparables
        dataset_version = dataset.version
    elif dataset_version is None:
        dataset_version = "in-memory"

    accepted, rejected = filter_comparables(transaction, comparables)
    rates = [c.royalty_rate for c in accepted if c.royalty_rate is not None]
    pct = calculate_percentiles(rates)

    benchmark = BenchmarkRange(
        percentile_10=pct["p10"],
        percentile_25=pct["p25"],
        percentile_50=pct["p50"],
        percentile_75=pct["p75"],
        percentile_90=pct["p90"],
        count_accepted=pct["count"],
    )

    assessments = []
    if pct["count"] > 0:
        rate = float(transaction.rate_percent)
        assessments = [
            statistical_rules.assess(transaction.payer_country, PartyRole.PAYER, rate, benchmark),
            statistical_rules.assess(transaction.recipient_country, PartyRole.RECIPIENT, rate, benchmark),
        ]

    risk_factors = _risk_factors(transaction, benchmark, assessments)
    if pct["count"] == 0:
        risk_factors.append(RiskFactor(
            code=RiskCode.NO_COMPARABLES,
            severity=Severity.CRITICAL,
            message=(
                "No se han encontrado comparables aceptables para esta "
                "operación. No es posible construir un rango."
            ),
            source_ids=["oecd-tpg-2022-cap3"],
        ))

    cited = ["tpip-dataset-v1", "oecd-tpg-2022-cap6"]
    for item in list(assessments) + list(risk_factors):
        cited.extend(item.source_ids)

    return AnalysisResult(
        analysis_id=transaction.id or f"TPIP-{uuid.uuid4().hex[:8].upper()}",
        dataset_version=dataset_version,
        transaction=transaction,
        method_applied=TPMethod.CUP,
        method_rationale=METHOD_RATIONALE_ROYALTY,
        benchmark=benchmark,
        comparables_accepted=accepted,
        comparables_rejected=rejected,
        assessments=assessments,
        risk_factors=risk_factors,
        sources=source_registry.resolve(cited),
        conclusion=_conclusion(transaction, assessments),
    )
