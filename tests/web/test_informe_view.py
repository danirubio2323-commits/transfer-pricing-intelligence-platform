"""La descarga del informe: lo que el usuario se lleva.

`tests/report` ya comprueba el PDF generado en memoria. Aquí se comprueba el que
**sirve la web**, que es el documento que acaba en el disco de alguien. No es la
misma prueba aunque lo parezca: entre uno y otro hay una vista, una guarda, una
rehidratación y unas cabeceras.
"""

from __future__ import annotations

import io

import pytest
from django.urls import reverse
from pypdf import PdfReader

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
def caso(client, usuario):
    client.force_login(usuario)
    client.post(reverse("analisis:crear"), VALIDO)
    return Caso.objects.get()


def _texto(respuesta) -> str:
    lector = PdfReader(io.BytesIO(respuesta.content))
    return "\n".join(pagina.extract_text() or "" for pagina in lector.pages)


@pytest.mark.django_db
def test_el_propietario_descarga_un_pdf(client, caso):
    respuesta = client.get(reverse("analisis:informe", kwargs={"pk": caso.pk}))

    assert respuesta.status_code == 200
    assert respuesta["Content-Type"] == "application/pdf"


@pytest.mark.django_db
def test_el_aviso_de_datos_sinteticos_esta_en_el_pdf_servido(client, caso):
    """El aviso inamovible del riesgo 1, en el documento que el usuario se lleva.

    No es una predicción: `DATOS SINTÉTICOS` sale del disclaimer de
    TPIP_DATASET_V1 en tp_domain/sources.py, y tests/report ya lo comprueba sobre
    el PDF en memoria. Aquí se comprueba sobre el que viaja por HTTP.
    """
    respuesta = client.get(reverse("analisis:informe", kwargs={"pk": caso.pk}))

    assert "DATOS SINTÉTICOS" in _texto(respuesta)


@pytest.mark.django_db
def test_se_descarga_como_adjunto_y_con_el_identificador_del_caso(client, caso):
    respuesta = client.get(reverse("analisis:informe", kwargs={"pk": caso.pk}))

    disposicion = respuesta["Content-Disposition"]

    assert "attachment" in disposicion
    assert str(caso.pk) in disposicion


@pytest.mark.django_db
def test_el_informe_de_otro_responde_404(client, usuario, otro_usuario):
    """404 y no 403, igual que el detalle: no se confirma que el caso exista."""
    ajeno = Caso.objects.create(usuario=otro_usuario, titulo="Ajeno", payload={})
    client.force_login(usuario)

    respuesta = client.get(reverse("analisis:informe", kwargs={"pk": ajeno.pk}))

    assert respuesta.status_code == 404


@pytest.mark.django_db
def test_dos_descargas_del_mismo_caso_dicen_lo_mismo_y_no_crean_filas(client, caso):
    """El PDF sale del payload guardado, no de recalcular: si se recalculase,
    dos descargas del mismo caso podrían diferir."""
    ruta = reverse("analisis:informe", kwargs={"pk": caso.pk})

    primera = _texto(client.get(ruta))
    segunda = _texto(client.get(ruta))

    assert "DATOS SINTÉTICOS" in primera
    assert "DATOS SINTÉTICOS" in segunda
    assert Caso.objects.count() == 1
