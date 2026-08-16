"""El modelo de usuario propio: identidad, unicidad, baja lógica y tope de gasto."""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from apps.cuentas.models import Usuario


def test_el_modelo_de_usuario_es_el_propio():
    assert get_user_model() is Usuario


def test_el_correo_es_unico(usuario):
    """Dos cuentas con el mismo correo son la misma persona duplicada."""
    with pytest.raises(IntegrityError):
        Usuario.objects.create_user(username="impostor", email=usuario.email, password="x")


def test_el_tope_de_gasto_por_defecto_son_cinco_euros(usuario):
    """El freno de mano viene puesto: una cuenta nueva no puede gastar sin límite."""
    assert usuario.tope_gasto_mensual_eur == Decimal("5.00")


def test_la_baja_es_logica_y_no_borrado(usuario):
    """Dar de baja no destruye la cuenta: sus casos y su gasto siguen siendo auditables."""
    usuario.is_active = False
    usuario.save()

    assert Usuario.objects.filter(pk=usuario.pk).exists()
    assert not Usuario.objects.get(pk=usuario.pk).is_active


def test_el_usuario_esta_registrado_en_el_panel():
    """El panel es la razón por la que se eligió Django."""
    assert Usuario in admin.site._registry


def test_el_panel_deja_editar_los_campos_propios():
    """Un campo en la tabla que el panel no muestra es un campo inexistente en la práctica."""
    editables = {
        campo
        for _, opciones in admin.site._registry[Usuario].fieldsets
        for campo in opciones["fields"]
    }

    assert {"tope_gasto_mensual_eur", "notas_admin"} <= editables
