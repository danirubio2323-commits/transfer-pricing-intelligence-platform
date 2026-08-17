"""El arnés en el panel, en solo lectura.

Igual que el registro de llamadas: es evidencia de lo que pasó, no un formulario.
Editar a mano una tasa de acierto convertiría la puerta de regresión en un
adorno.
"""

from django.contrib import admin

from apps.evaluacion.models import CasoEvaluacion, EjecucionEvaluacion


class SoloLectura(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return [campo.name for campo in self.model._meta.fields]


@admin.register(CasoEvaluacion)
class CasoEvaluacionAdmin(SoloLectura):
    list_display = ("id", "descripcion", "activo")
    list_filter = ("activo",)


@admin.register(EjecucionEvaluacion)
class EjecucionEvaluacionAdmin(SoloLectura):
    list_display = (
        "ejecutada_el",
        "tasa_acierto",
        "casos_acertados",
        "casos_totales",
        "coste_total_eur",
        "latencia_p95_ms",
        "es_linea_base",
    )
    list_filter = ("es_linea_base", "modelo")
    date_hierarchy = "ejecutada_el"
