"""La configuración carga, no exige nada en desarrollo, y el registro funciona."""

from __future__ import annotations

import logging
from decimal import Decimal

import structlog
from django.conf import settings

from config.logging import configure_logging
from config.settings.base import Settings

VARIABLES = (
    "DJANGO_SECRET_KEY",
    "DJANGO_DEBUG",
    "DJANGO_ALLOWED_HOSTS",
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_MODEL",
    "PRECIO_ENTRADA_EUR_POR_MTOK",
    "PRECIO_SALIDA_EUR_POR_MTOK",
)


def test_ninguna_variable_es_obligatoria_en_desarrollo(monkeypatch, tmp_path):
    """Con el entorno vacío y sin `.env`, la configuración carga igual."""
    for nombre in VARIABLES:
        monkeypatch.delenv(nombre, raising=False)
    monkeypatch.chdir(tmp_path)  # sin .env que leer

    ajustes = Settings(django_secret_key="clave-de-prueba")

    assert ajustes.django_debug is True
    assert ajustes.precio_entrada_eur_por_mtok == Decimal("0")


def test_la_clave_ausente_es_None_y_no_cadena_vacia(monkeypatch, tmp_path):
    """La capa de IA tiene que distinguir «sin definir» de «definida a nada»."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.chdir(tmp_path)

    ajustes = Settings(django_secret_key="clave-de-prueba")

    assert ajustes.anthropic_api_key is None
    assert ajustes.anthropic_model is None


def test_los_hosts_se_parten_en_lista(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    ajustes = Settings(
        django_secret_key="clave-de-prueba",
        django_allowed_hosts="a.example,b.example",
    )

    assert ajustes.allowed_hosts == ["a.example", "b.example"]


def test_django_expone_allowed_hosts_como_lista():
    assert isinstance(settings.ALLOWED_HOSTS, list)
    assert "127.0.0.1" in settings.ALLOWED_HOSTS


def test_el_logger_conserva_las_claves_vinculadas(capsys):
    configure_logging(logging.INFO)
    structlog.get_logger().bind(caso="abc-123").info("analisis_calculado")

    capturado = capsys.readouterr()  # una sola llamada: la segunda vaciaría el búfer
    texto = capturado.out + capturado.err
    assert "analisis_calculado" in texto
    assert "abc-123" in texto
