"""Material de estudio. Entidad separada de `Ficha`, y la separación es el punto.

**Una ficha es fuente citable con rango normativo; una unidad de estudio es
material de aprendizaje.** Fusionarlas con una bandera acabaría, tarde o
temprano, con un informe citando material didáctico como si fuera Derecho — y
ese error no se detecta leyendo el informe, porque parece una cita más.

Por eso no comparten tabla, ni identificador, ni registro. Una unidad de estudio
puede enlazar a las fichas que estudia; nunca al revés.
"""

from django.db import models


class UnidadEstudio(models.Model):
    """Material didáctico. NUNCA es fuente citable: no aparece en ningún informe."""

    slug = models.SlugField(max_length=80, unique=True)
    titulo = models.CharField(max_length=200)
    resumen = models.CharField(max_length=300)
    cuerpo = models.TextField()
    orden = models.PositiveIntegerField(default=0)
    publicada = models.BooleanField(default=False)
    fichas = models.ManyToManyField("corpus.Ficha", blank=True, related_name="unidades")
    creada_el = models.DateTimeField(auto_now_add=True)
    actualizada_el = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "unidades_estudio"
        ordering = ["orden", "titulo"]
        indexes = [models.Index(fields=["publicada", "orden"])]

    def __str__(self) -> str:
        return self.titulo
