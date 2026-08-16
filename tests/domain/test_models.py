"""
Tests de validación del modelo de dominio.

Fijan el contrato de entrada: qué se acepta, qué se rechaza y por qué. La
mayoría de estos casos antes pasaban silenciosamente y producían resultados
sin significado.
"""

import datetime as dt
from decimal import Decimal

import pytest
from pydantic import ValidationError

from tests.domain.conftest import REF_DATE, make_transaction
from tp_domain.models import (
    SUPPORTED_TRANSACTION_TYPES,
    AIExplanation,
    AnalysisResult,
    BenchmarkRange,
    DefensibilityLevel,
    Industry,
    JurisdictionAssessment,
    LocatorType,
    PartyRole,
    RangeRule,
    RiskCode,
    RiskFactor,
    Severity,
    Source,
    SourceKind,
    TPMethod,
    Transaction,
    TransactionType,
)
from tp_domain.sources import SOURCE_REGISTRY, resolve


# ---------------------------------------------------------------------------
# Alcance de Fase 1
# ---------------------------------------------------------------------------

def test_only_royalty_is_supported_in_phase_1():
    assert SUPPORTED_TRANSACTION_TYPES == {TransactionType.ROYALTY}


@pytest.mark.parametrize("ttype", [
    "management_fee", "dividend", "loan_interest", "cost_allocation",
])
def test_unsupported_transaction_types_are_rejected(ttype):
    """
    Regresión de la v0.1: `management_fee` comparaba un margen sobre costes
    contra el margen operativo del dataset y clasificaba el safe harbour del
    5% de la OCDE como riesgo alto. Bloquear es preferible a responder mal.
    """
    with pytest.raises(ValidationError, match="no soportado"):
        make_transaction(ttype=ttype)


def test_royalty_is_accepted():
    assert make_transaction(ttype="royalty").transaction_type is TransactionType.ROYALTY


# ---------------------------------------------------------------------------
# Validación de la transacción
# ---------------------------------------------------------------------------

def test_unknown_industry_is_a_validation_error():
    """Antes devolvía un análisis vacío; ahora no se puede ni construir."""
    with pytest.raises(ValidationError):
        make_transaction(industry="biotech")


def test_same_country_both_sides_is_rejected():
    with pytest.raises(ValidationError, match="jurisdicciones distintas"):
        make_transaction(payer="ES", recipient="ES")


def test_country_codes_are_normalised_to_upper():
    t = make_transaction(payer="es", recipient="de")
    assert (t.payer_country, t.recipient_country) == ("ES", "DE")


@pytest.mark.parametrize("rate", [-1, 150])
def test_rate_out_of_bounds_is_rejected(rate):
    with pytest.raises(ValidationError):
        make_transaction(rate=rate)


def test_zero_amount_is_rejected():
    with pytest.raises(ValidationError):
        Transaction(
            description="x", payer_country="ES", recipient_country="DE",
            transaction_type="royalty", industry="software",
            amount_eur=Decimal("0"), rate_percent=Decimal("5"),
            effective_date=REF_DATE,
        )


def test_effective_date_has_no_default():
    """Sin valor por defecto: no existe un análisis 'de hoy' implícito."""
    with pytest.raises(ValidationError):
        Transaction(
            description="x", payer_country="ES", recipient_country="DE",
            transaction_type="royalty", industry="software",
            amount_eur=Decimal("1000"), rate_percent=Decimal("5"),
        )


def test_amount_and_rate_are_decimal():
    t = make_transaction(rate=12.5)
    assert isinstance(t.amount_eur, Decimal)
    assert isinstance(t.rate_percent, Decimal)


def test_effective_date_is_a_date_not_datetime():
    t = make_transaction()
    assert isinstance(t.effective_date, dt.date)
    assert t.effective_date == REF_DATE


# ---------------------------------------------------------------------------
# Registro de fuentes
# ---------------------------------------------------------------------------

def test_source_registry_has_the_five_phase_1_sources():
    assert set(SOURCE_REGISTRY) == {
        "es-lis-art18-4", "de-astg-1-3a", "oecd-tpg-2022-cap3",
        "oecd-tpg-2022-cap6", "tpip-dataset-v1",
    }


def test_dataset_source_carries_a_synthetic_data_disclaimer():
    """El origen sintético de los comparables no puede quedar sin declarar."""
    disclaimer = SOURCE_REGISTRY["tpip-dataset-v1"].disclaimer
    assert disclaimer and "SINTÉTICOS" in disclaimer


def test_every_source_points_to_its_research_note():
    for source in SOURCE_REGISTRY.values():
        assert source.research_note.startswith("documentation/tax-research/")


def test_resolve_rejects_unknown_ids():
    with pytest.raises(KeyError, match="Fuente desconocida"):
        resolve(["esto-no-existe"])


def test_resolve_deduplicates_preserving_order():
    got = resolve(["de-astg-1-3a", "es-lis-art18-4", "de-astg-1-3a"])
    assert [s.id for s in got] == ["de-astg-1-3a", "es-lis-art18-4"]


# ---------------------------------------------------------------------------
# Trazabilidad jurídica de las fuentes (Fase 1: jurisdiction, locator,
# verificación). Ampliación de `Source` sobre el registro cerrado que ya
# exigía sources_cited ⊆ SOURCE_REGISTRY — estos campos son los que permiten
# distinguir una fuente verificada contra su texto primario de una que no.
# ---------------------------------------------------------------------------

def test_every_source_has_jurisdiction_locator_and_verification_date():
    for source in SOURCE_REGISTRY.values():
        assert source.jurisdiction
        assert source.locator_type is not None
        assert source.locator
        assert source.verified_at is not None


def test_only_the_dataset_source_lacks_verification_confidence():
    """
    Las 4 fuentes legales tienen que declarar si se verificaron contra el
    texto primario o mediante lectura dirigida. El dataset sintético no es
    una fuente jurídica que verificar de esa forma — su honestidad la da el
    disclaimer, no este campo.
    """
    for source_id, source in SOURCE_REGISTRY.items():
        if source.kind is SourceKind.DATASET:
            assert source.verification_confidence is None, source_id
        else:
            assert source.verification_confidence is not None, source_id


def test_offline_source_without_quote_is_rejected():
    with pytest.raises(ValidationError, match="quote"):
        Source(
            id="test-offline-no-quote", kind=SourceKind.LEGISLATION,
            citation="Norma de prueba", jurisdiction="ES",
            locator_type=LocatorType.OFFLINE, locator="raw/test.pdf",
            verified_at=REF_DATE, disclaimer="Sin localizador público.",
        )


def test_offline_source_without_disclaimer_is_rejected():
    with pytest.raises(ValidationError, match="disclaimer"):
        Source(
            id="test-offline-no-disclaimer", kind=SourceKind.LEGISLATION,
            citation="Norma de prueba", jurisdiction="ES",
            locator_type=LocatorType.OFFLINE, locator="raw/test.pdf",
            verified_at=REF_DATE, quote="Texto literal de prueba.",
        )


def test_offline_source_with_quote_and_disclaimer_is_accepted():
    source = Source(
        id="test-offline-ok", kind=SourceKind.LEGISLATION,
        citation="Norma de prueba", jurisdiction="ES",
        locator_type=LocatorType.OFFLINE, locator="raw/test.pdf",
        verified_at=REF_DATE, quote="Texto literal de prueba.",
        disclaimer="Sin localizador público.",
    )
    assert source.quote and source.disclaimer


def test_dataset_kind_is_exempt_from_the_offline_quote_requirement():
    """
    El dataset sintético usa locator_type OFFLINE (no tiene identificador
    público) pero no es una disposición jurídica con extracto que citar — el
    validador lo exime explícitamente de exigir quote/disclaimer.
    """
    source = Source(
        id="test-dataset-offline", kind=SourceKind.DATASET,
        citation="Dataset de prueba", jurisdiction="GLOBAL",
        locator_type=LocatorType.OFFLINE, locator="tp_domain/test.json",
        verified_at=REF_DATE,
    )
    assert source.quote is None and source.disclaimer is None


def test_non_offline_source_does_not_require_quote_or_disclaimer():
    source = Source(
        id="test-boe-id", kind=SourceKind.LEGISLATION,
        citation="Norma de prueba", jurisdiction="ES",
        locator_type=LocatorType.BOE_ID, locator="BOE-A-9999-99999",
        verified_at=REF_DATE,
    )
    assert source.quote is None and source.disclaimer is None


def test_source_validity_fields_default_to_none():
    """Ninguna de las 5 fuentes de Fase 1 tiene vigencia cerrada ni sucesora."""
    for source in SOURCE_REGISTRY.values():
        assert source.in_force_from is None
        assert source.in_force_to is None
        assert source.superseded_by is None


# ---------------------------------------------------------------------------
# Gobernanza: la IA no puede citar lo que el motor no emitió
# ---------------------------------------------------------------------------

def _minimal_result(**overrides) -> dict:
    base = dict(
        analysis_id="TPIP-TEST",
        dataset_version="1.0",
        transaction=make_transaction(),
        method_applied=TPMethod.CUP,
        method_rationale="test",
        benchmark=BenchmarkRange(count_accepted=0),
        sources=resolve(["es-lis-art18-4"]),
        conclusion="test",
    )
    base.update(overrides)
    return base


def test_ai_explanation_citing_a_known_source_is_accepted():
    result = AnalysisResult(**_minimal_result(
        ai_explanation=AIExplanation(
            text="…", prompt_version="explain_analysis_v1",
            model="claude-test", sources_cited=["es-lis-art18-4"],
        )
    ))
    assert result.ai_explanation.sources_cited == ["es-lis-art18-4"]


def test_ai_explanation_citing_an_unemitted_source_is_rejected():
    """
    La regla de gobernanza §3.2 como restricción del modelo, no como
    instrucción en un prompt: si la IA cita una fuente que el motor no emitió,
    el resultado no llega a construirse.
    """
    with pytest.raises(ValidationError, match="no emitió"):
        AnalysisResult(**_minimal_result(
            ai_explanation=AIExplanation(
                text="Según el §1.3a AStG…", prompt_version="explain_analysis_v1",
                model="claude-test", sources_cited=["de-astg-1-3a"],
            )
        ))


def test_assessment_citing_an_unemitted_source_is_rejected():
    with pytest.raises(ValidationError, match="no emitidas"):
        AnalysisResult(**_minimal_result(
            assessments=[JurisdictionAssessment(
                country="DE", role=PartyRole.RECIPIENT,
                range_rule=RangeRule.INTERQUARTILE_MEDIAN_ADJUSTMENT,
                defensibility_level=DefensibilityLevel.WEAK,
                consequence="…", source_ids=["de-astg-1-3a"],
            )]
        ))


def test_risk_factor_citing_an_unemitted_source_is_rejected():
    with pytest.raises(ValidationError, match="no emitidas"):
        AnalysisResult(**_minimal_result(
            risk_factors=[RiskFactor(
                code=RiskCode.THIN_SAMPLE, severity=Severity.WARNING,
                message="…", source_ids=["tpip-dataset-v1"],
            )]
        ))
