"""`Ficha` en el panel, en solo lectura.

Una edición aquí se perdería en el siguiente reindexado. Y una tabla que miente
sobre lo que hay en disco es peor que una tabla que no existe: el corpus se
edita en Obsidian, que es donde vive la fuente de verdad.
"""

from django.contrib import admin

from apps.corpus.models import Ficha


@admin.register(Ficha)
class FichaAdmin(admin.ModelAdmin):
    list_display = ("id", "jurisdiccion", "clase", "tipo_localizador", "verificada_el")
    list_filter = ("jurisdiccion", "clase", "tipo_localizador", "confianza_verificacion")
    search_fields = ("titulo", "cita", "localizador")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return [campo.name for campo in self.model._meta.fields]
