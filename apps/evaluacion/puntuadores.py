"""Puntuadores, de lo más barato a lo más caro, parando en el primero que decide.

**El orden es la política de coste.** La mayoría de los casos se resuelven en la
capa 1, que no cuesta nada y no toca la red. Solo lo que las dos primeras capas
no logran decidir llega a un juicio del modelo, que es la que se paga.

Un puntuador devuelve `(veredicto, motivo)`. El veredicto es `True`, `False` o
`None` — y `None` significa **«no me corresponde a mí decidir esto»**, no
«dudo». Confundir esas dos cosas haría que un caso indeciso contara como acierto.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

#: Extensión admisible, la misma que ya impone el validador de la capa de IA.
from ai.validators import (  # noqa: E402  (se agrupa aquí a propósito)
    MAX_WORDS,
    MIN_WORDS,
    extract_legal_references,
)
from tp_domain.models import AIExplanation, AnalysisResult


@dataclass(frozen=True)
class Veredicto:
    """Resultado de un puntuador. `acierta=None` significa «no decido yo»."""

    acierta: Optional[bool]
    motivo: str
    capa: str


def _cifras(texto: str) -> set[str]:
    """Números con decimales del texto. Los enteros sueltos se ignoran a propósito.

    El modelo escribe legítimamente «dos jurisdicciones» o «un año»; perseguir
    eso produce falsos positivos sin cubrir ningún riesgo real. Lo que no puede
    hacer es inventarse un percentil.
    """
    return set(re.findall(r"\d+[.,]\d+", texto))


# ---------------------------------------------------------------------------
# Capa 1 — determinista. No cuesta nada y decide la mayoría.
# ---------------------------------------------------------------------------


def deterministas(
    resultado: AnalysisResult, explicacion: AIExplanation, esperadas: dict
) -> Veredicto:
    """Fuentes dentro del registro, ninguna cifra nueva, extensión razonable."""
    emitidas = {fuente.id for fuente in resultado.sources}
    inventadas = sorted(set(explicacion.sources_cited) - emitidas)
    if inventadas:
        return Veredicto(False, f"cita fuentes que el motor no emitió: {inventadas}", "1")

    del_motor = _cifras(resultado.conclusion) | {
        str(v) for v in resultado.benchmark.model_dump().values() if v is not None
    }
    nuevas = sorted(c for c in _cifras(explicacion.text) if c not in del_motor)
    if nuevas:
        return Veredicto(False, f"introduce cifras que el motor no emitió: {nuevas}", "1")

    palabras = len(explicacion.text.split())
    if not MIN_WORDS <= palabras <= MAX_WORDS:
        return Veredicto(False, f"extensión fuera de rango: {palabras} palabras", "1")

    return Veredicto(None, "sin veredicto determinista", "1")


# ---------------------------------------------------------------------------
# Capa 2 — léxica sobre las referencias legales. Sigue sin costar nada.
# ---------------------------------------------------------------------------


def lexicos(resultado: AnalysisResult, explicacion: AIExplanation, esperadas: dict) -> Veredicto:
    """Comprueba las propiedades declaradas del caso dorado."""
    exigidas = set(esperadas.get("debe_citar_alguna_de") or [])
    if exigidas and not exigidas & set(explicacion.sources_cited):
        return Veredicto(
            False, f"no cita ninguna de las fuentes esperadas: {sorted(exigidas)}", "2"
        )

    espera_ajuste = esperadas.get("debe_mencionar_ajuste_a_la_mediana")
    if espera_ajuste is not None:
        menciona = "mediana" in explicacion.text.lower()
        if espera_ajuste and not menciona:
            return Veredicto(False, "no menciona el ajuste a la mediana y debería", "2")
        if not espera_ajuste and menciona:
            return Veredicto(False, "menciona un ajuste a la mediana que no procede", "2")

    if extract_legal_references(explicacion.text):
        # Cita normativa Y cumple lo exigido: decide en esta capa, sin llegar al
        # juicio del modelo.
        return Veredicto(True, "cumple las propiedades declaradas y fundamenta", "2")

    return Veredicto(None, "sin referencias legales que evaluar", "2")


# ---------------------------------------------------------------------------
# Capa 3 — juicio del modelo. La única que se paga.
# ---------------------------------------------------------------------------


def juicio_del_modelo(
    resultado: AnalysisResult, explicacion: AIExplanation, esperadas: dict, juez=None
) -> Veredicto:
    """Solo se invoca si las dos anteriores no han decidido.

    `juez` se inyecta. Sin él, el caso queda **sin decidir** en vez de contar
    como acierto: un arnés que aprueba lo que no ha podido evaluar miente.
    """
    if juez is None:
        return Veredicto(None, "no hay juez configurado; el caso queda sin decidir", "3")
    return juez(resultado, explicacion, esperadas)


CAPAS = (deterministas, lexicos)


def puntuar(
    resultado: AnalysisResult, explicacion: AIExplanation, esperadas: dict, juez=None
) -> Veredicto:
    """Recorre las capas y **se para en la primera que decide**."""
    for capa in CAPAS:
        veredicto = capa(resultado, explicacion, esperadas)
        if veredicto.acierta is not None:
            return veredicto
    return juicio_del_modelo(resultado, explicacion, esperadas, juez=juez)
