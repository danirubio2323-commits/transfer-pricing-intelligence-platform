"""El formulario produce un `Transaction` del dominio, o errores legibles.

Lo que se comprueba aquí no es que Django valide, sino que **el dominio sigue
siendo quien decide** y que su veredicto llega al usuario en un solo lenguaje.
"""

from __future__ import annotations

import pytest

from apps.analisis.forms import OPCIONES_TIPO, CasoForm
from tp_domain.models import Transaction

VALIDO = {
    "titulo": "",
    "description": "Canon por licencia de tecnología",
    "payer_country": "ES",
    "recipient_country": "DE",
    "transaction_type": "royalty",
    "industry": "software",
    "amount_eur": "1000000",
    "rate_percent": "8.0",
    "effective_date": "2026-01-01",
}


def _con(**cambios):
    return {**VALIDO, **cambios}


def test_un_envio_valido_produce_un_transaction_del_dominio():
    formulario = CasoForm(data=VALIDO)

    assert formulario.is_valid(), formulario.errors
    assert isinstance(formulario.cleaned_data["transaction"], Transaction)


def test_dos_jurisdicciones_iguales_es_un_error_del_modelo_entero():
    """No es un fallo de un campo: es una condición sobre la operación completa."""
    formulario = CasoForm(data=_con(recipient_country="ES"))

    assert not formulario.is_valid()
    assert any("jurisdicciones distintas" in e for e in formulario.non_field_errors()), (
        formulario.errors
    )


def test_el_desplegable_no_ofrece_tipos_que_el_motor_no_calcula():
    """Los servicios intragrupo están fuera de la Fase 1: no deben poder elegirse."""
    ofrecidos = {valor for valor, _ in OPCIONES_TIPO}

    assert ofrecidos == {"royalty"}
    assert "management_fee" not in ofrecidos


def test_un_tipo_no_soportado_se_rechaza():
    formulario = CasoForm(data=_con(transaction_type="management_fee"))

    assert not formulario.is_valid()
    assert "transaction_type" in formulario.errors


@pytest.mark.parametrize(
    "campo, valor",
    [("amount_eur", "0"), ("rate_percent", "101")],
)
def test_el_error_queda_pegado_al_campo_que_lo_causa(campo, valor):
    formulario = CasoForm(data=_con(**{campo: valor}))

    assert not formulario.is_valid()
    assert campo in formulario.errors


def test_la_fecha_efectiva_es_obligatoria():
    """No existe un análisis «de hoy»: la fecha decide qué comparables entran."""
    formulario = CasoForm(data=_con(effective_date=""))

    assert not formulario.is_valid()
    assert "effective_date" in formulario.errors


def test_el_titulo_vacio_se_deriva_de_la_descripcion():
    formulario = CasoForm(data=VALIDO)

    assert formulario.is_valid(), formulario.errors
    assert formulario.cleaned_data["titulo"] == "Canon por licencia de tecnología"


def test_el_titulo_derivado_se_recorta_a_160():
    formulario = CasoForm(data=_con(description="x" * 300))

    assert formulario.is_valid(), formulario.errors
    assert len(formulario.cleaned_data["titulo"]) <= 160


@pytest.mark.django_db
def test_el_titulo_derivado_se_desambigua_si_ya_existe(usuario):
    """Sin desambiguar, el segundo caso fallaría con un error de base de datos."""
    from apps.analisis.models import Caso

    Caso.objects.create(usuario=usuario, titulo="Canon por licencia de tecnología", payload={})

    formulario = CasoForm(data=VALIDO, usuario=usuario)

    assert formulario.is_valid(), formulario.errors
    assert formulario.cleaned_data["titulo"] != "Canon por licencia de tecnología"
    assert "2026-01-01" in formulario.cleaned_data["titulo"]
