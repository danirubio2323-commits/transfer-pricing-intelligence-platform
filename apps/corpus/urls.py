from django.urls import path

from apps.corpus import views

app_name = "corpus"

urlpatterns = [
    path("fuentes/", views.indice, name="indice"),
    path("fuentes/<path:ruta>/", views.ficha, name="ficha"),
]
