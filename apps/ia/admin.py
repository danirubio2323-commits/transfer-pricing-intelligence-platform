"""`LlamadaLLM` en el panel, en solo lectura.

Es un registro contable, no un formulario. Poder editar a mano una fila de gasto
convertiría el tope en una sugerencia.
"""

from django.contrib import admin

from apps.ia.models import LlamadaLLM


@admin.register(LlamadaLLM)
class LlamadaLLMAdmin(admin.ModelAdmin):
    list_display = ("creada_el", "usuario", "proposito", "modelo", "coste_eur", "latencia_ms")
    list_filter = ("proposito", "modelo", "usuario")
    date_hierarchy = "creada_el"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return [campo.name for campo in self.model._meta.fields]
