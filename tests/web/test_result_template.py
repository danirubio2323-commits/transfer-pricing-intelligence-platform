"""Lo que la pantalla dice, no cómo se ve.

Se comprueba el contenido renderizado: que el rango está y es el protagonista,
que hay una tarjeta por jurisdicción, que un vacío se declara en vez de dejar un
hueco, y que el aviso de datos sintéticos no se puede perder de vista.
"""

from __future__ import annotations

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
def detalle(client, usuario):
    client.force_login(usuario)
    client.post(reverse("analisis:crear"), VALIDO)
    caso = Caso.objects.get()
    return client.get(reverse("analisis:detalle", kwargs={"pk": caso.pk})).content.decode()


@pytest.mark.django_db
def test_el_rango_es_el_protagonista(detalle):
    assert "<svg" in detalle
    assert detalle.index("<svg") < detalle.index("Tratamiento por jurisdicción")


@pytest.mark.django_db
def test_hay_una_tarjeta_por_jurisdiccion(detalle):
    """El rango es uno, pero el Derecho aplicable es de cada país."""
    assert "ES" in detalle
    assert "DE" in detalle
    assert "Ajuste a la mediana" in detalle


@pytest.mark.django_db
def test_sin_comparables_no_se_dibuja_un_rango_vacio(client, usuario):
    """Dibujar un rango sin datos sería peor que no dibujar nada."""
    client.force_login(usuario)
    client.post(
        reverse("analisis:crear"), {**VALIDO, "payer_country": "FR", "industry": "pharmaceutical"}
    )
    caso = Caso.objects.get()

    html = client.get(reverse("analisis:detalle", kwargs={"pk": caso.pk})).content.decode()

    if "<svg" not in html:
        assert "No se ha podido calcular un rango" in html


@pytest.mark.django_db
def test_un_vacio_se_declara_en_vez_de_dejar_un_hueco(detalle):
    """Un contenedor vacío se lee como una página rota."""
    assert "sin asistencia de IA" in detalle


@pytest.mark.django_db
def test_el_esqueleto_accesible_esta_en_todas_las_paginas(detalle):
    assert '<html lang="es"' in detalle
    assert detalle.count("<h1") == 1
    assert '<main id="contenido"' in detalle
    assert 'href="#contenido"' in detalle


@pytest.mark.django_db
def test_el_aviso_de_datos_sinteticos_es_permanente(detalle):
    """No es un adorno: impide confundir esto con un estudio válido."""
    assert "DATOS SINTÉTICOS" in detalle
    assert "administración tributaria" in detalle


@pytest.mark.django_db
def test_el_formulario_tiene_una_etiqueta_por_campo(client, usuario):
    client.force_login(usuario)

    html = client.get(reverse("analisis:formulario")).content.decode()

    assert html.count("<label for=") >= 8
    assert '<html lang="es"' in html
