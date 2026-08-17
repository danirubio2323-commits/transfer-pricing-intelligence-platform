from django.urls import path

from apps.analisis import views

app_name = "analisis"

urlpatterns = [
    path("", views.formulario, name="formulario"),
    # Una colección, dos verbos: GET lista, POST crea. El reparto lo hace la
    # vista, porque Django enruta por camino y no por método.
    path("casos/", views.casos, name="lista"),
    path("casos/", views.casos, name="crear"),
    path("casos/<uuid:pk>/", views.detalle, name="detalle"),
    path("casos/<uuid:pk>/informe.pdf", views.informe, name="informe"),
    path("casos/<uuid:pk>/borrar/", views.borrar, name="borrar"),
]
