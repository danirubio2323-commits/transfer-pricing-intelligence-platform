"""Registro estructurado con `structlog`, montado antes de que haya nada que registrar.

Se configura una sola vez, desde `config/settings/base.py`. Los eventos salen
con nivel, marca de tiempo ISO y las claves que el llamante haya vinculado al
logger, de modo que un evento se pueda filtrar por caso o por usuario sin
analizar texto libre.
"""

from __future__ import annotations

import logging

import structlog


def configure_logging(nivel: int = logging.INFO) -> None:
    """Deja `structlog` utilizable. Idempotente: llamarla dos veces no duplica salida."""
    logging.basicConfig(format="%(message)s", level=nivel, force=True)
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(nivel),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=False,
    )
