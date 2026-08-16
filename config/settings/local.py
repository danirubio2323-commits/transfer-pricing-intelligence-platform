"""Configuración de desarrollo local. Escucha solo en la interfaz local.

La clave de firma sale del entorno si está definida y, si no, de un valor de
desarrollo explícito. Así la configuración carga con el entorno vacío y sin
`.env`, que es lo que permite que ningún gate anterior se rompa.
"""

from __future__ import annotations

import os

from config.settings.base import *  # noqa: F403
from config.settings.base import Settings

#: Clave de DESARROLLO, deliberadamente explícita y no secreta. Producción la
#: toma del entorno y se niega a arrancar sin ella (paso 26).
CLAVE_DE_DESARROLLO = "django-insecure-clave-solo-de-desarrollo-no-usar-en-produccion"

ajustes = Settings(django_secret_key=os.environ.get("DJANGO_SECRET_KEY") or CLAVE_DE_DESARROLLO)

SECRET_KEY = ajustes.django_secret_key
DEBUG = ajustes.django_debug
ALLOWED_HOSTS = [*ajustes.allowed_hosts, "testserver"]

ANTHROPIC_API_KEY = ajustes.anthropic_api_key
ANTHROPIC_MODEL = ajustes.anthropic_model
PRECIO_ENTRADA_EUR_POR_MTOK = ajustes.precio_entrada_eur_por_mtok
PRECIO_SALIDA_EUR_POR_MTOK = ajustes.precio_salida_eur_por_mtok
