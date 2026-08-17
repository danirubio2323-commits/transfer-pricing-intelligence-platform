"""Vistas del análisis: formulario, creación y detalle.

Ninguna importa el motor ni consulta `Caso` por su cuenta. El cálculo pasa por
`services.py` y la lectura con propietario por la guarda de `apps/comun`.
"""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.analisis.forms import CasoForm
from apps.analisis.services import crear_caso
from apps.comun.guardas import caso_del_usuario
from tp_domain.models import AnalysisResult


def formulario(request: HttpRequest) -> HttpResponse:
    return render(request, "analisis/form.html", {"formulario": CasoForm()})


def crear(request: HttpRequest) -> HttpResponse:
    """422 cuando no valida, 302 al detalle cuando sí. Nunca un 200 silencioso."""
    formulario_enviado = CasoForm(data=request.POST, usuario=request.user)
    if not formulario_enviado.is_valid():
        return render(request, "analisis/form.html", {"formulario": formulario_enviado}, status=422)

    caso = crear_caso(
        usuario=request.user,
        transaction=formulario_enviado.cleaned_data["transaction"],
        titulo=formulario_enviado.cleaned_data["titulo"],
    )
    return redirect("analisis:detalle", pk=caso.pk)


def detalle(request: HttpRequest, pk) -> HttpResponse:
    """La guarda es la única lectura: un caso ajeno responde 404, no 403."""
    caso = caso_del_usuario(request.user, pk)
    return render(
        request,
        "analisis/detalle.html",
        {"caso": caso, "resultado": AnalysisResult.model_validate(caso.payload)},
    )
