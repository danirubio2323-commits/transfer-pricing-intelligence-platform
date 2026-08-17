"""Reconstruye el índice del corpus desde los ficheros en disco.

Idempotente por construcción: se lee todo, se vacía la tabla y se vuelve a
llenar, dentro de una transacción. Ejecutarlo dos veces deja exactamente el
mismo estado, y si una ficha está incompleta no queda nada a medias.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.corpus.indexador import FichaIncompleta, RutaFueraDelCorpus, recorrer_corpus
from apps.corpus.models import Ficha


class Command(BaseCommand):
    help = "Reconstruye la tabla de fichas desde documentation/tax-research/"

    def handle(self, *args, **opciones):
        try:
            filas = recorrer_corpus()
        except (FichaIncompleta, RutaFueraDelCorpus) as fallo:
            # Nada se ha escrito todavía: la tabla queda como estaba.
            raise CommandError(str(fallo)) from fallo

        with transaction.atomic():
            Ficha.objects.all().delete()
            Ficha.objects.bulk_create(Ficha(**fila.__dict__) for fila in filas)

        self.stdout.write(self.style.SUCCESS(f"{len(filas)} fichas indexadas."))
