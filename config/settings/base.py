"""Configuración común a todos los entornos.

La configuración que viene de fuera está tipada en `Settings`, y **este es el
único punto del proyecto que lee `.env`**: todo lo demás —`manage.py`, pytest
vía `DJANGO_SETTINGS_MODULE`, las vistas y los servicios— pasa por aquí. Los
scripts de `scripts/` no leen ninguna variable de entorno.

Ninguna variable es obligatoria en desarrollo, y eso no es un descuido: es lo
que impide que un paso posterior rompa el gate de un paso anterior exigiendo un
secreto que antes no hacía falta. La única sin valor por defecto es la clave de
firma, y `local.py` le da uno de desarrollo explícito; `production.py` (paso 26)
se niega a arrancar sin ella, que es exactamente el paso cuyo código la
satisface.

Las cinco aplicaciones de `contrib` que entran no son decorativas: este producto
tiene cuentas y panel de administración, y el panel es la razón por la que se
eligió Django frente a FastAPI.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.logging import configure_logging

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Configuración externa, tipada y validada en el arranque."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="before")
    @classmethod
    def _vacio_es_ausente(cls, valores: object) -> object:
        """Una variable declarada y vacía en `.env` cuenta como no definida.

        `.env.example` se versiona con todas las claves presentes y los valores
        vacíos, y el arranque lo copia a `.env` tal cual. Sin esto, un
        `ANTHROPIC_API_KEY=` llegaría como cadena vacía en vez de `None` —y la
        capa de IA no podría distinguir «sin definir» de «definida a nada»— y un
        `PRECIO_ENTRADA_EUR_POR_MTOK=` reventaría la validación del decimal.
        """
        if isinstance(valores, dict):
            return {
                clave: valor
                for clave, valor in valores.items()
                if not (isinstance(valor, str) and not valor.strip())
            }
        return valores

    django_secret_key: str
    django_debug: bool = True
    django_allowed_hosts: str = "127.0.0.1,localhost"
    anthropic_api_key: str | None = None
    anthropic_model: str | None = None
    precio_entrada_eur_por_mtok: Decimal = Field(default=Decimal("0"))
    precio_salida_eur_por_mtok: Decimal = Field(default=Decimal("0"))

    @property
    def allowed_hosts(self) -> list[str]:
        """`a.example,b.example` es una lista de dos, no una cadena con una coma."""
        return [h.strip() for h in self.django_allowed_hosts.split(",") if h.strip()]


configure_logging()

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.cuentas",
    "apps.analisis",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "apps.comun.middleware.ExigirAutenticacion",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

LANGUAGE_CODE = "es-es"
TIME_ZONE = "Europe/Madrid"
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

#: Modelo de usuario propio, fijado antes de la primera migración (paso 4).
AUTH_USER_MODEL = "cuentas.Usuario"

# --- Sesión y acceso (paso 5) ---
LOGIN_URL = "/entrar/"
LOGIN_REDIRECT_URL = "/casos/"
LOGOUT_REDIRECT_URL = "/entrar/"

#: Ocho horas: una jornada. Más allá, se vuelve a pedir la contraseña.
SESSION_COOKIE_AGE = 8 * 60 * 60
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
#: La cookie no es legible desde JavaScript, que es lo que impide robarla con
#: un script inyectado. Nunca un token en almacenamiento del navegador (§20.3).
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
