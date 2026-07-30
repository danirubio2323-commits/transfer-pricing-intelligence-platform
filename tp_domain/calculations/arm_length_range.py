"""
Arm's length range calculation.

Core algorithm: filter comparables -> calculate percentiles -> defensibility score
"""

from typing import List
from tp_domain.models import (
    Transaction, Comparable, BenchmarkRange, AnalysisResult,
    DefensibilityLevel, TPMethod
)
import numpy as np
import json
from pathlib import Path


def load_comparables() -> List[Comparable]:
    """Load comparables from JSON."""
    # comparables.json vive en tp_domain/, este módulo en tp_domain/calculations/
    path = Path(__file__).parent.parent / "comparables.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return [Comparable(**item) for item in data]


def filter_comparables(
    transaction: Transaction,
    comparables: List[Comparable]
) -> List[Comparable]:
    """
    Filter comparables by industry and transaction type.

    CRITICAL: Industry match is mandatory for valid benchmarking.
    Different industries have completely different rate ranges.
    """
    filtered = []

    for comp in comparables:
        # Year filter
        if comp.data_year < transaction.effective_date.year - 2:
            continue

        # INDUSTRY FILTER (mandatory)
        if comp.industry != transaction.industry:
            continue

        # Type-specific filter
        if transaction.transaction_type.value == "royalty":
            if comp.royalty_rate is None:
                continue
            filtered.append(comp)
        else:
            filtered.append(comp)

    return filtered


def calculate_percentiles(values: List[float]) -> dict:
    """
    Calculate P25, P50 (median), P75 for a list of values.
    """
    if not values:
        return {"p25": None, "p50": None, "p75": None, "count": 0}

    sorted_vals = sorted(values)

    return {
        "p25": float(np.percentile(sorted_vals, 25)),
        "p50": float(np.percentile(sorted_vals, 50)),
        "p75": float(np.percentile(sorted_vals, 75)),
        "count": len(sorted_vals)
    }


def calculate_defensibility_score(proposed_rate: float, p25: float, p50: float, p75: float) -> int:
    """
    Score defensibility (1-10) based on position in benchmark range.

    Rules:
    - Between P25 and P75: score = 8-10 (STRONG)
    - Between P10 and P90: score = 5-7 (MODERATE)
    - Outside P10-P90: score = 1-4 (WEAK)
    """

    if p25 <= proposed_rate <= p75:
        return 9  # Clearly defensible
    elif p25 * 0.7 <= proposed_rate <= p75 * 1.3:  # Rough P10-P90
        return 6  # Moderate
    else:
        return 2  # Weak


def calculate_arm_length_range(
    transaction: Transaction,
    comparables: List[Comparable] = None
) -> AnalysisResult:
    """
    Main function: validate a transfer price is arm's length.

    Input: Transaction (from_country, to_country, type, industry, amount, rate_proposed)
    Output: AnalysisResult with benchmark range + defensibility score
    """

    if comparables is None:
        comparables = load_comparables()

    # Step 1: Filter comparables
    filtered = filter_comparables(transaction, comparables)

    if not filtered:
        # No comparables found
        return AnalysisResult(
            transaction_id=transaction.id or "unknown",
            method_recommended=TPMethod.CUP,
            benchmark_range=BenchmarkRange(
                percentile_25=None,
                percentile_50=None,
                percentile_75=None,
                count_comparables=0
            ),
            proposed_rate=transaction.rate_percent,
            defensibility_score=None,
            defensibility_level=DefensibilityLevel.WEAK,
            comparables_used=[],
            risk_factors=["No comparable data found for this transaction type"],
            conclusion="Insufficient data to validate arm's length price. Manual analysis required."
        )

    # Step 2: Extract rates (depending on transaction type)
    if transaction.transaction_type.value == "royalty":
        rates = [c.royalty_rate for c in filtered if c.royalty_rate is not None]
    else:
        rates = [c.operating_margin for c in filtered if c.operating_margin is not None]

    if not rates:
        return AnalysisResult(
            transaction_id=transaction.id or "unknown",
            method_recommended=TPMethod.CUP,
            benchmark_range=BenchmarkRange(
                percentile_25=None,
                percentile_50=None,
                percentile_75=None,
                count_comparables=0
            ),
            proposed_rate=transaction.rate_percent,
            defensibility_score=None,
            defensibility_level=DefensibilityLevel.WEAK,
            comparables_used=[],
            risk_factors=["No valid rate data in comparables"],
            conclusion="Unable to calculate benchmark. Data quality issue."
        )

    # Step 3: Calculate percentiles
    percentiles = calculate_percentiles(rates)
    p25, p50, p75 = percentiles["p25"], percentiles["p50"], percentiles["p75"]

    # Step 4: Calculate defensibility score
    score = calculate_defensibility_score(transaction.rate_percent, p25, p50, p75)

    # Determine defensibility level
    if score >= 8:
        level = DefensibilityLevel.STRONG
    elif score >= 5:
        level = DefensibilityLevel.MODERATE
    else:
        level = DefensibilityLevel.WEAK

    # Step 5: Risk factors
    risk_factors = []
    if transaction.rate_percent > p75:
        risk_factors.append(f"Rate {transaction.rate_percent}% exceeds P75 ({p75}%)")
    if transaction.rate_percent < p25:
        risk_factors.append(f"Rate {transaction.rate_percent}% below P25 ({p25}%)")
    if len(filtered) < 5:
        risk_factors.append(f"Only {len(filtered)} comparables found (minimum 5 recommended)")

    # Step 6: Conclusion
    if level == DefensibilityLevel.STRONG:
        conclusion = f"This transfer price is DEFENSIBLE. Rate {transaction.rate_percent}% is within arm's length range ({p25}%-{p75}%)."
    elif level == DefensibilityLevel.MODERATE:
        conclusion = f"This transfer price is MODERATE. Rate {transaction.rate_percent}% is outside P25-P75 but within reasonable range. Requires additional documentation."
    else:
        # Distinguish between exceeds and below
        if transaction.rate_percent > p75:
            conclusion = f"This transfer price is RISKY. Rate {transaction.rate_percent}% significantly EXCEEDS benchmark ({p75}%). High audit probability."
        else:
            conclusion = f"This transfer price is RISKY. Rate {transaction.rate_percent}% significantly BELOW benchmark ({p25}%). High audit probability."

    return AnalysisResult(
        transaction_id=transaction.id or "unknown",
        method_recommended=TPMethod.CUP,
        benchmark_range=BenchmarkRange(
            percentile_25=p25,
            percentile_50=p50,
            percentile_75=p75,
            count_comparables=len(filtered)
        ),
        proposed_rate=transaction.rate_percent,
        defensibility_score=score,
        defensibility_level=level,
        comparables_used=filtered[:5],  # Show top 5
        risk_factors=risk_factors,
        conclusion=conclusion
    )
