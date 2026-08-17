from django.urls import path

from apps.analisis import views

app_name = "analisis"

urlpatterns = [
    path("", views.formulario, name="formulario"),
    path("casos/", views.crear, name="crear"),
    path("casos/<uuid:pk>/", views.detalle, name="detalle"),
]
