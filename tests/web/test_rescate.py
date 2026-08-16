"""El código rescatado sigue siendo independiente del framework.

Esta migración se apoya en que el motor, la capa de IA y el generador de
informes no dependían de Streamlit y no dependen ahora de Django. Si algún día
alguien mete un `import django` dentro de `tp_domain/`, este fichero lo dice
antes de que esa dependencia se vuelva estructural y deje de poder deshacerse.
"""

from __future__ import annotations

import subprocess
import sys

PAQUETES_RESCATADOS = ("tp_domain", "ai", "infrastructure")


def test_los_paquetes_rescatados_se_importan_sin_django_ni_streamlit():
    """Se importan en un intérprete limpio, sin configurar Django."""
    guion = (
        "import importlib, sys; "
        f"[importlib.import_module(m) for m in {PAQUETES_RESCATADOS!r}]; "
        "assert 'streamlit' not in sys.modules, 'alguien importa streamlit'; "
        "assert 'django' not in sys.modules, 'alguien importa django'; "
        "print('ok')"
    )
    resultado = subprocess.run([sys.executable, "-c", guion], capture_output=True, text=True)

    assert resultado.returncode == 0, resultado.stderr
    assert "ok" in resultado.stdout


def test_el_registro_cerrado_de_fuentes_conserva_sus_cinco_entradas():
    """El motor solo puede citar lo que ya está en el registro."""
    from tp_domain.sources import SOURCE_REGISTRY

    assert len(SOURCE_REGISTRY) == 5
