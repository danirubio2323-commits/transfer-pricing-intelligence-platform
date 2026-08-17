"""
Cliente de Anthropic para la explicación narrativa.

Contrato de esta capa, en una frase: **puede fallar entera sin que se note en el
informe**. Si no hay clave, si la API cae, si el modelo devuelve algo que no
pasa la validación — la función devuelve `None` y el PDF sale sin sección de IA.
Ninguna ruta de error propaga hacia arriba.

**El modelo se inyecta; esta capa no lo descubre.** Antes, sin `ANTHROPIC_MODEL`
se preguntaba al catálogo en ejecución y se elegía el Sonnet más reciente. Eso
rompía la reproducibilidad —dos informes idénticos en todo lo demás podían
haberse redactado con modelos distintos sin que nadie lo decidiera—, convertía
una llamada de red opcional en obligatoria, y hacía imposible tarifar antes de
llamar, que es lo que exige el tope de gasto. Ahora, sin modelo la capa se
desactiva y lo dice.

La clave se lee de `ANTHROPIC_API_KEY` del entorno, o la inyecta el llamante.
Quien carga `.env` es la configuración tipada de la aplicación y nadie más.

El identificador exacto que se acabe usando viaja dentro de `AIExplanation.model`,
para que un informe emitido hoy diga con qué modelo se redactó.
"""

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Any, List, NamedTuple, Optional

from ai.schemas import PROMPT_VERSION, ExplanationDraft, ExplanationRequest
from ai.validators import ExplanationRejected, validate_draft
from tp_domain.models import AIExplanation, AnalysisResult

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"

MAX_TOKENS = 1500
#: Temperatura baja: el objetivo es una redacción fiel y reproducible, no
#: variedad expresiva.
TEMPERATURE = 0.2
#: Un único reintento, y solo con los motivos de rechazo.
MAX_ATTEMPTS = 2


class ClaudeUnavailable(RuntimeError):
    """No se puede usar la capa de IA (sin clave, sin modelo o API caída)."""


# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------


def resolve_api_key() -> Optional[str]:
    """
    Devuelve la primera clave disponible, o None si no hay ninguna.

    Antes había un primer eslabón que leía los secretos de Streamlit Cloud. Se
    retira con la interfaz de Streamlit: era la única dependencia de esta capa
    con un framework, y esta capa tiene que poder importarse sin ninguno
    —`tests/web/test_rescate.py` lo comprueba en un intérprete limpio—.

    La aplicación web no llama a esta función: le pasa la clave que ya ha leído
    su propia configuración tipada, que es **el único punto del proyecto que lee
    `.env`**. Este eslabón existe para quien use la capa de IA suelta, desde un
    script o una prueba.
    """
    return os.environ.get("ANTHROPIC_API_KEY") or None


def load_system_prompt(version: str = PROMPT_VERSION) -> str:
    """Extrae el bloque de system prompt del fichero versionado."""
    path = PROMPTS_DIR / f"{version}.md"
    document = path.read_text(encoding="utf-8")
    match = re.search(r"```text\n(.*?)```", document, flags=re.DOTALL)
    if not match:
        raise ClaudeUnavailable(f"El prompt {path} no contiene bloque ```text```")
    return match.group(1).strip()


def build_client(api_key: Optional[str] = None):
    """Crea el cliente de Anthropic, o falla explícitamente si no hay clave."""
    key = api_key or resolve_api_key()
    if not key:
        raise ClaudeUnavailable("No hay ANTHROPIC_API_KEY configurada.")
    try:
        from anthropic import Anthropic
    except ImportError as exc:  # pragma: no cover
        raise ClaudeUnavailable("El paquete `anthropic` no está instalado.") from exc
    return Anthropic(api_key=key)


# ---------------------------------------------------------------------------
# Parseo de la respuesta
# ---------------------------------------------------------------------------


def extract_text(message) -> str:
    """Concatena los bloques de texto de una respuesta de la API."""
    parts = [
        getattr(block, "text", "")
        for block in getattr(message, "content", [])
        if getattr(block, "type", "text") == "text"
    ]
    return "".join(parts).strip()


def parse_draft(raw: str) -> ExplanationDraft:
    """
    Convierte la respuesta cruda en un borrador tipado.

    Tolera que el modelo envuelva el JSON en un bloque de código, que es el
    desliz más habitual; cualquier otra desviación es un rechazo legítimo.
    """
    text = raw.strip()
    fenced = re.match(r"^```(?:json)?\s*\n(.*?)\n?```$", text, flags=re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()

    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ExplanationRejected([f"la respuesta no es JSON válido: {exc.msg}"]) from exc

    if not isinstance(payload, dict):
        raise ExplanationRejected(["la respuesta no es un objeto JSON"])

    try:
        return ExplanationDraft(**payload)
    except Exception as exc:  # noqa: BLE001 - pydantic ValidationError
        raise ExplanationRejected([f"la respuesta no cumple el esquema: {exc}"]) from exc


# ---------------------------------------------------------------------------
# Flujo
# ---------------------------------------------------------------------------


def _retry_message(reasons: List[str]) -> str:
    """
    Mensaje del segundo intento.

    Contiene ÚNICAMENTE los motivos de rechazo. No se reenvía información del
    análisis: el modelo ya la tiene en el primer turno, y añadir contexto nuevo
    en la corrección abriría la puerta a que el segundo intento diga cosas que
    el primero no podía decir.
    """
    listed = "\n".join(f"- {reason}" for reason in reasons)
    return (
        "El borrador anterior ha sido rechazado por la validación automática "
        f"por los siguientes motivos:\n{listed}\n\n"
        "Devuelve un nuevo objeto JSON con el mismo formato, corrigiendo "
        "exclusivamente esos motivos. No añadas información nueva."
    )


class RespuestaIA(NamedTuple):
    """Lo que devuelve una llamada que ha ido bien.

    `usage` y `stop_reason` viajan **sin interpretar**: esta capa no cuenta
    tokens ni calcula coste. El único recuento fiable es el que reporta el
    proveedor, y quien lo persiste es la capa web (`LlamadaLLM`, paso 16).
    Contarlos aquí sería estimar, y una estimación no sirve para un tope.
    """

    explicacion: AIExplanation
    usage: Any = None
    stop_reason: Optional[str] = None


def request_explanation(
    result: AnalysisResult,
    client=None,
    model: Optional[str] = None,
) -> RespuestaIA:
    """
    Pide la explicación y la devuelve validada, con el uso que reportó el proveedor.

    **Exige `model`.** Si no llega, la capa se desactiva en vez de adivinar: un
    modelo que no se conoce antes de llamar tampoco se puede tarifar antes de
    llamar, y sin tarifa no hay tope de gasto comprobable antes del gasto.

    Lanza `ClaudeUnavailable` o `ExplanationRejected`. Para uso normal desde la
    aplicación, prefiere `explain_analysis`, que no lanza.
    """
    if not model:
        raise ClaudeUnavailable(
            "No hay ANTHROPIC_MODEL configurado: la capa de IA queda desactivada. "
            "El modelo se fija en configuración, no se resuelve en ejecución."
        )
    client = client or build_client()
    system = load_system_prompt()
    payload = ExplanationRequest.from_result(result)

    messages = [{"role": "user", "content": payload.model_dump_json(indent=2)}]
    last_error: Optional[ExplanationRejected] = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            message = client.messages.create(
                model=model,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                system=system,
                messages=messages,
            )
        except Exception as exc:  # noqa: BLE001 - errores de red o de API
            raise ClaudeUnavailable(f"La llamada a la API ha fallado: {exc}") from exc

        raw = extract_text(message)

        try:
            draft = parse_draft(raw)
            return RespuestaIA(
                explicacion=validate_draft(draft, payload, model=model),
                usage=getattr(message, "usage", None),
                stop_reason=getattr(message, "stop_reason", None),
            )
        except ExplanationRejected as rejection:
            last_error = rejection
            logger.warning(
                "Borrador rechazado (intento %s/%s): %s",
                attempt,
                MAX_ATTEMPTS,
                "; ".join(rejection.reasons),
            )
            if attempt == MAX_ATTEMPTS:
                break
            messages = messages + [
                {"role": "assistant", "content": raw},
                {"role": "user", "content": _retry_message(rejection.reasons)},
            ]

    raise last_error  # type: ignore[misc]


def explain_analysis(
    result: AnalysisResult,
    client=None,
    model: Optional[str] = None,
) -> Optional[RespuestaIA]:
    """
    Punto de entrada para la aplicación. **No lanza nunca.**

    Devuelve la respuesta validada, o `None` si no hay clave, no hay modelo, la
    API falla o el borrador no supera la validación en dos intentos. El informe
    se genera igual: la sección de IA es aditiva.
    """
    try:
        return request_explanation(result, client=client, model=model)
    except ClaudeUnavailable as exc:
        logger.info("Capa de IA no disponible: %s", exc)
    except ExplanationRejected as exc:
        logger.warning("Explicación descartada tras el reintento: %s", exc)
    except Exception as exc:  # noqa: BLE001 - nada puede tumbar el informe
        logger.exception("Fallo inesperado en la capa de IA: %s", exc)
    return None
