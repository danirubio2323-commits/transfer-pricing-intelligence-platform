"""Vistas del análisis: formulario, creación y detalle.

Ninguna importa el motor ni consulta `Caso` por su cuenta. El cálculo pasa por
`services.py` y la lectura con propietario por la guarda de `apps/comun`.
"""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from infrastructure.report import render_report_bytes

from apps.analisis.forms import CasoForm
from apps.analisis.presentacion import tarjetas_de_jurisdiccion
from apps.analisis.services import crear_caso
from apps.comun.guardas import caso_del_usuario
from infrastructure.charts import benchmark_range_svg
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
    resultado = AnalysisResult.model_validate(caso.payload)
    return render(
        request,
        "analisis/detalle.html",
        {
            "caso": caso,
            "resultado": resultado,
            # El gráfico y las tarjetas se preparan aquí: la plantilla pinta,
            # no decide. Un `{% if %}` sobre un enum es lógica sin probar.
            "grafico": benchmark_range_svg(resultado),
            "tarjetas": tarjetas_de_jurisdiccion(resultado),
        },
    )


def informe(request: HttpRequest, pk) -> HttpResponse:
    """Regenera el PDF desde el caso persistido. Sin red y sin recalcular.

    El documento sale del `payload` guardado, no de volver a ejecutar el motor:
    si se recalculase, dos descargas del mismo caso podrían diferir, y con la
    capa de IA enchufada (paso 17) el texto redactado sería otro. Lo que el
    usuario se lleva tiene que ser lo que vio en pantalla.
    """
    caso = caso_del_usuario(request.user, pk)
    resultado = AnalysisResult.model_validate(caso.payload)

    respuesta = HttpResponse(render_report_bytes(resultado), content_type="application/pdf")
    respuesta["Content-Disposition"] = f'attachment; filename="tpip-{caso.pk}.pdf"'
    return respuesta
