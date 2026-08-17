"""El arnés de evaluación: conjunto dorado y sus ejecuciones.

Sin esto los prompts se petrifican. Nadie se atreve a tocarlos porque no hay
forma de saber si un cambio mejora o empeora, y la regresión la acaba
descubriendo el usuario en un informe.

`EjecucionEvaluacion` guarda coste y latencias **junto a** la tasa de acierto a
propósito: una mejora de dos puntos que triplica el coste es una decisión que
hay que tomar con los tres números delante, no una mejora.
"""

from django.db import models


class CasoEvaluacion(models.Model):
    """Índice del conjunto dorado, que vive en evaluacion/casos/*.json."""

    id = models.CharField(max_length=60, primary_key=True)
    descripcion = models.CharField(max_length=200)
    entrada = models.JSONField()
    propiedades_esperadas = models.JSONField()
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "casos_evaluacion"
        ordering = ["id"]

    def __str__(self) -> str:
        return self.id


class EjecucionEvaluacion(models.Model):
    ejecutada_el = models.DateTimeField(auto_now_add=True, db_index=True)
    #: Sin el commit, una tasa de acierto no es reproducible: no se sabe contra
    #: qué código se midió.
    sha_commit = models.CharField(max_length=40)
    modelo = models.CharField(max_length=80)
    prompt_version = models.CharField(max_length=40)
    casos_totales = models.PositiveIntegerField()
    casos_acertados = models.PositiveIntegerField()
    tasa_acierto = models.FloatField()
    coste_total_eur = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    latencia_p50_ms = models.PositiveIntegerField()
    latencia_p95_ms = models.PositiveIntegerField()
    es_linea_base = models.BooleanField(default=False)
    detalle = models.JSONField()

    class Meta:
        db_table = "ejecuciones_evaluacion"
        ordering = ["-ejecutada_el"]

    def __str__(self) -> str:
        marca = " [línea base]" if self.es_linea_base else ""
        return f"{self.ejecutada_el:%Y-%m-%d %H:%M} · {self.tasa_acierto:.0%}{marca}"
