"""Índice del corpus jurídico.

**Reconstruible.** El `.md` en disco es la fuente de verdad y esta tabla solo lo
refleja: se puede borrar entera y volver a levantarla con un comando. Por eso el
identificador de la ficha es el mismo que usa el motor en su registro de
fuentes, y no hay tabla de traducción entre ambos.
"""

from django.db import models


class Ficha(models.Model):
    """Índice RECONSTRUIBLE del corpus. El .md en disco es la fuente de verdad."""

    id = models.CharField(max_length=80, primary_key=True)
    titulo = models.CharField(max_length=200)
    jurisdiccion = models.CharField(max_length=8, db_index=True)
    clase = models.CharField(max_length=24)
    rango_normativo = models.CharField(max_length=80)
    cita = models.TextField()
    pinpoint = models.CharField(max_length=120, blank=True)
    tipo_localizador = models.CharField(max_length=16)
    localizador = models.CharField(max_length=300)
    url_oficial = models.URLField(max_length=400, blank=True)
    confianza_verificacion = models.CharField(max_length=32, null=True, blank=True)
    verificada_el = models.DateField()
    ruta_fichero = models.CharField(max_length=300, unique=True)
    hash_fichero = models.CharField(max_length=64)
    actualizada_el = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fichas"
        ordering = ["jurisdiccion", "id"]

    def __str__(self) -> str:
        return f"[{self.jurisdiccion}] {self.titulo}"

    @property
    def es_resoluble(self) -> bool:
        """Si un tercero puede llegar a la norma por sí mismo."""
        return self.tipo_localizador in {"boe_id", "url"}
