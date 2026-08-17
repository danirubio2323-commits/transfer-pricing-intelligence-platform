"""El caso: un análisis ejecutado y guardado.

`payload` es la fuente de verdad —el volcado completo de `AnalysisResult`, el
objeto de dominio rescatado— y los cuatro campos desnormalizados se derivan de
él al guardar, nunca al revés. Eso permite filtrar por versión de motor sin
abrir el JSON, sin que puedan contradecirse.

Todo lo que lea un caso lo rehidrata con `AnalysisResult.model_validate` y
trabaja sobre el objeto de dominio. Ninguna plantilla lee claves sueltas del
`payload`: si el volcado cambia de forma, pydantic lo dice en el acto en vez de
producir una pantalla medio vacía.
"""

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models


class CasoVivoManager(models.Manager):
    """Gestor por defecto: las filas borradas en suave no existen para nadie
    salvo para el panel de administración."""

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class Caso(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="casos",
        db_index=True,
    )
    titulo = models.CharField(max_length=160, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    engine_version = models.CharField(max_length=16)
    dataset_version = models.CharField(max_length=16)
    has_ai_explanation = models.BooleanField(default=False)
    payload = models.JSONField()

    objects = CasoVivoManager()
    todos = models.Manager()

    class Meta:
        db_table = "casos"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["usuario", "-created_at"])]
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "titulo"],
                condition=models.Q(deleted_at__isnull=True),
                name="titulo_unico_por_usuario_entre_casos_vivos",
            )
        ]

    def __str__(self) -> str:
        return self.titulo

    def save(self, *args, **kwargs):
        """Los tres campos desnormalizados salen del `payload`, no al revés."""
        if isinstance(self.payload, dict):
            self.engine_version = self.payload.get("engine_version", "")
            self.dataset_version = self.payload.get("dataset_version", "")
            self.has_ai_explanation = self.payload.get("ai_explanation") is not None
        super().save(*args, **kwargs)

    @property
    def esta_borrado(self) -> bool:
        return self.deleted_at is not None


class CasoContrastado(models.Model):
    """Un precedente curado: un caso congelado que sirve de referencia a todos.

    **Curar no desprivatiza.** El `payload` se COPIA, no se comparte: el caso
    original sigue siendo de su dueño y sigue detrás de la guarda. Y el
    precedente sobrevive a que el original se borre, porque su copia es suya.

    `comentario_curador` no es opcional en la práctica: un precedente sin la
    razón por la que lo es no es un precedente, es una fila más.
    """

    slug = models.SlugField(max_length=80, unique=True)
    titulo = models.CharField(max_length=160)
    #: SET_NULL y no CASCADE: si el caso de origen desaparece, el precedente
    #: sigue en pie con su copia intacta.
    caso_origen = models.ForeignKey(Caso, null=True, blank=True, on_delete=models.SET_NULL)
    payload = models.JSONField()
    comentario_curador = models.TextField()
    publicado = models.BooleanField(default=False)
    curado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    creado_el = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "casos_contrastados"
        ordering = ["-creado_el"]

    def __str__(self) -> str:
        return self.titulo
