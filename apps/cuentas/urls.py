from django.urls import path

from apps.cuentas import views

app_name = "cuentas"

urlpatterns = [
    path("entrar/", views.entrar, name="entrar"),
    path("salir/", views.salir, name="salir"),
    path("cuenta/contrasena/", views.cambiar_contrasena, name="contrasena"),
]
