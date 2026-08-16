"""Acceso, cierre de sesión y cierre por omisión.

El criterio que gobierna este fichero: el fallo por omisión tiene que ser el
seguro. Si alguien añade una vista y olvida protegerla, debe quedar cerrada.
"""

from __future__ import annotations

import pytest
from django.urls import reverse

CLAVE = "clave-de-prueba-no-usada-en-produccion"


@pytest.mark.django_db
def test_una_peticion_anonima_va_a_entrar_conservando_el_destino(client):
    """El cierre por omisión: `/` no está protegida por un decorador, sino por el middleware."""
    respuesta = client.get("/")

    assert respuesta.status_code == 302
    assert respuesta["Location"].startswith("/entrar/")
    assert "next=%2F" in respuesta["Location"] or "next=/" in respuesta["Location"]


@pytest.mark.django_db
def test_entrar_es_publica(client):
    assert client.get("/entrar/").status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize(
    "usuario_enviado, clave_enviada",
    [
        ("noexiste", CLAVE),  # usuario inexistente
        ("daru", "clave-equivocada"),  # contraseña incorrecta
    ],
)
def test_el_rechazo_es_422_y_no_dice_cual_de_los_dos_motivos(
    client, usuario, usuario_enviado, clave_enviada
):
    """Distinguir los motivos convertiría el formulario en un detector de cuentas."""
    respuesta = client.post("/entrar/", {"username": usuario_enviado, "password": clave_enviada})

    assert respuesta.status_code == 422
    assert "Usuario o contraseña incorrectos." in respuesta.content.decode()


@pytest.mark.django_db
def test_una_cuenta_inactiva_recibe_el_mismo_mensaje(client, usuario):
    usuario.is_active = False
    usuario.save()

    respuesta = client.post("/entrar/", {"username": usuario.username, "password": CLAVE})

    assert respuesta.status_code == 422
    assert "Usuario o contraseña incorrectos." in respuesta.content.decode()


@pytest.mark.django_db
def test_credenciales_validas_entran(client, usuario):
    respuesta = client.post("/entrar/", {"username": usuario.username, "password": CLAVE})

    assert respuesta.status_code == 302
    assert respuesta["Location"] == "/casos/"


@pytest.mark.django_db
def test_un_next_a_otro_host_se_ignora(client, usuario):
    """Una redirección abierta convierte el acceso en un trampolín hacia fuera."""
    respuesta = client.post(
        "/entrar/",
        {"username": usuario.username, "password": CLAVE, "next": "https://ejemplo.invalido/"},
    )

    assert respuesta.status_code == 302
    assert respuesta["Location"] == "/casos/"


@pytest.mark.django_db
def test_salir_con_get_responde_405_y_no_cierra_la_sesion(client, usuario):
    """Con GET, una imagen o un enlace cerrarían la sesión de otro."""
    client.force_login(usuario)

    respuesta = client.get("/salir/")

    assert respuesta.status_code == 405
    assert client.get("/entrar/").wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_salir_con_post_cierra_la_sesion(client, usuario):
    client.force_login(usuario)

    respuesta = client.post("/salir/")

    assert respuesta.status_code == 302
    assert not respuesta.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_cambiar_la_contrasena_rota_la_clave_de_sesion(client, usuario):
    """Si la cookie antigua siguiera valiendo, cambiar la contraseña no expulsaría a nadie."""
    client.force_login(usuario)
    sesion_anterior = client.session.session_key

    respuesta = client.post(
        reverse("cuentas:contrasena"),
        {
            "old_password": CLAVE,
            "new_password1": "otra-clave-larga-y-distinta-99",
            "new_password2": "otra-clave-larga-y-distinta-99",
        },
    )

    assert respuesta.status_code == 302
    assert client.session.session_key != sesion_anterior
