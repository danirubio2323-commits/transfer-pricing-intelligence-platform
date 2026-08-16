"""Fixtures compartidas de toda la suite web.

Viven aquí porque este es el primer paso en el que existe la tabla de usuarios,
y desde el paso 5 **todas** las pruebas de `tests/web/` las piden. Sin este
fichero la suite entera falla con `fixture 'usuario' not found`, que se lee como
una instalación rota y no lo es.

`otro_usuario` no es un duplicado por comodidad: es la contraparte de las
pruebas de aislamiento, que comprueban que un usuario recibe 404 —no 403— al
pedir un caso ajeno.
"""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model

CLAVE = "clave-de-prueba-no-usada-en-produccion"


@pytest.fixture
def usuario(db):
    return get_user_model().objects.create_user(
        username="daru", email="daru@example.test", password=CLAVE
    )


@pytest.fixture
def otro_usuario(db):
    """La contraparte: existe para poder comprobar que no ve lo del primero."""
    return get_user_model().objects.create_user(
        username="otra", email="otra@example.test", password=CLAVE
    )


@pytest.fixture
def administrador(db):
    return get_user_model().objects.create_superuser(
        username="admin", email="admin@example.test", password=CLAVE
    )
