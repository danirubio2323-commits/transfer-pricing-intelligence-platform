"""Restaura una copia y **comprueba que está entera**.

Una copia sin restaurar no es una copia: es un fichero del que nadie sabe nada.
Este comando restaura en un directorio de destino y compara los recuentos de las
ocho tablas contra el `.recuentos.json` que se escribió al copiar.

Tres códigos de salida, y la distinción importa igual que en el arnés:

- `0` — las ocho tablas coinciden.
- `1` — alguna difiere. Se nombra la tabla y los dos números.
- `2` — la copia o su fichero de recuentos no existen. No es una discrepancia:
  es que no hay nada que comparar.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.comun.tablas import TABLAS

NO_EXISTE = 2
NO_COINCIDE = 1


def _recuentos_de(fichero: Path) -> dict[str, int]:
    """Cuenta directamente sobre el fichero restaurado, sin pasar por Django."""
    conexion = sqlite3.connect(str(fichero))
    try:
        cifras = {}
        for tabla in TABLAS:
            try:
                cifras[tabla] = conexion.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]  # noqa: S608
            except sqlite3.Error:
                cifras[tabla] = 0
        return cifras
    finally:
        conexion.close()


class Command(BaseCommand):
    help = "Restaura una copia y verifica los recuentos de las ocho tablas."

    def add_arguments(self, parser):
        parser.add_argument("--copia", required=True)
        parser.add_argument("--destino", required=True)

    def handle(self, *args, **opciones):
        copia = Path(opciones["copia"])
        recuentos_json = copia.with_suffix(".recuentos.json")

        if not copia.exists():
            self.stderr.write(f"No existe la copia: {copia}")
            raise SystemExit(NO_EXISTE)
        if not recuentos_json.exists():
            self.stderr.write(
                f"No existe el fichero de recuentos: {recuentos_json}. "
                "Sin él, restaurar no demuestra que la copia esté entera."
            )
            raise SystemExit(NO_EXISTE)

        destino = Path(opciones["destino"])
        destino.mkdir(parents=True, exist_ok=True)
        restaurada = destino / copia.name

        entrada = sqlite3.connect(str(copia))
        salida = sqlite3.connect(str(restaurada))
        try:
            entrada.backup(salida)
        finally:
            salida.close()
            entrada.close()

        esperados = json.loads(recuentos_json.read_text(encoding="utf-8"))
        obtenidos = _recuentos_de(restaurada)

        discrepancias = [
            f"{TABLAS[t]} ({t}): esperadas {esperados.get(t, 0)}, restauradas {obtenidos[t]}"
            for t in TABLAS
            if esperados.get(t, 0) != obtenidos[t]
        ]
        if discrepancias:
            self.stderr.write("La restauración NO coincide:")
            for linea in discrepancias:
                self.stderr.write(f"  - {linea}")
            raise SystemExit(NO_COINCIDE)

        total = sum(obtenidos.values())
        self.stdout.write(
            self.style.SUCCESS(
                f"Restauración verificada en {restaurada} — las 8 tablas coinciden, {total} filas."
            )
        )
