"""Registro de `Caso` y `CasoContrastado` en el panel de administración.

`Caso` usa `Caso.todos` como consulta base a propósito: el administrador ve
también los borrados en suave, porque el borrado del usuario no es una
destrucción.

**Esto es lo que convierte el aviso de privacidad en un hecho comprobable en
lugar de una advertencia teórica**: quien administra ve los casos de todas las
cuentas, y por eso hay que declararlo, no dejarlo implícito.
"""

from django.contrib import admin
from django.utils.text import slugify

from apps.analisis.models import Caso, CasoContrastado


@admin.action(description="Curar como precedente (en borrador)")
def curar_como_precedente(modeladmin, request, queryset):
    """Copia el caso a un precedente nuevo, sin tocar el original.

    **Curar no desprivatiza.** El `payload` se copia; el caso sigue siendo de su
    dueño y sigue detrás de la guarda. Y el precedente sobrevive a que el
    original se borre, porque su copia es suya.

    Nace **en borrador**: publicar es una segunda decisión deliberada, no un
    efecto secundario de curar. El comentario se rellena después, porque es lo
    que convierte una fila en un precedente.
    """
    creados = 0
    for caso in queryset:
        base = slugify(caso.titulo)[:70] or "precedente"
        slug, sufijo = base, 1
        while CasoContrastado.objects.filter(slug=slug).exists():
            sufijo += 1
            slug = f"{base}-{sufijo}"

        CasoContrastado.objects.create(
            slug=slug,
            titulo=caso.titulo,
            caso_origen=caso,
            payload=caso.payload,  # copia congelada
            comentario_curador="",
            publicado=False,
            curado_por=request.user,
        )
        creados += 1

    modeladmin.message_user(
        request,
        f"{creados} precedente(s) creados en borrador. "
        "Añade el comentario del curador antes de publicarlos.",
    )


@admin.register(Caso)
class CasoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "usuario", "created_at", "engine_version", "esta_borrado")
    list_filter = ("usuario", "engine_version", "has_ai_explanation")
    search_fields = ("titulo",)
    readonly_fields = ("id", "created_at", "engine_version", "dataset_version")
    actions = [curar_como_precedente]

    def get_queryset(self, request):
        """Incluye los borrados en suave: el panel es el único sitio donde se ven."""
        return Caso.todos.all()


@admin.register(CasoContrastado)
class CasoContrastadoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "publicado", "curado_por", "creado_el")
    list_filter = ("publicado", "curado_por")
    search_fields = ("titulo", "comentario_curador")
    prepopulated_fields = {"slug": ("titulo",)}
    readonly_fields = ("payload", "caso_origen", "curado_por", "creado_el")
