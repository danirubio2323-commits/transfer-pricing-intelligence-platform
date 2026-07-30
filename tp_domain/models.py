"""
Transfer Pricing Domain Models

This module contains the core data models for TPIP.
All business logic related to transfer pricing lives here.
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


# ============================================================================
# ENUMS (tipos fijos de datos)
# ============================================================================

class TransactionType(str, Enum):
    """Tipos de transacciones transfer pricing"""
    ROYALTY = "royalty"
    DIVIDEND = "dividend"
    LOAN_INTEREST = "loan_interest"
    MANAGEMENT_FEE = "management_fee"
    COST_ALLOCATION = "cost_allocation"


class TPMethod(str, Enum):
    """Los 5 métodos de transfer pricing según OECD"""
    CUP = "cup"  # Comparable Uncontrolled Price
    RESALE_PRICE = "resale_price"
    COST_PLUS = "cost_plus"
    PROFIT_SPLIT = "profit_split"
    TNM = "tnm"  # Transactional Net Margin Method


class DefensibilityLevel(str, Enum):
    """Nivel de defensibilidad de un precio de transferencia"""
    STRONG = "strong"  # 8-10
    MODERATE = "moderate"  # 5-7
    WEAK = "weak"  # 1-4


# ============================================================================
# COMPARABLE (datos de benchmark)
# ============================================================================

class Comparable(BaseModel):
    """Un comparable = una empresa con datos similares a la nuestra"""

    id: str
    company_name: str
    country: str
    industry: str
    royalty_rate: Optional[float] = None  # %
    gross_margin: Optional[float] = None  # %
    operating_margin: Optional[float] = None  # %
    data_year: int
    source: str = "OECD"

    class Config:
        json_schema_extra = {
            "example": {
                "id": "comp_001",
                "company_name": "Pharma Corp",
                "country": "CH",
                "industry": "pharmaceutical",
                "royalty_rate": 5.2,
                "data_year": 2024,
                "source": "OECD TP Database"
            }
        }


# ============================================================================
# TRANSACTION (la transacción que queremos analizar)
# ============================================================================

class Transaction(BaseModel):
    """Una transacción de transfer pricing que queremos validar"""

    # Identificación
    id: Optional[str] = None
    description: str = Field(..., description="Descripción de la transacción")

    # Participantes
    from_country: str = Field(..., description="País origen (ej: 'ES')")
    to_country: str = Field(..., description="País destino (ej: 'LU')")

    # Tipo de transacción
    transaction_type: TransactionType = Field(..., description="Tipo: royalty, dividend, etc.")
    industry: str = Field(..., description="Industry: pharmaceutical, software, manufacturing")

    # Datos económicos
    amount_eur: float = Field(..., gt=0, description="Monto en EUR")
    rate_percent: float = Field(..., ge=0, le=100, description="Tasa propuesta (%)")
    effective_date: datetime = Field(default_factory=datetime.now, description="Fecha efectiva")

    # TP Methodology
    method_hint: Optional[TPMethod] = Field(None, description="Sugerencia de método (opcional)")

    class Config:
        json_schema_extra = {
            "example": {
                "description": "Pago de royalty por licencia de patente",
                "from_country": "ES",
                "to_country": "LU",
                "transaction_type": "royalty",
                "industry": "software",
                "amount_eur": 1000000,
                "rate_percent": 12.0,
                "effective_date": "2024-01-01"
            }
        }


# ============================================================================
# BENCHMARK RESULT (resultado del análisis)
# ============================================================================

class BenchmarkRange(BaseModel):
    """El rango de precios arm's length según comparables"""

    # Optional: son None cuando no se encuentran comparables para la transacción.
    # La UI comprueba `percentile_25 is None` para mostrar el caso "sin datos".
    percentile_25: Optional[float] = None
    percentile_50: Optional[float] = None  # mediana
    percentile_75: Optional[float] = None
    count_comparables: int

    class Config:
        json_schema_extra = {
            "example": {
                "percentile_25": 4.5,
                "percentile_50": 6.1,
                "percentile_75": 8.2,
                "count_comparables": 23
            }
        }


class AnalysisResult(BaseModel):
    """El resultado completo del análisis de una transacción"""

    transaction_id: str
    method_recommended: TPMethod
    benchmark_range: BenchmarkRange
    proposed_rate: float
    # Optional: es None cuando no hay comparables suficientes para puntuar.
    defensibility_score: Optional[int] = Field(None, ge=1, le=10, description="1-10, donde 10 es muy defensible")
    defensibility_level: DefensibilityLevel
    comparables_used: List[Comparable]
    risk_factors: List[str] = Field(default_factory=list)
    conclusion: str
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "tx_001",
                "method_recommended": "cup",
                "benchmark_range": {
                    "percentile_25": 4.5,
                    "percentile_50": 6.1,
                    "percentile_75": 8.2,
                    "count_comparables": 23
                },
                "proposed_rate": 12.0,
                "defensibility_score": 4,
                "defensibility_level": "weak",
                "risk_factors": [
                    "Rate exceeds 90th percentile",
                    "Only 3 recent comparables found"
                ],
                "conclusion": "This transfer price is RISKY and likely to be challenged in audit."
            }
        }
