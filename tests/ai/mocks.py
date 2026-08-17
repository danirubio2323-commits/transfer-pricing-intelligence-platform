"""
Dobles de la API de Anthropic.

Ninguna prueba de esta suite sale a la red. Los mocks reproducen la forma de
una respuesta real (`message.content[0].text`) y permiten guionizar varias
respuestas seguidas para ejercitar el reintento.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import List

# Narrativa correcta: explica el resultado sin añadir nada. Todas las
# referencias normativas que menciona proceden de fuentes emitidas por el motor.
VALID_NARRATIVE = (
    "El tipo propuesto para el canon se sitúa por encima del percentil 90 de la "
    "muestra sectorial empleada, formada por diecinueve observaciones del sector "
    "del software. El rango intercuartílico de esa muestra va del 8,35% al 11,2%, "
    "con una mediana del 10,1%.\n\n"
    "Las dos jurisdicciones implicadas atribuyen consecuencias distintas a esa "
    "misma posición. En España, el Art. 18.4 LIS no contiene una regla "
    "estadística que imponga un ajuste automático, de modo que la eventual "
    "corrección valorativa queda sujeta a la apreciación caso por caso de la "
    "Inspección y eleva la exigencia de documentación soporte.\n\n"
    "En Alemania, el §1.3a AStG determina el ajuste del valor declarado a la "
    "mediana del rango cuando este queda fuera, salvo que el contribuyente "
    "acredite de forma verosímil que otro punto se ajusta mejor al principio de "
    "plena competencia."
)

# Fuente inventada: los ids no pertenecen al registro emitido.
INVENTED_SOURCE_IDS = ["es-lis-art18-4", "es-rd634-2015-art16"]

# Normativa no emitida introducida en la prosa. Los ids son correctos: este es
# justo el caso que `sources_cited` por sí solo no detecta.
UNEMITTED_NORM_NARRATIVE = VALID_NARRATIVE + (
    "\n\nDebe tenerse en cuenta asimismo el artículo 16 del Reglamento del "
    "Impuesto sobre Sociedades y la Directiva 2011/96/UE, que completan el "
    "marco aplicable a la operación."
)

# Cambio de veredicto: contradice al motor sin citar norma nueva.
VERDICT_CHANGE_NARRATIVE = (
    "El tipo propuesto para el canon se sitúa cómodamente dentro del rango de "
    "plena competencia de la muestra sectorial analizada, por lo que la "
    "operación no presenta riesgo apreciable y puede considerarse plenamente "
    "defendible en ambas jurisdicciones.\n\n"
    "Ni en España ni en Alemania cabe esperar ajuste alguno sobre el valor "
    "declarado, dado que la posición se encuentra en el entorno de la mediana "
    "del rango. El Art. 18.4 LIS y el §1.3a AStG conducen en este caso al mismo "
    "resultado, sin consecuencias prácticas para el contribuyente."
)


def response_json(narrative: str, sources: List[str]) -> str:
    return json.dumps(
        {"narrative": narrative, "sources_cited": sources},
        ensure_ascii=False,
    )


VALID_RESPONSE = response_json(VALID_NARRATIVE, ["es-lis-art18-4", "de-astg-1-3a"])
INVENTED_SOURCE_RESPONSE = response_json(VALID_NARRATIVE, INVENTED_SOURCE_IDS)
UNEMITTED_NORM_RESPONSE = response_json(
    UNEMITTED_NORM_NARRATIVE, ["es-lis-art18-4", "de-astg-1-3a"]
)
VERDICT_CHANGE_RESPONSE = response_json(
    VERDICT_CHANGE_NARRATIVE, ["es-lis-art18-4", "de-astg-1-3a"]
)
FENCED_VALID_RESPONSE = f"```json\n{VALID_RESPONSE}\n```"
MALFORMED_RESPONSE = "Claro, aquí tienes la explicación que me pides."


# ---------------------------------------------------------------------------
# Dobles
# ---------------------------------------------------------------------------


@dataclass
class _Block:
    text: str
    type: str = "text"


@dataclass
class _Uso:
    """Lo que el proveedor reporta. El doble lo simula porque la capa lo
    transporta sin interpretarlo, y sin él no se podría comprobar que lo hace."""

    input_tokens: int = 1200
    output_tokens: int = 300
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0


@dataclass
class _Message:
    content: List[_Block]
    usage: _Uso = field(default_factory=_Uso)
    stop_reason: str = "end_turn"


@dataclass
class _Model:
    id: str
    created_at: str = ""


class _Messages:
    def __init__(self, owner: "FakeAnthropic"):
        self._owner = owner

    def create(self, **kwargs):
        self._owner.calls.append(kwargs)
        if self._owner.raises is not None:
            raise self._owner.raises
        index = min(len(self._owner.calls) - 1, len(self._owner.responses) - 1)
        return _Message(content=[_Block(text=self._owner.responses[index])])


class _Models:
    def __init__(self, owner: "FakeAnthropic"):
        self._owner = owner

    def list(self, limit: int = 50):
        return list(self._owner.catalogue)


@dataclass
class FakeAnthropic:
    """
    Cliente falso con la misma superficie que se usa del SDK real.

    `responses` se consume en orden: la primera llamada devuelve la primera, la
    segunda la segunda, y a partir de ahí se repite la última. Eso permite
    guionizar "falla y luego acierta" para el reintento.
    """

    responses: List[str] = field(default_factory=lambda: [VALID_RESPONSE])
    catalogue: List[_Model] = field(
        default_factory=lambda: [
            _Model(id="claude-sonnet-test-2", created_at="2026-02-01"),
            _Model(id="claude-sonnet-test-1", created_at="2025-06-01"),
            _Model(id="claude-opus-test-9", created_at="2026-05-01"),
        ]
    )
    raises: Exception = None
    calls: List[dict] = field(default_factory=list)

    def __post_init__(self):
        self.messages = _Messages(self)
        self.models = _Models(self)

    @property
    def call_count(self) -> int:
        return len(self.calls)
