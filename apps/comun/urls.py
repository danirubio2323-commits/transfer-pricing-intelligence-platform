from django.urls import path
from django.views.generic import TemplateView

app_name = "comun"

urlpatterns = [
    path("privacidad/", TemplateView.as_view(template_name="privacidad.html"), name="privacidad"),
]
