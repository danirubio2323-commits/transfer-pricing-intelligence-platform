"""Registro de `Caso` en el panel de administración.

Usa `Caso.todos` como consulta base a propósito: el administrador ve también los
borrados en suave, porque el borrado del usuario no es una destrucción.

**Esto es lo que convierte el aviso de privacidad en un hecho comprobable en
lugar de una advertencia teórica**: quien administra ve los casos de todas las
cuentas, y por eso hay que declararlo, no dejarlo implícito.
"""

from django.contrib import admin

from apps.analisis.models import Caso


@admin.register(Caso)
class CasoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "usuario", "created_at", "engine_version", "esta_borrado")
    list_filter = ("usuario", "engine_version", "has_ai_explanation")
    search_fields = ("titulo",)
    readonly_fields = ("id", "created_at", "engine_version", "dataset_version")

    def get_queryset(self, request):
        """Incluye los borrados en suave: el panel es el único sitio donde se ven."""
        return Caso.todos.all()
