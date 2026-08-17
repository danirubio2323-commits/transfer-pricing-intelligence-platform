"""Publicación del corpus: índice y ficha renderizada.

La cabecera de cada ficha sale del índice —título, rango, cita, localizador,
confianza y fecha— y el cuerpo se renderiza desde el `.md`. Así lo que se
muestra como dato estructurado viene de la tabla, y lo que se muestra como
prosa viene del fichero, sin que ninguno tenga que reinterpretar al otro.

La comprobación de que la ruta no se sale del corpus vive en el indexador, no
aquí: es la misma que usa el reindexado, y tener dos sería tener una que algún
día diverge.
"""

from __future__ import annotations

import markdown as md
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render

from apps.corpus.indexador import RutaFueraDelCorpus, ruta_del_corpus
from apps.corpus.models import Ficha

#: Extensiones del renderizador. Sin HTML crudo: el corpus es texto, no plantilla.
EXTENSIONES = ["tables", "fenced_code", "toc"]


def indice(request: HttpRequest) -> HttpResponse:
    jurisdiccion = request.GET.get("jurisdiccion", "").strip().upper()

    fichas = Ficha.objects.all()
    if jurisdiccion:
        fichas = fichas.filter(jurisdiccion=jurisdiccion)

    return render(
        request,
        "corpus/indice.html",
        {
            "fichas": fichas,
            "jurisdiccion": jurisdiccion,
            "jurisdicciones": sorted(
                Ficha.objects.values_list("jurisdiccion", flat=True).distinct()
            ),
        },
    )


def ficha(request: HttpRequest, ruta: str) -> HttpResponse:
    """`400` si la ruta se sale del corpus, `404` si no existe. Nunca un 500."""
    # El orden importa: primero se valida la ruta, después se busca. Un intento
    # de salirse del corpus tiene que dar 400 y no 404, porque no es un «no
    # encontrado» — y confundirlos haría del 404 un detector de qué hay fuera.
    try:
        fichero = ruta_del_corpus(f"{ruta}.md")
    except RutaFueraDelCorpus:
        return HttpResponseBadRequest("La ruta solicitada queda fuera del corpus.")

    registro = get_object_or_404(Ficha, ruta_fichero=f"{ruta}.md")

    import frontmatter

    documento = frontmatter.load(fichero)
    cuerpo = md.markdown(documento.content, extensions=EXTENSIONES)

    return render(request, "corpus/ficha.html", {"ficha": registro, "cuerpo": cuerpo})
