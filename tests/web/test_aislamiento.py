"""Aislamiento por propietario. Sin esto el producto no es publicable.

La propiedad que se comprueba no es «A no ve lo de B», sino algo más fuerte: **A
no puede distinguir un caso de B de un caso que no existe**. Por eso todo
responde 404 y nunca 403 — un 403 confirmaría que ese identificador es real.

Las rutas HTTP se añaden a este fichero según nacen: el detalle en el paso 11,
el informe en el 14 y el listado en el 15. La guarda se prueba directamente, y
cada ruta que aparece se añade aquí con su caso cruzado.
"""

from __future__ import annotations

import datetime as dt
import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from django.http import Http404

from apps.analisis.models import Caso
from apps.comun.consultas import casos_de
from apps.comun.guardas import caso_del_usuario
from tp_domain.calculations.arm_length_range import calculate_arm_length_range
from tp_domain.models import Industry, Transaction, TransactionType


def _payload():
    resultado = calculate_arm_length_range(
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
    return resultado.model_dump(mode="json")


@pytest.fixture
def caso_de_otro(otro_usuario):
    return Caso.objects.create(usuario=otro_usuario, titulo="Ajeno", payload=_payload())


@pytest.mark.django_db
def test_el_caso_propio_se_recupera(usuario):
    caso = Caso.objects.create(usuario=usuario, titulo="Propio", payload=_payload())

    assert caso_del_usuario(usuario, caso.pk).pk == caso.pk


@pytest.mark.django_db
def test_el_caso_ajeno_responde_404_y_no_403(usuario, caso_de_otro):
    """Un 403 confirmaría que ese identificador existe y es de otra persona."""
    with pytest.raises(Http404):
        caso_del_usuario(usuario, caso_de_otro.pk)


@pytest.mark.django_db
def test_un_identificador_inexistente_responde_igual(usuario, caso_de_otro):
    """Indistinguible del caso anterior: esa es toda la propiedad."""
    inexistente = uuid.uuid4()

    with pytest.raises(Http404):
        caso_del_usuario(usuario, inexistente)


@pytest.mark.django_db
def test_un_caso_propio_borrado_en_suave_tambien_responde_404(usuario):
    caso = Caso.objects.create(usuario=usuario, titulo="Borrado", payload=_payload())
    caso.deleted_at = datetime.now(UTC)
    caso.save()

    with pytest.raises(Http404):
        caso_del_usuario(usuario, caso.pk)


@pytest.mark.django_db
def test_el_listado_solo_devuelve_los_propios(usuario, otro_usuario):
    Caso.objects.create(usuario=usuario, titulo="Mío", payload=_payload())
    Caso.objects.create(usuario=otro_usuario, titulo="Suyo", payload=_payload())

    mios = list(casos_de(usuario))

    assert len(mios) == 1
    assert mios[0].titulo == "Mío"


@pytest.mark.django_db
def test_el_informe_de_un_caso_ajeno_no_se_genera_siquiera(client, usuario, caso_de_otro):
    """La guarda corta antes de invocar al generador: no se produce un PDF que
    luego se descarte, no llega a existir."""
    from django.urls import reverse

    client.force_login(usuario)

    respuesta = client.get(reverse("analisis:informe", kwargs={"pk": caso_de_otro.pk}))

    assert respuesta.status_code == 404
