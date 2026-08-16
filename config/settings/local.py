"""Configuración de desarrollo local. Escucha solo en la interfaz local."""

from config.settings.base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver"]

# Clave de DESARROLLO, deliberadamente explícita y no secreta. Producción la
# toma del entorno y se niega a arrancar sin ella (paso 26).
SECRET_KEY = "django-insecure-clave-solo-de-desarrollo-no-usar-en-produccion"
