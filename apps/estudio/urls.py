from django.urls import path

from apps.estudio import views

app_name = "estudio"

urlpatterns = [
    path("estudio/", views.indice, name="indice"),
    path("estudio/<slug:slug>/", views.unidad, name="unidad"),
]
