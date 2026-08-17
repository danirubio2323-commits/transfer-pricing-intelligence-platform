"""Índice y detalle del material de estudio.

Una unidad sin publicar responde 404 aunque se pida por su dirección exacta: un
borrador no es contenido, y distinguir «existe pero no está publicada» de «no
existe» solo serviría para que alguien supiera qué estás escribiendo.
"""

from __future__ import annotations

import markdown as md
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from apps.estudio.models import UnidadEstudio

EXTENSIONES = ["tables", "fenced_code", "toc"]


def indice(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "estudio/indice.html",
        {"unidades": UnidadEstudio.objects.filter(publicada=True)},
    )


def unidad(request: HttpRequest, slug: str) -> HttpResponse:
    unidad = get_object_or_404(UnidadEstudio, slug=slug, publicada=True)
    return render(
        request,
        "estudio/unidad.html",
        {
            "unidad": unidad,
            "cuerpo": md.markdown(unidad.cuerpo, extensions=EXTENSIONES),
            "fichas": unidad.fichas.all(),
        },
    )
