"""Utilidades compartidas por los tests de dominio."""

import datetime as dt
from decimal import Decimal

import pytest

from tp_domain.calculations.arm_length_range import load_dataset
from tp_domain.models import Comparable, Industry, Transaction

#: Fecha fija en todas las transacciones de test. Nunca `date.today()`: la
#: suite no debe empezar a fallar el 1 de enero de un año cualquiera.
REF_DATE = dt.date(2026, 1, 1)


@pytest.fixture(scope="session")
def dataset():
    return load_dataset()


@pytest.fixture(scope="session")
def comparables(dataset):
    return dataset.comparables


def make_transaction(
    industry: str = "software",
    rate: float = 10.0,
    payer: str = "ES",
    recipient: str = "DE",
    ttype: str = "royalty",
    effective_date: dt.date = REF_DATE,
) -> Transaction:
    return Transaction(
        description="Operación de test",
        payer_country=payer,
        recipient_country=recipient,
        transaction_type=ttype,
        industry=industry,
        amount_eur=Decimal("1000000"),
        rate_percent=Decimal(str(rate)),
        effective_date=effective_date,
    )


def make_comparable(
    cid: str,
    industry: str = "software",
    rate: float = 9.0,
    year: int = 2025,
    country: str = "DE",
) -> Comparable:
    return Comparable(
        id=cid,
        company_name=f"Test {cid}",
        country=country,
        industry=Industry(industry),
        royalty_rate=rate,
        gross_margin=50.0,
        operating_margin=15.0,
        data_year=year,
        source="unit-test",
    )
