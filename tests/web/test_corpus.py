"""La publicación del corpus: índice, ficha y los dos errores que hay que distinguir.

`400` y `404` no son intercambiables aquí. Un intento de salirse del corpus no
es un «no encontrado»: si respondiera 404, el error se convertiría en un
detector de qué ficheros existen fuera del corpus.
"""

from __future__ import annotations

import pytest
from django.core.management import call_command
from django.urls import reverse

from apps.corpus.models import Ficha

FICHA_ES = "jurisdictions/spain/art18-lis-operaciones-vinculadas"


@pytest.fixture
def corpus(db):
    call_command("reindexar_corpus")
    return Ficha.objects.all()


@pytest.fixture
def autenticado(client, usuario):
    client.force_login(usuario)
    return client


@pytest.mark.django_db
def test_el_indice_lista_todas_las_fichas(autenticado, corpus):
    html = autenticado.get(reverse("corpus:indice")).content.decode()

    for ficha in corpus:
        assert ficha.titulo in html
        assert ficha.rango_normativo in html


@pytest.mark.django_db
def test_el_indice_se_filtra_por_jurisdiccion(autenticado, corpus):
    respuesta = autenticado.get(reverse("corpus:indice"), {"jurisdiccion": "DE"})

    listadas = {f.jurisdiccion for f in respuesta.context["fichas"]}

    assert listadas == {"DE"}


@pytest.mark.django_db
def test_una_ficha_muestra_su_cabecera_y_su_cuerpo(autenticado, corpus):
    ficha = Ficha.objects.get(ruta_fichero=f"{FICHA_ES}.md")

    html = autenticado.get(reverse("corpus:ficha", kwargs={"ruta": FICHA_ES})).content.decode()

    assert ficha.titulo in html
    assert ficha.cita in html
    assert ficha.verificada_el.strftime("%d/%m/%Y") in html


@pytest.mark.django_db
def test_una_ruta_inexistente_responde_404(autenticado, corpus):
    respuesta = autenticado.get(
        reverse("corpus:ficha", kwargs={"ruta": "jurisdictions/spain/no-existe"})
    )

    assert respuesta.status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize(
    "ruta",
    [
        "../../manage.py",
        "jurisdictions/../../../manage.py",
        "jurisdictions/spain/../../../config/urls",
    ],
)
def test_salirse_del_corpus_responde_400_y_no_404(autenticado, corpus, ruta):
    """Un 404 aquí convertiría el error en un detector de qué hay fuera."""
    respuesta = autenticado.get(f"/fuentes/{ruta}/")

    assert respuesta.status_code == 400


@pytest.mark.django_db
def test_una_ficha_sin_localizador_resoluble_no_se_muestra_como_enlace(autenticado, corpus):
    """Las offline se enseñan como referencia, nunca como enlace roto."""
    offline = Ficha.objects.filter(tipo_localizador="offline").first()

    html = autenticado.get(
        reverse("corpus:ficha", kwargs={"ruta": offline.ruta_fichero.removesuffix(".md")})
    ).content.decode()

    assert "sin-enlace" in html


@pytest.mark.django_db
def test_la_confianza_de_verificacion_se_dice_en_castellano(autenticado, corpus):
    """El nombre del enum no se le enseña a un revisor de precios de transferencia."""
    html = autenticado.get(reverse("corpus:ficha", kwargs={"ruta": FICHA_ES})).content.decode()

    assert "verificada contra fuente primaria" in html
    assert "primary_source_verified" not in html


@pytest.mark.django_db
def test_el_detalle_enlaza_cada_fuente_con_su_ficha(client, usuario, corpus):
    """El enlace se resuelve por identificador compartido, sin traducción."""
    client.force_login(usuario)
    client.post(
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
    from apps.analisis.models import Caso

    caso = Caso.objects.get()
    html = client.get(reverse("analisis:detalle", kwargs={"pk": caso.pk})).content.decode()

    assert f"/fuentes/{FICHA_ES}/" in html


@pytest.mark.django_db
def test_el_corpus_esta_detras_de_la_sesion(client, corpus):
    """Como todo lo demás: el cierre es por omisión."""
    respuesta = client.get(reverse("corpus:indice"))

    assert respuesta.status_code == 302
    assert respuesta["Location"].startswith("/entrar/")
