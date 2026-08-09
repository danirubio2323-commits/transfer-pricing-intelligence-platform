"""
Contratos de la capa de IA.

Dos esquemas y una regla de diseño:

- `ExplanationRequest` es lo ÚNICO que ve el modelo. Es una proyección cerrada
  del `AnalysisResult`, no el objeto entero. Lo que no entra, no se puede
  alucinar: fuera quedan los comparables (material para inventar observaciones
  concretas) y las rutas internas de las fichas de investigación.

- `ExplanationDraft` es lo que el modelo devuelve. Es un borrador, no una
  explicación: solo se convierte en `AIExplanation` después de pasar por
  `ai.validators.validate_draft`.

El nombre importa. Mientras es `Draft` no puede adjuntarse a un resultado.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from tp_domain.models import AnalysisResult

PROMPT_VERSION = "explain_analysis_v1"


# ---------------------------------------------------------------------------
# Entrada
# ---------------------------------------------------------------------------

class AllowedSource(BaseModel):
    """Fuente citable, tal y como la ve el modelo."""
    model_config = ConfigDict(frozen=True)

    id: str
    citation: str
    pinpoint: Optional[str] = None


class TransactionBrief(BaseModel):
    description: str
    industry: str
    payer_country: str
    recipient_country: str
    amount_eur: str
    rate_percent: float


class BenchmarkBrief(BaseModel):
    percentile_10: Optional[float] = None
    percentile_25: Optional[float] = None
    percentile_50: Optional[float] = None
    percentile_75: Optional[float] = None
    percentile_90: Optional[float] = None
    count_accepted: int
    count_rejected: int
    percentile_method: str


class AssessmentBrief(BaseModel):
    country: str
    role: str
    range_rule: str
    defensibility_level: str
    defensibility_score: Optional[int] = None
    adjusted_rate: Optional[float] = None
    consequence: str
    source_ids: List[str] = Field(default_factory=list)


class RiskFactorBrief(BaseModel):
    severity: str
    message: str


class ExplanationRequest(BaseModel):
    """Payload que se envía al modelo. Nada más sale del sistema."""

    analysis_id: str
    method: str
    method_rationale: str
    transaction: TransactionBrief
    benchmark: BenchmarkBrief
    position: Optional[str] = None
    assessments: List[AssessmentBrief] = Field(default_factory=list)
    risk_factors: List[RiskFactorBrief] = Field(default_factory=list)
    engine_conclusion: str
    allowed_sources: List[AllowedSource] = Field(default_factory=list)

    @classmethod
    def from_result(cls, result: AnalysisResult) -> "ExplanationRequest":
        t = result.transaction
        b = result.benchmark
        position = result.assessments[0].position if result.assessments else None

        return cls(
            analysis_id=result.analysis_id,
            method=result.method_applied.value,
            method_rationale=result.method_rationale,
            transaction=TransactionBrief(
                description=t.description,
                industry=t.industry.value,
                payer_country=t.payer_country,
                recipient_country=t.recipient_country,
                amount_eur=f"{t.amount_eur:.2f}",
                rate_percent=float(t.rate_percent),
            ),
            benchmark=BenchmarkBrief(
                percentile_10=b.percentile_10,
                percentile_25=b.percentile_25,
                percentile_50=b.percentile_50,
                percentile_75=b.percentile_75,
                percentile_90=b.percentile_90,
                count_accepted=b.count_accepted,
                count_rejected=len(result.comparables_rejected),
                percentile_method=b.percentile_method,
            ),
            position=position.value if position else None,
            assessments=[
                AssessmentBrief(
                    country=a.country,
                    role=a.role.value,
                    range_rule=a.range_rule.value,
                    defensibility_level=a.defensibility_level.value,
                    defensibility_score=a.defensibility_score,
                    adjusted_rate=a.adjusted_rate,
                    consequence=a.consequence,
                    source_ids=list(a.source_ids),
                )
                for a in result.assessments
            ],
            risk_factors=[
                RiskFactorBrief(severity=f.severity.value, message=f.message)
                for f in result.risk_factors
            ],
            engine_conclusion=result.conclusion,
            # Registro CERRADO. El validador comprueba contra esta misma lista.
            allowed_sources=[
                AllowedSource(id=s.id, citation=s.citation, pinpoint=s.pinpoint)
                for s in result.sources
            ],
        )

    @property
    def allowed_source_ids(self) -> set:
        return {s.id for s in self.allowed_sources}


# ---------------------------------------------------------------------------
# Salida
# ---------------------------------------------------------------------------

class ExplanationDraft(BaseModel):
    """
    Lo que devuelve el modelo, todavía sin validar.

    Deliberadamente NO es un `AIExplanation`: un borrador no puede adjuntarse a
    un `AnalysisResult` hasta que `validate_draft` lo promueva.
    """
    model_config = ConfigDict(extra="forbid")

    narrative: str = Field(..., min_length=1)
    sources_cited: List[str] = Field(default_factory=list)
