"""Traduce el resultado del dominio a lo que la plantilla pinta.

Existe porque **ninguna plantilla calcula nada**. Un `{% if %}` que decide una
etiqueta a partir de un enum es lógica escondida en un sitio donde no se puede
probar. Aquí se puede, y las etiquetas salen de `infrastructure.theme`, que es
la fuente única del vocabulario visible.
"""

from __future__ import annotations

from typing import Any

from infrastructure.theme import (
    LEVEL_LABEL,
    POSITION_LABEL,
    RULE_LABEL_SHORT,
)
from tp_domain.models import AnalysisResult

#: Clase CSS por nivel. El nombre del enum no se imprime nunca en el HTML.
CLAVE_NIVEL = {"STRONG": "ok", "MODERATE": "warn", "WEAK": "risk"}


def tarjetas_de_jurisdiccion(resultado: AnalysisResult) -> list[dict[str, Any]]:
    """Una tarjeta por veredicto. El rango es uno; el Derecho, de cada país."""
    return [
        {
            "pais": veredicto.country,
            "regla": RULE_LABEL_SHORT[veredicto.range_rule],
            "nivel": LEVEL_LABEL[veredicto.defensibility_level],
            "nivel_clave": CLAVE_NIVEL[veredicto.defensibility_level.name],
            "posicion": POSITION_LABEL[veredicto.position] if veredicto.position else None,
        }
        for veredicto in resultado.assessments
    ]


def fuentes_enlazadas(resultado: AnalysisResult) -> list[dict[str, Any]]:
    """Cada fuente citada, con la ruta de su ficha si el corpus la tiene.

    El enlace se resuelve por **identificador compartido**: `Ficha.id` es el
    mismo id que emite el registro de fuentes del motor, así que no hay tabla de
    traducción entre uno y otro. Si una fuente no está en el corpus se muestra
    sin enlace, nunca con uno roto.
    """
    from apps.corpus.models import Ficha

    rutas = dict(
        Ficha.objects.filter(pk__in=[f.id for f in resultado.sources]).values_list(
            "pk", "ruta_fichero"
        )
    )
    return [
        {
            "citation": fuente.citation,
            "pinpoint": fuente.pinpoint,
            "ruta": rutas[fuente.id].removesuffix(".md") if fuente.id in rutas else None,
        }
        for fuente in resultado.sources
    ]
