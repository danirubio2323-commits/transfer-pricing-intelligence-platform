"""Las ocho tablas del sistema, en un solo sitio.

La copia de seguridad y su verificación necesitan la misma lista, y tenerla dos
veces garantiza que un día diverjan: se añadiría una tabla al modelo, se
copiaría entera, y la verificación seguiría dando por buena una restauración a
la que le falta.
"""

from __future__ import annotations

#: Nombre de tabla → etiqueta legible. El orden es el del apartado 4.
TABLAS: dict[str, str] = {
    "usuarios": "Cuentas",
    "casos": "Casos",
    "casos_contrastados": "Precedentes",
    "fichas": "Corpus",
    "unidades_estudio": "Unidades de estudio",
    "llamadas_llm": "Llamadas al modelo",
    "casos_evaluacion": "Conjunto dorado",
    "ejecuciones_evaluacion": "Ejecuciones del arnés",
}


def recuentos(conexion) -> dict[str, int]:
    """Filas de cada tabla. Una tabla que aún no existe cuenta como 0, no falla."""
    cifras = {}
    with conexion.cursor() as cursor:
        for tabla in TABLAS:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")  # noqa: S608 — lista cerrada
                cifras[tabla] = cursor.fetchone()[0]
            except Exception:  # noqa: BLE001 — tabla ausente en una base a medias
                cifras[tabla] = 0
    return cifras
