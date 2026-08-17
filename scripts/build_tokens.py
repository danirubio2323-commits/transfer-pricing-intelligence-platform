"""Genera `static/css/tokens.css` desde la paleta de `infrastructure.theme`.

Cierra el contrato entre pantalla e informe: el CSS deja de tener colores
literales y pasa a consumir variables generadas del **mismo diccionario** que
usa el PDF. Si alguien cambia un hexadecimal en `theme.py` y no regenera, el
modo `--check` lo dice; si alguien lo cambia en `tokens.css` a mano, la próxima
generación se lo lleva por delante — que es lo correcto: `theme.py` manda.

**Se invoca con `-m`**, siempre:

    uv run python -m scripts.build_tokens

Ejecutarlo como ruta (`python scripts/build_tokens.py`) pone `scripts/` en
`sys.path[0]` en vez de la raíz del proyecto, y entonces `infrastructure` no se
encuentra. No es un capricho de estilo: es la única forma que funciona.

Códigos de salida: 0 sincronizado · 1 desincronizado · 2 error de uso.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from infrastructure.theme import COLORS_PANTALLA

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "static" / "css" / "tokens.css"

#: Escala de espaciado de §7, base 4px. Ningún valor arbitrario fuera de aquí.
ESPACIADO = (4, 8, 12, 16, 24, 32, 48, 64)

#: Escala tipográfica de §7, en rem.
TIPOGRAFIA = {
    "xs": "0.875",
    "base": "1",
    "md": "1.0625",
    "lg": "1.375",
    "xl": "2",
}

RADIO = {"control": "4px", "tarjeta": "8px", "tabla": "0"}


def _variable(clave: str) -> str:
    return f"--tpip-{clave.replace('_', '-')}"


def generar() -> str:
    """El contenido que debería tener `tokens.css`. Función pura: no toca disco."""
    lineas = [
        "/* GENERADO por `uv run python -m scripts.build_tokens`. NO EDITAR A MANO.",
        " * La paleta vive en infrastructure/theme.py; aquí solo se proyecta a CSS.",
        " * Editar este fichero es trabajo que la próxima generación borra. */",
        "",
        ":root {",
        "  /* Superficie de PANTALLA. La del informe vive en theme.COLORS y la",
        "     consume el generador de PDF, no este fichero. */",
    ]
    for clave, valor in COLORS_PANTALLA.items():
        lineas.append(f"  {_variable(clave)}: {valor};")

    lineas.append("")
    lineas.append("  /* Espaciado, base 4px */")
    for px in ESPACIADO:
        lineas.append(f"  --tpip-espacio-{px}: {px}px;")

    lineas.append("")
    lineas.append("  /* Escala tipográfica, en rem */")
    for nombre, rem in TIPOGRAFIA.items():
        lineas.append(f"  --tpip-texto-{nombre}: {rem}rem;")

    lineas.append("")
    lineas.append("  /* Radio */")
    for nombre, valor in RADIO.items():
        lineas.append(f"  --tpip-radio-{nombre}: {valor};")

    lineas.append("")
    lineas.append("  /* Movimiento: 120ms, y solo si nadie ha pedido lo contrario */")
    lineas.append("  --tpip-transicion: 120ms ease-out;")
    lineas.append("}")
    lineas.append("")
    return "\n".join(lineas)


def main(argv: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument(
        "--check",
        action="store_true",
        help="No escribe. Sale 0 si el fichero coincide, 1 si hay que regenerar.",
    )
    opciones = analizador.parse_args(argv)

    esperado = generar()
    actual = DESTINO.read_text(encoding="utf-8") if DESTINO.exists() else None

    if opciones.check:
        if actual == esperado:
            return 0
        print(
            "tokens.css está desincronizado con theme.py. "
            "Regenera con: uv run python -m scripts.build_tokens",
            file=sys.stderr,
        )
        return 1

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text(esperado, encoding="utf-8")
    print(f"escrito {DESTINO.relative_to(RAIZ)} — {len(COLORS_PANTALLA)} colores")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
