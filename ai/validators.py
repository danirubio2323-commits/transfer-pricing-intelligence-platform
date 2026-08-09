"""
Validación del borrador devuelto por el modelo.

Un borrador solo se convierte en `AIExplanation` si pasa estas comprobaciones.
La validación es la frontera: al otro lado, el objeto ya puede adjuntarse a un
`AnalysisResult` y salir impreso en el informe.

Se comprueban cuatro cosas, en orden de importancia:

1. **Fuentes citadas.** `sources_cited` solo puede contener ids del registro
   cerrado que emitió el motor.

2. **Normativa introducida en la prosa.** Esta es la comprobación que de verdad
   ataca el riesgo. Un modelo puede devolver `sources_cited` impecable y aun
   así escribir "conviene atender al artículo 16 del RIS" en el texto. Se
   extraen las referencias normativas del cuerpo y se contrastan con las que el
   motor emitió. Una referencia más específica que la fuente disponible
   (inventar un apartado) también se rechaza.

3. **Formato.** Sin markdown: el texto va a un PDF maquetado, no a un chat.

4. **Extensión.** Fuera de un rango razonable, se rechaza en lugar de imprimir
   un párrafo suelto o cuatro páginas.

Dos comprobaciones consideradas y descartadas, para que conste el motivo:

- *Consistencia numérica* (que toda cifra del texto exista en el análisis).
  Descartada: el modelo escribe legítimamente "dos jurisdicciones" o "un año",
  y perseguir eso genera falsos positivos sin cubrir ningún riesgo real.

- *Lista negra de verbos de recomendación*. Descartada: la conclusión del
  propio motor habla de "exigencia de documentación soporte", así que una
  paráfrasis fiel dispararía el rechazo. El prompt lo prohíbe y el informe
  muestra la conclusión determinista encima de la sección de IA, donde una
  contradicción sería visible.
"""

from __future__ import annotations

import re
import unicodedata
from typing import List, Set

from ai.schemas import PROMPT_VERSION, ExplanationDraft, ExplanationRequest
from tp_domain.models import AIExplanation

#: Extensión admisible del texto, en palabras. El prompt pide entre 120 y 450;
#: el margen evita rechazar por un par de palabras de más o de menos.
MIN_WORDS = 40
MAX_WORDS = 700

#: Referencias normativas reconocibles. No pretende cubrir toda cita posible:
#: cubre las formas en que se cita legislación en este dominio.
_REFERENCE_PATTERNS = (
    # Artículos y parágrafos: "Art. 18.4", "artículo 18", "§1.3a"
    r"(?:art(?:[íi]culos?)?\.?|§)\s*(\d+(?:[.\-]\w+)*)",
    # Párrafos de las Directrices: "párr. 6.34"
    r"p[áa]rr(?:afos?)?\.?\s*(\d+(?:[.\-]\d+)*)",
    # Capítulos: "Cap. III"
    r"cap(?:[íi]tulos?)?\.?\s*([ivxlc]+)\b",
    # Normas con número/año: "Ley 27/2014", "Directiva 2011/96/UE"
    r"(?:ley|directiva|reglamento|real\s+decreto|rd|rdl|rdleg|norma\s+foral)"
    r"\s*(?:\(ue\)\s*)?(\d+[/\-]\d+)",
    # Resoluciones y sentencias: "RG 7833/2023", "STS 1234/2020"
    r"(?:rg|sts|san|stc|teac|ecli|roj)\s*[:\s]?\s*([\w\-/.]+\d)",
)

_PREFIXES = {
    "art": "art", "artículo": "art", "articulo": "art", "artículos": "art",
    "articulos": "art", "§": "art",
    "párr": "parr", "parr": "parr", "párrafo": "parr", "parrafo": "parr",
    "cap": "cap", "capítulo": "cap", "capitulo": "cap",
}


class ExplanationRejected(Exception):
    """
    El borrador no cumple el contrato.

    Lleva la lista de motivos para que el cliente pueda reintentar una vez
    devolviéndoselos al modelo, en lugar de fallar en silencio.
    """

    def __init__(self, reasons: List[str]):
        self.reasons = reasons
        super().__init__("; ".join(reasons))


def _strip_accents(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


def _normalise(marker: str, number: str) -> str:
    marker = _PREFIXES.get(_strip_accents(marker.rstrip(".")).lower(), marker.lower())
    number = number.strip().rstrip(".").lower()
    return f"{marker} {number}"


def extract_legal_references(text: str) -> Set[str]:
    """
    Extrae referencias normativas normalizadas de un texto libre.

    "Art. 18.4", "artículo 18.4" y "art 18.4" colapsan en la misma referencia.
    """
    haystack = _strip_accents(text).lower()
    found: Set[str] = set()

    for pattern in _REFERENCE_PATTERNS:
        for match in re.finditer(pattern, haystack, flags=re.IGNORECASE):
            marker = match.group(0)[: match.start(1) - match.start(0)]
            marker = re.sub(r"[\s.:()]+$", "", marker).strip()
            found.add(_normalise(marker or "ref", match.group(1)))

    return found


def _components(reference: str) -> List[str]:
    return [part for part in re.split(r"[\s.\-/]+", reference) if part]


def _is_covered(candidate: str, allowed: Set[str]) -> bool:
    """
    Una referencia está cubierta si coincide con una emitida o es MENOS
    específica que ella.

    "artículo 18" está cubierto por "art 18.4": el modelo cita con menos
    precisión, que es inocuo. Lo contrario no: si el motor emitió "art 18.4" y
    el modelo escribe "art 18.4.b", se está inventando un apartado.
    """
    cand = _components(candidate)
    for reference in allowed:
        ref = _components(reference)
        if cand == ref[: len(cand)]:
            return True
    return False


def allowed_references(request: ExplanationRequest) -> Set[str]:
    """Referencias normativas que el motor sí ha puesto sobre la mesa."""
    references: Set[str] = set()
    for source in request.allowed_sources:
        references |= extract_legal_references(source.citation)
        if source.pinpoint:
            references |= extract_legal_references(source.pinpoint)
    return references


def validate_draft(
    draft: ExplanationDraft,
    request: ExplanationRequest,
    model: str,
    prompt_version: str = PROMPT_VERSION,
) -> AIExplanation:
    """
    Promueve un borrador a `AIExplanation`, o lo rechaza con motivos.

    Lanza `ExplanationRejected`. No devuelve nunca una explicación degradada:
    o el texto cumple, o el informe sale sin sección de IA.
    """
    reasons: List[str] = []

    # 1. Fuentes citadas dentro del registro emitido
    unknown = sorted(set(draft.sources_cited) - request.allowed_source_ids)
    if unknown:
        reasons.append(
            f"cita fuentes que el motor no emitió: {unknown}"
        )

    if request.assessments and not draft.sources_cited:
        reasons.append("no cita ninguna fuente pese a existir base legal en el análisis")

    # 2. Normativa introducida en la prosa
    allowed = allowed_references(request)
    invented = sorted(
        ref for ref in extract_legal_references(draft.narrative)
        if not _is_covered(ref, allowed)
    )
    if invented:
        reasons.append(
            f"introduce normativa ausente del análisis: {invented}"
        )

    # 3. Formato
    if re.search(r"^\s*(#{1,6}\s|[-*•]\s|\d+\.\s)", draft.narrative, flags=re.MULTILINE):
        reasons.append("contiene markdown o listas; el destino es un PDF maquetado")

    # 4. Extensión
    words = len(draft.narrative.split())
    if not MIN_WORDS <= words <= MAX_WORDS:
        reasons.append(
            f"extensión fuera de rango: {words} palabras "
            f"(admitido {MIN_WORDS}-{MAX_WORDS})"
        )

    if reasons:
        raise ExplanationRejected(reasons)

    return AIExplanation(
        text=draft.narrative.strip(),
        prompt_version=prompt_version,
        model=model,
        sources_cited=list(draft.sources_cited),
    )
