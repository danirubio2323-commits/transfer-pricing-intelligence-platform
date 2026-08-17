"""El contrato entre `theme.py` y el CSS.

Lo que se comprueba no es que el CSS sea bonito, sino que **no puede divergir**
de la paleta. Si alguien cambia un hexadecimal en un sitio y no en el otro, la
pantalla y el informe dejarían de representar lo mismo — y este proyecto existe
en parte para que representen lo mismo.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from infrastructure.theme import COLORS_PANTALLA

RAIZ = Path(__file__).resolve().parents[2]
TOKENS = RAIZ / "static" / "css" / "tokens.css"
APP = RAIZ / "static" / "css" / "app.css"


def test_cada_color_de_la_paleta_tiene_su_variable():
    css = TOKENS.read_text(encoding="utf-8")

    faltan = [
        clave
        for clave, valor in COLORS_PANTALLA.items()
        if f"--tpip-{clave.replace('_', '-')}: {valor};" not in css
    ]

    assert faltan == [], faltan


def test_app_css_no_contiene_ni_un_color_literal():
    """Un hexadecimal aquí es una divergencia esperando a ocurrir."""
    literales = re.findall(r"#[0-9A-Fa-f]{3,6}\b", APP.read_text(encoding="utf-8"))

    assert literales == [], literales


def test_el_generador_dice_que_esta_sincronizado():
    hecho = subprocess.run(
        [sys.executable, "-m", "scripts.build_tokens", "--check"], cwd=RAIZ, capture_output=True
    )

    assert hecho.returncode == 0, hecho.stderr.decode()


def test_el_generador_detecta_la_desincronizacion():
    """La comprobación PUEDE fallar; si no pudiera, no comprobaría nada."""
    original = TOKENS.read_text(encoding="utf-8")
    try:
        TOKENS.write_text(original + "\n/* alteración deliberada */\n", encoding="utf-8")
        hecho = subprocess.run(
            [sys.executable, "-m", "scripts.build_tokens", "--check"], cwd=RAIZ, capture_output=True
        )
        assert hecho.returncode == 1, hecho.returncode
    finally:
        TOKENS.write_text(original, encoding="utf-8")


def test_los_scripts_se_invocan_con_m_y_este_es_el_motivo():
    """Como ruta suelta no encuentra `infrastructure`. Documentado aquí para que
    nadie «simplifique» el -m y lo descubra a las once de la noche."""
    hecho = subprocess.run(
        [sys.executable, "scripts/build_tokens.py", "--check"], cwd=RAIZ, capture_output=True
    )

    assert hecho.returncode != 0
    assert b"infrastructure" in hecho.stderr


def test_el_movimiento_respeta_a_quien_pide_que_no_lo_haya():
    css = APP.read_text(encoding="utf-8")

    assert "prefers-reduced-motion" in css
