"""Vistas del análisis: formulario, creación y detalle.

Ninguna importa el motor ni consulta `Caso` por su cuenta. El cálculo pasa por
`services.py` y la lectura con propietario por la guarda de `apps/comun`.
"""

from __future__ import annotations

from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render

from apps.analisis.forms import CasoForm
from apps.analisis.models import CasoContrastado
from apps.analisis.presentacion import fuentes_enlazadas, tarjetas_de_jurisdiccion
from apps.analisis.services import crear_caso
from apps.comun.consultas import ORDEN_POR_DEFECTO, ORDENES, casos_de
from apps.comun.escrituras import borrar_caso_de
from apps.comun.guardas import caso_del_usuario
from infrastructure.charts import benchmark_range_svg
from infrastructure.report import render_report_bytes
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
            "fuentes": fuentes_enlazadas(resultado),
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


#: Tope de página. Lo decide el servidor: un cliente no puede pedir la tabla
#: entera pasando un número grande.
POR_PAGINA_POR_DEFECTO = 20
POR_PAGINA_MAXIMO = 100


def _por_pagina(peticion: HttpRequest) -> int:
    """Recorta al máximo del servidor. Un valor no numérico cae al defecto."""
    try:
        pedido = int(peticion.GET.get("por_pagina", POR_PAGINA_POR_DEFECTO))
    except (TypeError, ValueError):
        return POR_PAGINA_POR_DEFECTO
    return max(1, min(pedido, POR_PAGINA_MAXIMO))


def lista(request: HttpRequest) -> HttpResponse:
    """Un caso que se guarda pero no se encuentra es un caso perdido."""
    texto = request.GET.get("q", "").strip()
    jurisdiccion = request.GET.get("jurisdiccion", "").strip()
    orden = request.GET.get("orden", ORDEN_POR_DEFECTO)

    consulta = casos_de(request.user, texto=texto, jurisdiccion=jurisdiccion, orden=orden)
    paginador = Paginator(consulta, _por_pagina(request))
    # `get_page` tolera una página fuera de rango y una no numérica: devuelve la
    # última válida en vez de un 500, que es lo que haría `page()`.
    pagina = paginador.get_page(request.GET.get("pagina"))

    return render(
        request,
        "analisis/lista.html",
        {
            "pagina": pagina,
            "texto": texto,
            "jurisdiccion": jurisdiccion,
            "orden": orden if orden in ORDENES else ORDEN_POR_DEFECTO,
            "ordenes": ORDENES,
            # Dos vacíos distintos: «aún no has analizado nada» no es lo mismo
            # que «tu búsqueda no encuentra nada», y confundirlos desorienta.
            "hay_filtro": bool(texto or jurisdiccion),
        },
    )


def borrar(request: HttpRequest, pk) -> HttpResponse:
    """Borrado suave, y solo por POST: con GET, un enlace borraría al pulsarlo."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    borrar_caso_de(request.user, caso_del_usuario(request.user, pk))
    return redirect("analisis:lista")


def casos(request: HttpRequest) -> HttpResponse:
    """`/casos/` es una sola ruta con dos verbos, como manda §5.

    GET lista, POST crea. Django enruta por camino y no por método, así que el
    reparto se hace aquí en vez de inventar dos URLs distintas para lo que
    conceptualmente es una colección.
    """
    if request.method == "POST":
        return crear(request)
    return lista(request)


def contrastados(request: HttpRequest) -> HttpResponse:
    """La biblioteca de precedentes, visible para toda cuenta autenticada."""
    return render(
        request,
        "analisis/contrastados.html",
        {"precedentes": CasoContrastado.objects.filter(publicado=True)},
    )


def contrastado(request: HttpRequest, slug: str) -> HttpResponse:
    """Un precedente. Sin publicar, 404 — salvo para quien administra."""
    consulta = CasoContrastado.objects.all()
    if not request.user.is_staff:
        consulta = consulta.filter(publicado=True)

    precedente = get_object_or_404(consulta, slug=slug)
    # Se lee igual que un caso: mismo payload, mismos parciales.
    resultado = AnalysisResult.model_validate(precedente.payload)

    return render(
        request,
        "analisis/contrastado.html",
        {
            "precedente": precedente,
            "resultado": resultado,
            "grafico": benchmark_range_svg(resultado),
            "tarjetas": tarjetas_de_jurisdiccion(resultado),
            "fuentes": fuentes_enlazadas(resultado),
        },
    )
