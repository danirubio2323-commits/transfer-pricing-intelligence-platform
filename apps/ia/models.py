"""Registro contable de las llamadas al modelo.

Los cuatro contadores de tokens vienen **reportados por el proveedor**. Nunca se
estiman aquí: un recuento propio diverge del que se factura, y entonces el tope
estaría vigilando un número que no es el que se paga.
"""

from django.conf import settings
from django.db import models


class LlamadaLLM(models.Model):
    """Uso REPORTADO POR EL PROVEEDOR. Nunca se estiman tokens contándolos aquí."""

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_index=True)
    caso = models.ForeignKey("analisis.Caso", null=True, blank=True, on_delete=models.SET_NULL)
    creada_el = models.DateTimeField(auto_now_add=True, db_index=True)
    #: `explicacion` o `evaluacion`. El arnés no debe consumir el tope de nadie.
    proposito = models.CharField(max_length=32, db_index=True)
    modelo = models.CharField(max_length=80)
    prompt_version = models.CharField(max_length=40)
    tokens_entrada = models.PositiveIntegerField(default=0)
    tokens_salida = models.PositiveIntegerField(default=0)
    tokens_cache_escritura = models.PositiveIntegerField(default=0)
    tokens_cache_lectura = models.PositiveIntegerField(default=0)
    coste_eur = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    latencia_ms = models.PositiveIntegerField()
    razon_finalizacion = models.CharField(max_length=32, blank=True)
    error = models.CharField(max_length=200, blank=True)
    intento = models.PositiveSmallIntegerField()

    class Meta:
        db_table = "llamadas_llm"
        ordering = ["-creada_el"]
        indexes = [models.Index(fields=["usuario", "creada_el"])]

    def __str__(self) -> str:
        return f"{self.modelo} · {self.proposito} · {self.coste_eur} €"
