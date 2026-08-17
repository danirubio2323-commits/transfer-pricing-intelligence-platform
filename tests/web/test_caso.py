"""La entidad `Caso`: propietario, ida y vuelta del payload, y borrado suave."""

from __future__ import annotations

import datetime as dt
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from django.db import IntegrityError
from django.db.models import ProtectedError

from apps.analisis.models import Caso
from tp_domain.calculations.arm_length_range import calculate_arm_length_range
from tp_domain.models import AnalysisResult, Industry, Transaction, TransactionType


@pytest.fixture
def resultado():
    """Un `AnalysisResult` real del motor rescatado, no un diccionario inventado.

    Se construye con la misma API que usan las 180 pruebas rescatadas: si el
    contrato del dominio cambiara, esta prueba se entera.
    """
    return calculate_arm_length_range(
        Transaction(
            description="Canon por licencia de tecnología",
            payer_country="ES",
            recipient_country="DE",
            transaction_type=TransactionType.ROYALTY,
            industry=Industry.SOFTWARE,
            amount_eur=Decimal("1000000"),
            rate_percent=Decimal("8.0"),
            effective_date=dt.date(2026, 1, 1),
        )
    )


@pytest.mark.django_db
def test_el_payload_va_y_vuelve_por_el_modelo_de_dominio(usuario, resultado):
    """Nada lee claves sueltas del JSON: se rehidrata y se valida."""
    caso = Caso.objects.create(
        usuario=usuario, titulo="Canon ES-DE", payload=resultado.model_dump(mode="json")
    )

    recuperado = AnalysisResult.model_validate(Caso.objects.get(pk=caso.pk).payload)

    assert recuperado.engine_version == resultado.engine_version


@pytest.mark.django_db
def test_los_campos_desnormalizados_se_derivan_al_guardar(usuario, resultado):
    """Se derivan del payload, nunca al revés: así no pueden contradecirlo."""
    caso = Caso.objects.create(
        usuario=usuario, titulo="Derivación", payload=resultado.model_dump(mode="json")
    )

    assert caso.engine_version == resultado.engine_version
    assert caso.dataset_version == resultado.dataset_version
    assert caso.has_ai_explanation is False


@pytest.mark.django_db
def test_un_caso_sin_propietario_no_se_guarda(resultado):
    """`usuario_id` es NOT NULL: un caso sin dueño no es aislable de nadie.

    Se afirma `IntegrityError` y no `Exception` a secas: la restricción tiene que
    venir de la base de datos, no de que el ORM tropiece por otro motivo.
    """
    with pytest.raises(IntegrityError):
        Caso.objects.create(titulo="Huérfano", payload=resultado.model_dump(mode="json"))


@pytest.mark.django_db
def test_el_borrado_suave_lo_oculta_del_gestor_por_defecto(usuario, resultado):
    caso = Caso.objects.create(
        usuario=usuario, titulo="A borrar", payload=resultado.model_dump(mode="json")
    )

    caso.deleted_at = datetime.now(UTC)
    caso.save()

    assert not Caso.objects.filter(pk=caso.pk).exists()
    assert Caso.todos.filter(pk=caso.pk).exists()


@pytest.mark.django_db
def test_borrar_un_usuario_con_casos_esta_protegido(usuario, resultado):
    """Borrar la cuenta no puede llevarse por delante sus análisis en silencio."""
    Caso.objects.create(
        usuario=usuario, titulo="Con dueño", payload=resultado.model_dump(mode="json")
    )

    with pytest.raises(ProtectedError):
        usuario.delete()

    assert Caso.todos.count() == 1
