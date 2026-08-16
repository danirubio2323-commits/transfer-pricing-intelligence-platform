"""Rutas raíz. En el paso 1 solo existe el panel de administración."""

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]
