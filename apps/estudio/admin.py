"""`UnidadEstudio` en el panel, **editable**.

Al contrario que `Ficha`, esto se escribe desde aquí. Es la segunda vez que el
panel se cobra la decisión de elegir Django: un jurista no-ingeniero redacta y
publica su material sin tocar el repositorio ni abrir un editor de código.
"""

from django.contrib import admin

from apps.estudio.models import UnidadEstudio


@admin.register(UnidadEstudio)
class UnidadEstudioAdmin(admin.ModelAdmin):
    list_display = ("orden", "titulo", "publicada", "actualizada_el")
    list_filter = ("publicada",)
    list_editable = ("publicada",)
    search_fields = ("titulo", "resumen", "cuerpo")
    prepopulated_fields = {"slug": ("titulo",)}
    filter_horizontal = ("fichas",)
