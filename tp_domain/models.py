"""
Transfer Pricing Domain Models.

Vocabulario del dominio de TPIP. Este módulo define QUÉ existe; las políticas
(qué regla aplica cada jurisdicción, qué fuentes justifican qué) viven en
`tp_domain/rules/` y `tp_domain/sources.py`.

Alcance de Fase 1: cánones / intangibles. Los demás tipos de operación se
rechazan en validación — ver `SUPPORTED_TRANSACTION_TYPES`.
"""

from __future__ import annotations

import datetime as dt
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# Versión del motor. Viaja dentro de cada AnalysisResult: un análisis emitido
# hoy debe poder reproducirse mañana sabiendo con qué lógica se generó.
ENGINE_VERSION = "0.2.0"


# ===========================================================================
# ENUMS
# ===========================================================================

class TransactionType(str, Enum):
    """Tipos de operación vinculada."""
    ROYALTY = "royalty"
    DIVIDEND = "dividend"
    LOAN_INTEREST = "loan_interest"
    MANAGEMENT_FEE = "management_fee"
    COST_ALLOCATION = "cost_allocation"


#: Alcance de la Fase 1. Los servicios intragrupo (`MANAGEMENT_FEE`) están
#: deliberadamente fuera: compararlos contra el margen operativo del dataset
#: produce veredictos sin significado económico (un 5% —el safe harbour de la
#: OCDE para servicios de bajo valor añadido— salía clasificado como riesgo
#: alto). Vuelven en Fase 2 con su propia rama de cálculo.
SUPPORTED_TRANSACTION_TYPES = frozenset({TransactionType.ROYALTY})


class Industry(str, Enum):
    """Industrias cubiertas por el dataset de comparables."""
    PHARMACEUTICAL = "pharmaceutical"
    SOFTWARE = "software"
    MANUFACTURING = "manufacturing"


class TPMethod(str, Enum):
    """Los 5 métodos de precios de transferencia de la OCDE."""
    CUP = "cup"
    RESALE_PRICE = "resale_price"
    COST_PLUS = "cost_plus"
    PROFIT_SPLIT = "profit_split"
    TNMM = "tnmm"


class DefensibilityLevel(str, Enum):
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"


class RangePosition(str, Enum):
    """Dónde cae el tipo propuesto respecto del rango de comparables."""
    BELOW_P10 = "below_p10"
    P10_TO_P25 = "p10_to_p25"
    WITHIN_IQR = "within_iqr"
    P75_TO_P90 = "p75_to_p90"
    ABOVE_P90 = "above_p90"


class RangeRule(str, Enum):
    """
    Regla estadística que impone (o no) una jurisdicción sobre el rango.

    Vocabulario; el mapa país -> regla vive en `tp_domain/rules/`.
    """
    #: La ley no contiene regla estadística. Caso español (Art. 18.4 LIS).
    NO_STATUTORY_RULE = "no_statutory_rule"
    #: Rango intercuartílico obligatorio y ajuste a la mediana. Caso alemán
    #: (§1.3a AStG).
    INTERQUARTILE_MEDIAN_ADJUSTMENT = "interquartile_median_adjustment"
    #: Jurisdicción no modelada en esta versión. No se asume la regla de
    #: ningún otro país: se dice que no se sabe.
    NOT_MODELLED = "not_modelled"


class PartyRole(str, Enum):
    PAYER = "payer"
    RECIPIENT = "recipient"


class SourceKind(str, Enum):
    LEGISLATION = "legislation"
    GUIDELINES = "guidelines"
    CASE_LAW = "case_law"
    DATASET = "dataset"


class RejectionReason(str, Enum):
    INDUSTRY_MISMATCH = "industry_mismatch"
    STALE_YEAR = "stale_year"
    NO_RATE_DATA = "no_rate_data"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class RiskCode(str, Enum):
    RATE_ABOVE_RANGE = "rate_above_range"
    RATE_BELOW_RANGE = "rate_below_range"
    THIN_SAMPLE = "thin_sample"
    SYNTHETIC_DATA = "synthetic_data"
    JURISDICTION_NOT_MODELLED = "jurisdiction_not_modelled"
    MANDATORY_ADJUSTMENT = "mandatory_adjustment"
    NO_COMPARABLES = "no_comparables"


# ===========================================================================
# FUENTES
# ===========================================================================

class Source(BaseModel):
    """
    Una fuente citable. El registro cerrado vive en `tp_domain/sources.py`.

    Existe para que la capa de IA no pueda inventar citas: solo puede
    referenciar entradas emitidas por el motor (regla de gobernanza §3.2).
    """
    model_config = ConfigDict(frozen=True)

    id: str
    kind: SourceKind
    citation: str
    pinpoint: Optional[str] = None
    official_ref: Optional[str] = None
    research_note: Optional[str] = None
    disclaimer: Optional[str] = None


# ===========================================================================
# COMPARABLES
# ===========================================================================

class Comparable(BaseModel):
    """Una observación de mercado del dataset de referencia."""

    id: str
    company_name: str
    country: str
    industry: Industry
    royalty_rate: Optional[float] = None
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    data_year: int
    source: str = "OECD"


class RejectedComparable(BaseModel):
    """
    Un comparable descartado y por qué.

    El anexo de aceptados y rechazados es lo que distingue un estudio de
    benchmarking de una media aritmética.
    """
    comparable_id: str
    company_name: str
    reason: RejectionReason
    detail: str


class ComparableDataset(BaseModel):
    """Dataset cargado, con su versión, para trazabilidad del análisis."""
    version: str
    comparables: List[Comparable]


# ===========================================================================
# TRANSACCIÓN
# ===========================================================================

class Transaction(BaseModel):
    """Una operación vinculada a analizar."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "description": "Canon por licencia de tecnología",
                "payer_country": "ES",
                "recipient_country": "DE",
                "transaction_type": "royalty",
                "industry": "software",
                "amount_eur": "1000000",
                "rate_percent": "12.0",
                "effective_date": "2026-01-01",
            }
        }
    )

    id: Optional[str] = None
    description: str = Field(..., min_length=1)

    #: Quién paga el canon y deduce el gasto.
    payer_country: str = Field(..., min_length=2, max_length=2)
    #: Quién percibe el canon.
    recipient_country: str = Field(..., min_length=2, max_length=2)

    transaction_type: TransactionType
    industry: Industry

    # Decimal en lo que se imprime en un informe. Los percentiles siguen en
    # float: la frontera de conversión está en el motor de cálculo.
    amount_eur: Decimal = Field(..., gt=0)
    rate_percent: Decimal = Field(..., ge=0, le=100)

    #: Obligatoria y sin valor por defecto: no existe un análisis "de hoy".
    effective_date: dt.date

    method_hint: Optional[TPMethod] = None

    @field_validator("payer_country", "recipient_country")
    @classmethod
    def _upper(cls, v: str) -> str:
        return v.upper()

    @field_validator("transaction_type")
    @classmethod
    def _supported_only(cls, v: TransactionType) -> TransactionType:
        if v not in SUPPORTED_TRANSACTION_TYPES:
            supported = ", ".join(sorted(t.value for t in SUPPORTED_TRANSACTION_TYPES))
            raise ValueError(
                f"Tipo de operación '{v.value}' no soportado en esta versión. "
                f"Fase 1 cubre únicamente: {supported}."
            )
        return v

    @model_validator(mode="after")
    def _countries_differ(self) -> "Transaction":
        if self.payer_country == self.recipient_country:
            raise ValueError(
                "Una operación vinculada transfronteriza requiere dos "
                "jurisdicciones distintas."
            )
        return self


# ===========================================================================
# RESULTADO
# ===========================================================================

class BenchmarkRange(BaseModel):
    """
    Rango de plena competencia. Es un hecho de mercado: no tiene nacionalidad.

    Los cinco percentiles son None cuando no hay comparables suficientes.
    """
    percentile_10: Optional[float] = None
    percentile_25: Optional[float] = None
    percentile_50: Optional[float] = None
    percentile_75: Optional[float] = None
    percentile_90: Optional[float] = None
    count_accepted: int = 0
    #: Convención de cálculo. La OCDE no impone una; dejarla implícita sería
    #: una decisión metodológica sin dueño.
    percentile_method: str = "linear interpolation (numpy default)"


class JurisdictionAssessment(BaseModel):
    """
    Veredicto de UNA jurisdicción sobre la operación.

    Un análisis produce tantos como jurisdicciones implicadas: cada
    administración aplica su propia regla a su propio lado de la operación.
    """
    country: str
    role: PartyRole
    range_rule: RangeRule
    position: Optional[RangePosition] = None
    defensibility_level: DefensibilityLevel
    defensibility_score: Optional[int] = Field(None, ge=1, le=10)
    #: Tipo al que la jurisdicción ajustaría de oficio, si su regla lo impone.
    adjusted_rate: Optional[float] = None
    consequence: str
    source_ids: List[str] = Field(default_factory=list)


class RiskFactor(BaseModel):
    code: RiskCode
    severity: Severity
    message: str
    source_ids: List[str] = Field(default_factory=list)


class AIExplanation(BaseModel):
    """
    Explicación redactada por IA sobre un resultado YA calculado.

    `sources_cited` se valida contra el registro del propio análisis en
    `AnalysisResult`: si la IA cita algo que el motor no emitió, el resultado
    no se construye. La gobernanza deja de ser una instrucción en un prompt y
    pasa a ser una restricción del modelo.
    """
    text: str
    prompt_version: str
    model: str
    generated_at: dt.datetime = Field(default_factory=dt.datetime.now)
    sources_cited: List[str] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    """Resultado completo. Se basta solo: el PDF y la IA no consultan nada más."""

    analysis_id: str
    created_at: dt.datetime = Field(default_factory=dt.datetime.now)
    engine_version: str = ENGINE_VERSION
    dataset_version: str

    transaction: Transaction

    method_applied: TPMethod
    method_rationale: str

    benchmark: BenchmarkRange
    comparables_accepted: List[Comparable] = Field(default_factory=list)
    comparables_rejected: List[RejectedComparable] = Field(default_factory=list)

    assessments: List[JurisdictionAssessment] = Field(default_factory=list)
    risk_factors: List[RiskFactor] = Field(default_factory=list)
    sources: List[Source] = Field(default_factory=list)

    #: Redacción determinista. Siempre presente: el informe se genera sin IA.
    conclusion: str
    #: Aditiva. Su ausencia no degrada el informe.
    ai_explanation: Optional[AIExplanation] = None

    @model_validator(mode="after")
    def _every_cited_source_exists(self) -> "AnalysisResult":
        known = {s.id for s in self.sources}

        for assessment in self.assessments:
            unknown = set(assessment.source_ids) - known
            if unknown:
                raise ValueError(
                    f"Assessment de {assessment.country} cita fuentes no "
                    f"emitidas por el motor: {sorted(unknown)}"
                )

        for factor in self.risk_factors:
            unknown = set(factor.source_ids) - known
            if unknown:
                raise ValueError(
                    f"Factor de riesgo '{factor.code.value}' cita fuentes no "
                    f"emitidas por el motor: {sorted(unknown)}"
                )

        if self.ai_explanation is not None:
            unknown = set(self.ai_explanation.sources_cited) - known
            if unknown:
                raise ValueError(
                    "La explicación de IA cita fuentes que el motor no emitió: "
                    f"{sorted(unknown)}. Toda cita debe proceder del registro "
                    "del análisis."
                )

        return self
