"""Accesibilidad y transparencia, comprobadas sobre el HTML renderizado.

**Sobre el medio.** Aquí se comprueba lo que un análisis del HTML puede decidir:
que existan los landmarks, que cada control tenga etiqueta, que los errores sean
texto y no solo color, que el SVG se anuncie. Lo que este medio **no** puede
decidir —el orden real de tabulación, lo que dice un lector de pantalla, el
reflujo a 320 px— no se afirma en este fichero: vive en los gates manuales.

Afirmar aquí lo segundo sería peor que no comprobarlo, porque daría por
verificado lo que nadie ha mirado.
"""

from __future__ import annotations

import re

import pytest
from django.urls import reverse

from apps.analisis.models import Caso

VALIDO = {
    "titulo": "",
    "description": "Canon por licencia de tecnología",
    "payer_country": "ES",
    "recipient_country": "DE",
    "transaction_type": "royalty",
    "industry": "software",
    "amount_eur": "1000000",
    "rate_percent": "8.0",
    "effective_date": "2026-01-01",
}


@pytest.fixture
def autenticado(client, usuario):
    client.force_login(usuario)
    return client


@pytest.fixture
def detalle(autenticado):
    autenticado.post(reverse("analisis:crear"), VALIDO)
    caso = Caso.objects.get()
    return autenticado.get(reverse("analisis:detalle", kwargs={"pk": caso.pk})).content.decode()


def _paginas(cliente):
    """Las pantallas autenticadas que existen hoy."""
    return {
        "formulario": cliente.get(reverse("analisis:formulario")).content.decode(),
        "listado": cliente.get("/casos/").content.decode(),
        "fuentes": cliente.get(reverse("corpus:indice")).content.decode(),
        "estudio": cliente.get(reverse("estudio:indice")).content.decode(),
        "privacidad": cliente.get(reverse("comun:privacidad")).content.decode(),
    }


# ---------------------------------------------------------------------------
# El esqueleto, en TODAS las páginas
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_todas_las_paginas_traen_el_esqueleto_accesible(autenticado):
    for nombre, html in _paginas(autenticado).items():
        assert '<html lang="es"' in html, nombre
        assert html.count("<h1") == 1, nombre
        assert '<main id="contenido"' in html, nombre
        assert "<header" in html, nombre
        assert '<footer role="contentinfo"' in html, nombre


@pytest.mark.django_db
def test_el_enlace_de_salto_es_el_primer_elemento_enfocable(autenticado):
    """Quien navega con teclado no debe recorrer la cabecera entera para llegar
    a lo que ha venido a leer."""
    for nombre, html in _paginas(autenticado).items():
        cuerpo = html[html.index("<body") :]
        primer_enfocable = re.search(r"<(a|button|input|select|textarea)\b", cuerpo)
        assert primer_enfocable is not None, nombre
        trozo = cuerpo[primer_enfocable.start() : primer_enfocable.start() + 200]
        assert 'href="#contenido"' in trozo, f"{nombre}: {trozo[:80]}"


# ---------------------------------------------------------------------------
# El formulario
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_cada_control_tiene_su_etiqueta(autenticado):
    """Cero controles sin etiqueta: un campo sin nombre no se puede rellenar a ciegas."""
    html = autenticado.get(reverse("analisis:formulario")).content.decode()

    etiquetados = set(re.findall(r'<label for="([^"]+)"', html))
    controles = set(re.findall(r'<(?:input|select|textarea)[^>]*\bid="([^"]+)"', html))
    # Los campos ocultos (CSRF) no llevan etiqueta y no deben exigirla.
    controles -= set(re.findall(r'<input[^>]*type="hidden"[^>]*id="([^"]+)"', html))

    assert controles - etiquetados == set(), controles - etiquetados


@pytest.mark.django_db
def test_los_errores_son_texto_y_no_solo_color(autenticado):
    """Un error señalado solo con un borde rojo no existe para quien no lo ve."""
    html = autenticado.post(
        reverse("analisis:crear"), {**VALIDO, "recipient_country": "ES"}
    ).content.decode()

    assert 'role="alert"' in html
    assert "jurisdicciones distintas" in html


@pytest.mark.django_db
def test_el_error_de_un_campo_queda_referenciado_desde_el_campo(autenticado):
    """`aria-describedby` es lo que une el control con su mensaje."""
    html = autenticado.post(
        reverse("analisis:crear"), {**VALIDO, "rate_percent": "101"}
    ).content.decode()

    assert "aria-describedby" in html


@pytest.mark.django_db
def test_el_formulario_conserva_lo_ya_escrito_tras_un_error(autenticado):
    """Reescribir nueve campos por un fallo en uno es una barrera, no un detalle."""
    html = autenticado.post(
        reverse("analisis:crear"), {**VALIDO, "recipient_country": "ES"}
    ).content.decode()

    assert "Canon por licencia de tecnología" in html


# ---------------------------------------------------------------------------
# El gráfico
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_el_grafico_del_rango_se_anuncia_con_texto(detalle):
    """Sin `<title>`, la imagen es un hueco mudo para un lector de pantalla."""
    # Se busca DENTRO del <svg>: el <title> de la cabecera es otra cosa y
    # aceptarlo daría por bueno un gráfico mudo.
    svg = re.search(r"<svg\b.*?</svg>", detalle, re.S)
    assert svg is not None
    grafico = svg.group(0)

    assert 'role="img"' in grafico

    titulo = re.search(r"<title>(.*?)</title>", grafico, re.S)
    assert titulo is not None
    assert "Rango de plena competencia" in titulo.group(1)
    assert "mediana" in titulo.group(1)


# ---------------------------------------------------------------------------
# El aviso de privacidad
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_el_aviso_de_privacidad_esta_en_el_pie_de_toda_pagina(autenticado):
    """No es una advertencia teórica: quien administra ve los casos de todos."""
    for nombre, html in _paginas(autenticado).items():
        pie = html[html.index('<footer role="contentinfo"') :]
        assert "permiso de administración" in pie, nombre
        assert "cualquier" in pie, nombre


@pytest.mark.django_db
def test_el_aviso_aparece_tambien_junto_al_formulario(autenticado):
    """Decirlo solo en el pie sería decirlo tarde: aquí es cuando se va a escribir el dato."""
    html = autenticado.get(reverse("analisis:formulario")).content.decode()

    principal = html[html.index('<main id="contenido"') : html.index("<footer")]

    assert "permiso de administración" in principal


@pytest.mark.django_db
def test_la_pagina_de_privacidad_dice_que_se_guarda_y_como_se_borra(autenticado):
    html = autenticado.get(reverse("comun:privacidad")).content.decode()

    for termino in ("se guarda", "borr"):
        assert termino in html.lower(), termino


# ---------------------------------------------------------------------------
# El movimiento y el foco
# ---------------------------------------------------------------------------


def _css() -> str:
    from pathlib import Path

    return (Path(__file__).resolve().parents[2] / "static" / "css" / "app.css").read_text(
        encoding="utf-8"
    )


def test_el_foco_deja_un_anillo_visible():
    """Quitar el foco deja la aplicación inservible con teclado."""
    css = _css()

    assert ":focus-visible" in css
    assert "outline-offset" in css


def test_el_movimiento_se_anade_solo_a_quien_no_ha_pedido_lo_contrario():
    """Animar por defecto y desactivar después deja colarse toda transición que
    se olvide de la excepción. Aquí el punto de partida es la quietud."""
    css = _css()

    assert "prefers-reduced-motion: no-preference" in css

    # Y ninguna `transition` fuera de ese bloque.
    patron = (
        "@media " + re.escape("(prefers-reduced-motion: no-preference)") + ".*?" + chr(10) + "}"
    )
    bloque = re.search(patron, css, re.S)
    assert bloque is not None
    fuera = css[: bloque.start()] + css[bloque.end() :]

    assert "transition:" not in fuera


def test_los_objetivos_de_puntero_tienen_un_suelo():
    css = _css()

    assert "min-height: 24px" in css


def test_las_tablas_anchas_se_desplazan_en_su_contenedor_y_no_en_la_pagina():
    """Mover TODA la pantalla en horizontal para leer una columna es la barrera
    que este contenedor evita."""
    from pathlib import Path

    assert "overflow-x: auto" in _css()

    raiz = Path(__file__).resolve().parents[2] / "templates"
    for plantilla in raiz.rglob("*.html"):
        html = plantilla.read_text(encoding="utf-8")
        if "<table>" in html:
            assert 'class="tabla-ancha"' in html, plantilla.name


# ---------------------------------------------------------------------------
# Nada de sintaxis de plantilla en la página
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_ninguna_pagina_imprime_sintaxis_de_plantilla(autenticado):
    """Django solo admite `{# … #}` en UNA línea; multilínea se renderiza literal.

    Salía impreso en el HTML —el aviso de privacidad venía precedido de su
    propio comentario— y ninguna prueba lo veía, porque todas afirmaban
    `«el texto esperado está»` y ninguna `«no hay nada que no debiera estar»`.
    """
    for nombre, html in _paginas(autenticado).items():
        for resto in ("{#", "#}", "{%", "%}", "{{", "}}"):
            assert resto not in html, f"{nombre}: queda {resto} sin procesar"


def test_ninguna_plantilla_usa_un_comentario_multilinea_de_almohadilla():
    """La forma correcta para varias líneas es `{% comment %}`."""
    from pathlib import Path

    raiz = Path(__file__).resolve().parents[2] / "templates"
    culpables = [
        f.name
        for f in raiz.rglob("*.html")
        for m in re.finditer(r"\{#.*?#\}", f.read_text(encoding="utf-8"), re.S)
        if "\n" in m.group(0)
    ]

    assert culpables == []


@pytest.mark.django_db
def test_el_titulo_de_la_pestana_es_texto_y_nada_mas(autenticado, detalle):
    """El `<title>` es lo primero que anuncia un lector de pantalla y lo que se
    lee en la pestaña y en un marcador. Un bloque de HTML metido ahí por un
    pegado suelto no rompe nada visible en la página, y por eso hay que mirarlo.
    """
    paginas = {**_paginas(autenticado), "detalle": detalle}

    for nombre, html in paginas.items():
        titulo = re.search(r"<title>(.*?)</title>", html, re.S)
        assert titulo is not None, nombre
        texto = titulo.group(1)

        assert "<" not in texto and ">" not in texto, f"{nombre}: {texto[:80]}"
        assert texto.strip() == texto.strip().splitlines()[0].strip(), nombre
        assert texto.strip().endswith("TPIP"), nombre
