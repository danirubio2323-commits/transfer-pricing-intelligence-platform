"""Configuración común a todos los entornos.

Las cinco aplicaciones de `contrib` que entran aquí no son decorativas: este
producto tiene cuentas y panel de administración (§8), y el panel es la razón
por la que se eligió Django frente a FastAPI.

No se ejecuta `migrate` en el paso 1. La primera migración que se aplica al
proyecto tiene que ser la de `apps.cuentas` con `AUTH_USER_MODEL` ya declarado
(paso 4); aplicar antes las tablas de `auth` con el usuario por defecto es el
estado del que Django no sabe salir.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
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
