"""El módulo de estudio, y la invariante que justifica que sea otra entidad.

**Una ficha es fuente citable con rango normativo; una unidad de estudio es
material de aprendizaje.** Si se fusionaran con una bandera, tarde o temprano un
informe citaría material didáctico como si fuera Derecho — y ese error no se
detecta leyendo el informe, porque parece una cita más.

Por eso la prueba que de verdad importa aquí no es que el índice liste bien: es
que **ninguna unidad de estudio puede alcanzar un informe**.
"""

from __future__ import annotations

import datetime as dt

import pytest
from django.core.management import call_command
from django.urls import reverse

from apps.corpus.models import Ficha
from apps.estudio.models import UnidadEstudio


@pytest.fixture
def autenticado(client, usuario):
    client.force_login(usuario)
    return client


@pytest.fixture
def unidades(db):
    publicada = UnidadEstudio.objects.create(
        slug="que-es-un-rango",
        titulo="Qué es un rango de plena competencia",
        resumen="El percentil como herramienta.",
        cuerpo="## Cuerpo\n\nTexto.",
        orden=1,
        publicada=True,
    )
    UnidadEstudio.objects.create(
        slug="borrador",
        titulo="Todavía escribiendo",
        resumen="No publicada.",
        cuerpo="Texto.",
        orden=2,
        publicada=False,
    )
    UnidadEstudio.objects.create(
        slug="ajuste-a-la-mediana",
        titulo="El ajuste a la mediana",
        resumen="Cuándo es obligatorio.",
        cuerpo="Texto.",
        orden=0,
        publicada=True,
    )
    return publicada


@pytest.mark.django_db
def test_el_indice_solo_lista_las_publicadas_y_en_su_orden(autenticado, unidades):
    respuesta = autenticado.get(reverse("estudio:indice"))

    titulos = [u.titulo for u in respuesta.context["unidades"]]

    assert titulos == ["El ajuste a la mediana", "Qué es un rango de plena competencia"]
    assert "Todavía escribiendo" not in respuesta.content.decode()


@pytest.mark.django_db
def test_un_borrador_responde_404_aunque_se_pida_por_su_direccion(autenticado, unidades):
    """Distinguir «existe pero no publicada» de «no existe» solo serviría para
    que alguien supiera qué estás escribiendo."""
    respuesta = autenticado.get(reverse("estudio:unidad", kwargs={"slug": "borrador"}))

    assert respuesta.status_code == 404


@pytest.mark.django_db
def test_una_unidad_enlaza_las_fichas_que_estudia(autenticado, unidades):
    call_command("reindexar_corpus")
    dos = list(Ficha.objects.all()[:2])
    unidades.fichas.set(dos)

    html = autenticado.get(
        reverse("estudio:unidad", kwargs={"slug": unidades.slug})
    ).content.decode()

    for ficha in dos:
        assert ficha.titulo in html


# ---------------------------------------------------------------------------
# La invariante
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_ninguna_unidad_de_estudio_esta_en_el_registro_de_fuentes(unidades):
    """El registro es cerrado y solo contiene Derecho. El material didáctico no."""
    from tp_domain.sources import SOURCE_REGISTRY

    slugs = set(UnidadEstudio.objects.values_list("slug", flat=True))

    assert slugs.isdisjoint(SOURCE_REGISTRY.keys())


@pytest.mark.django_db
def test_una_unidad_de_estudio_no_aparece_en_ningun_informe(autenticado, unidades):
    """La prueba que justifica que esto sea otra entidad.

    Se genera el informe de un caso real y se comprueba que ni el título ni el
    slug de ninguna unidad aparecen en el PDF. Si algún día alguien fusionara las
    dos tablas, esto lo diría antes de que un informe citara material de estudio
    como si fuera Derecho.
    """
    import io

    from pypdf import PdfReader

    from apps.analisis.models import Caso

    autenticado.post(
        reverse("analisis:crear"),
        {
            "titulo": "",
            "description": "Canon por licencia de tecnología",
            "payer_country": "ES",
            "recipient_country": "DE",
            "transaction_type": "royalty",
            "industry": "software",
            "amount_eur": "1000000",
            "rate_percent": "8.0",
            "effective_date": "2026-01-01",
        },
    )
    caso = Caso.objects.get()
    pdf = autenticado.get(reverse("analisis:informe", kwargs={"pk": caso.pk}))
    texto = "\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(pdf.content)).pages)

    for unidad in UnidadEstudio.objects.all():
        assert unidad.titulo not in texto, unidad.titulo
        assert unidad.slug not in texto, unidad.slug


@pytest.mark.django_db
def test_una_unidad_se_crea_desde_el_panel(client, administrador):
    """Al contrario que Ficha, este contenido se escribe en el panel y no en disco."""
    client.force_login(administrador)

    respuesta = client.post(
        "/admin/estudio/unidadestudio/add/",
        {
            "slug": "nueva",
            "titulo": "Nueva unidad",
            "resumen": "Resumen.",
            "cuerpo": "Texto.",
            "orden": 3,
            "publicada": "on",
            "creada_el_0": dt.date.today().isoformat(),
            "creada_el_1": "10:00:00",
        },
        follow=True,
    )

    assert respuesta.status_code == 200
    assert UnidadEstudio.objects.filter(slug="nueva").exists()


@pytest.mark.django_db
def test_el_estudio_esta_detras_de_la_sesion(client, unidades):
    respuesta = client.get(reverse("estudio:indice"))

    assert respuesta.status_code == 302
    assert respuesta["Location"].startswith("/entrar/")


@pytest.mark.django_db
def test_el_indice_declara_que_no_es_fuente_citable(autenticado, unidades):
    """Dicho en la pantalla, no solo en el modelo de datos."""
    html = autenticado.get(reverse("estudio:indice")).content.decode()

    assert "No es fuente citable" in html or "no es fuente citable" in html
