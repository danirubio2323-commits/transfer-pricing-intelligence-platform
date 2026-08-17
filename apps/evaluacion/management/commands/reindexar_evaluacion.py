"""Reconstruye el conjunto dorado desde `evaluacion/casos/*.json`.

Idempotente, igual que el reindexado del corpus, y por el mismo motivo: los
ficheros en control de versiones son la fuente de verdad, y la tabla solo los
refleja. Un cambio del conjunto se revisa en un *pull request*, como el código.
"""

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.evaluacion.models import CasoEvaluacion

DIRECTORIO = Path(settings.BASE_DIR) / "evaluacion" / "casos"
OBLIGATORIOS = ("id", "descripcion", "entrada", "propiedades_esperadas")


class Command(BaseCommand):
    help = "Reconstruye el conjunto dorado desde evaluacion/casos/"

    def handle(self, *args, **opciones):
        casos = []
        for ruta in sorted(DIRECTORIO.glob("*.json")):
            datos = json.loads(ruta.read_text(encoding="utf-8"))
            faltan = [c for c in OBLIGATORIOS if c not in datos]
            if faltan:
                raise CommandError(f"{ruta.name}: faltan los campos {faltan}")
            casos.append(
                CasoEvaluacion(
                    id=datos["id"],
                    descripcion=datos["descripcion"],
                    entrada=datos["entrada"],
                    propiedades_esperadas=datos["propiedades_esperadas"],
                    activo=datos.get("activo", True),
                )
            )

        with transaction.atomic():
            CasoEvaluacion.objects.all().delete()
            CasoEvaluacion.objects.bulk_create(casos)

        self.stdout.write(self.style.SUCCESS(f"{len(casos)} casos dorados indexados."))
