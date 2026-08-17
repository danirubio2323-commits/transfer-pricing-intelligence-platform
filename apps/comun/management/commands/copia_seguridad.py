"""Copia de seguridad con la API de copia en línea de SQLite.

**No es un `cp`.** Copiar `db.sqlite3` mientras el proceso escribe produce un
fichero corrupto **sin avisar**: el fichero existe, tiene el tamaño esperado y
solo se descubre que no sirve el día que hace falta. La API de copia en línea
respeta las transacciones y da un fichero consistente.

Junto a la copia se escribe un `.recuentos.json` con las filas de cada una de las
ocho tablas. Ese fichero es lo que convierte la restauración en **verificable**:
sin él, restaurar solo demuestra que hay un fichero, no que esté completo.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from apps.comun.tablas import recuentos

DIRECTORIO = Path(settings.BASE_DIR) / "copias"


class Command(BaseCommand):
    help = "Copia la base de datos y registra los recuentos para poder verificarla."

    def add_arguments(self, parser):
        parser.add_argument(
            "--destino",
            default=None,
            help="Directorio donde escribir. Por defecto, copias/ del proyecto.",
        )

    def handle(self, *args, **opciones):
        # Se copia desde la CONEXIÓN VIVA, no abriendo el fichero por su ruta.
        # Es más correcto —respeta las transacciones en curso— y además es lo
        # único que funciona cuando la base está en memoria, como bajo pruebas.
        connection.ensure_connection()
        origen = connection.connection
        if origen is None:
            raise CommandError("No hay conexión a la base de datos.")

        destino = Path(opciones["destino"]) if opciones["destino"] else DIRECTORIO
        destino.mkdir(parents=True, exist_ok=True)

        marca = datetime.now().strftime("%Y%m%d-%H%M%S")
        fichero = destino / f"tpip-{marca}.sqlite3"

        # Los recuentos se toman ANTES de copiar, sobre la conexión viva: son los
        # que la copia debe reproducir.
        cifras = recuentos(connection)

        salida = sqlite3.connect(str(fichero))
        try:
            origen.backup(salida)  # API de copia en línea, no un cp
        finally:
            salida.close()

        fichero.with_suffix(".recuentos.json").write_text(
            json.dumps(cifras, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

        total = sum(cifras.values())
        self.stdout.write(
            self.style.SUCCESS(
                f"Copia escrita en {fichero.name} — {total} filas en 8 tablas. "
                f"Verifícala con: manage.py restaurar_copia --copia {fichero}"
            )
        )
