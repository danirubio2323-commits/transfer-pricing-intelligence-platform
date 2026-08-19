"""Rutas raíz. En el paso 1 solo existe el panel de administración."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.comun.urls")),
    path("", include("apps.cuentas.urls")),
    path("", include("apps.analisis.urls")),
    path("", include("apps.corpus.urls")),
    path("", include("apps.estudio.urls")),
]
