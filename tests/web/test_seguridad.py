"""Cabeceras, CSRF y la frontera entre desarrollo y producción.

Lo que se comprueba aquí no es que las variables estén escritas —eso lo vería
cualquiera leyendo el fichero— sino que **se emiten** en la respuesta y que
producción **no arranca** sin clave de firma.

La distinción importa: `X_FRAME_OPTIONS = "DENY"` sin el middleware que la
escribe es una variable que nadie lee, y un `SECRET_KEY` con valor de reserva
deja firmar sesiones a cualquiera que lea el repositorio.
"""

from __future__ import annotations

import os
import subprocess
import sys

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse

from apps.analisis.models import Caso

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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


# ---------------------------------------------------------------------------
# Cabeceras que sí salen en la respuesta
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_toda_respuesta_lleva_nosniff_y_referrer_policy(client, usuario):
    """El identificador de un caso viaja en la URL: el `Referer` no debe salir
    del sitio, y el navegador no debe adivinar el tipo de un fichero."""
    client.force_login(usuario)

    respuesta = client.get(reverse("analisis:formulario"))

    assert respuesta.headers["X-Content-Type-Options"] == "nosniff"
    assert respuesta.headers["Referrer-Policy"] == "same-origin"


@pytest.mark.django_db
def test_la_respuesta_prohibe_enmarcar_la_aplicacion(client, usuario):
    """Sin el middleware de clickjacking, `X_FRAME_OPTIONS` no la escribe nadie."""
    client.force_login(usuario)

    respuesta = client.get(reverse("analisis:formulario"))

    assert respuesta.headers["X-Frame-Options"] == "DENY"


def test_el_middleware_de_clickjacking_esta_montado():
    assert "django.middleware.clickjacking.XFrameOptionsMiddleware" in settings.MIDDLEWARE


def test_whitenoise_va_detras_de_securitymiddleware():
    """Delante quedaría fuera del alcance de las cabeceras de seguridad."""
    orden = settings.MIDDLEWARE

    assert orden.index("whitenoise.middleware.WhiteNoiseMiddleware") == (
        orden.index("django.middleware.security.SecurityMiddleware") + 1
    )


# ---------------------------------------------------------------------------
# CSRF
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_un_post_sin_token_csrf_responde_403_y_no_crea_nada(usuario):
    """El único 403 legítimo del proyecto. Y sobre todo: cero filas."""
    cliente = Client(enforce_csrf_checks=True)
    cliente.force_login(usuario)

    respuesta = cliente.post(reverse("analisis:crear"), VALIDO)

    assert respuesta.status_code == 403
    assert Caso.objects.count() == 0


@pytest.mark.django_db
def test_con_token_csrf_el_mismo_post_pasa(usuario):
    """La prueba anterior no vale sin esta: sin ella, un 403 por cualquier otro
    motivo —una ruta mal escrita— se leería como «el CSRF funciona»."""
    cliente = Client(enforce_csrf_checks=True)
    cliente.force_login(usuario)
    cliente.get(reverse("analisis:formulario"))  # deja la cookie del token
    token = cliente.cookies["csrftoken"].value

    respuesta = cliente.post(reverse("analisis:crear"), {**VALIDO, "csrfmiddlewaretoken": token})

    assert respuesta.status_code == 302
    assert Caso.objects.count() == 1


# ---------------------------------------------------------------------------
# Local no finge tener TLS
# ---------------------------------------------------------------------------


def test_en_local_las_cookies_no_llevan_la_marca_segura():
    """Activarla sin HTTPS deja la aplicación inservible en local, y una medida
    que hay que desactivar para trabajar acaba desactivada el día del despliegue."""
    assert settings.SESSION_COOKIE_SECURE is False
    assert settings.CSRF_COOKIE_SECURE is False
    assert settings.SECURE_SSL_REDIRECT is False


def test_en_local_la_cookie_de_sesion_sigue_siendo_httponly():
    """Lo que no depende de TLS no se relaja: un script inyectado no la lee."""
    assert settings.SESSION_COOKIE_HTTPONLY is True
    assert settings.SESSION_COOKIE_SAMESITE == "Lax"


# ---------------------------------------------------------------------------
# Producción, cargada en un subproceso limpio
# ---------------------------------------------------------------------------


def _arrancar_produccion(entorno: dict[str, str]) -> subprocess.CompletedProcess[str]:
    """Django se configura una sola vez por proceso: producción se carga fuera."""
    limpio = {k: v for k, v in os.environ.items() if k != "DJANGO_SECRET_KEY"}
    limpio["DJANGO_SETTINGS_MODULE"] = "config.settings.production"
    limpio.update(entorno)

    return subprocess.run(
        [
            sys.executable,
            "-c",
            "import django; django.setup();"
            "from django.conf import settings as s;"
            "print('ARRANCO');"
            "print(s.DEBUG, s.SESSION_COOKIE_SECURE, s.CSRF_COOKIE_SECURE,"
            " s.SECURE_SSL_REDIRECT, s.SECURE_HSTS_SECONDS,"
            " s.SECURE_HSTS_INCLUDE_SUBDOMAINS, s.SECURE_HSTS_PRELOAD,"
            " s.SECURE_CONTENT_TYPE_NOSNIFF, s.SECURE_REFERRER_POLICY,"
            " s.X_FRAME_OPTIONS)",
        ],
        cwd=RAIZ,
        env=limpio,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def test_produccion_no_arranca_sin_clave_y_lo_dice_por_su_nombre():
    """No basta con «falla»: un error de importación cualquiera también fallaría.
    Tiene que nombrar la variable que falta, o nadie sabrá qué arreglar."""
    hecho = _arrancar_produccion({})

    # Solo `stdout`: la traza de error incluye la línea de código, y ahí aparece
    # la propia palabra `ARRANCO` sin que nada haya arrancado.
    assert "ARRANCO" not in hecho.stdout
    assert hecho.returncode != 0
    assert "DJANGO_SECRET_KEY" in hecho.stderr


def test_produccion_no_cae_a_la_clave_de_desarrollo():
    """El fallo tiene que ser por ausencia, no un apaño que reutilice `local.py`."""
    from config.settings.local import CLAVE_DE_DESARROLLO

    hecho = _arrancar_produccion({})

    assert CLAVE_DE_DESARROLLO not in (hecho.stdout + hecho.stderr)


def test_produccion_con_clave_arranca_y_cierra_todo():
    clave = "x" + "y" * 70  # larga de sobra: `check --deploy` exige 50 caracteres
    hecho = _arrancar_produccion({"DJANGO_SECRET_KEY": clave})
    salida = hecho.stdout + hecho.stderr

    assert "ARRANCO" in salida, salida
    valores = salida.splitlines()[1].split()

    assert valores[:4] == ["False", "True", "True", "True"]  # DEBUG y las tres de TLS
    assert valores[4:8] == ["31536000", "True", "True", "True"]  # HSTS y nosniff
    assert valores[8:] == ["same-origin", "DENY"]


def test_produccion_lee_los_hosts_del_entorno():
    hecho = subprocess.run(
        [
            sys.executable,
            "-c",
            "import django; django.setup();"
            "from django.conf import settings as s; print(s.ALLOWED_HOSTS)",
        ],
        cwd=RAIZ,
        env={
            **os.environ,
            "DJANGO_SETTINGS_MODULE": "config.settings.production",
            "DJANGO_SECRET_KEY": "x" + "y" * 70,
            "DJANGO_ALLOWED_HOSTS": "tpip.example,otro.example",
        },
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    assert "tpip.example" in hecho.stdout
    assert "otro.example" in hecho.stdout
    # `testserver` es un apaño de pruebas y no debe colarse en producción.
    assert "testserver" not in hecho.stdout
