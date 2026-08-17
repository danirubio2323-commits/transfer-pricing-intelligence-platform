"""El ciclo completo: formulario, motor, persistencia con dueño y detalle."""

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
def autenticado(client, usuario):
    client.force_login(usuario)
    return client


@pytest.mark.django_db
def test_el_formulario_vacio_responde_200(autenticado):
    assert autenticado.get(reverse("analisis:formulario")).status_code == 200


@pytest.mark.django_db
def test_un_envio_valido_crea_un_caso_del_usuario_y_redirige(autenticado, usuario):
    respuesta = autenticado.post(reverse("analisis:crear"), VALIDO)

    assert respuesta.status_code == 302
    caso = Caso.objects.get()
    assert caso.usuario == usuario
    assert respuesta["Location"] == reverse("analisis:detalle", kwargs={"pk": caso.pk})


@pytest.mark.django_db
def test_un_envio_invalido_responde_422_y_no_persiste_nada(autenticado):
    """422 y no el 200 habitual: «el formulario rechazó la entrada» debe ser
    comprobable por una máquina."""
    respuesta = autenticado.post(reverse("analisis:crear"), {**VALIDO, "recipient_country": "ES"})

    assert respuesta.status_code == 422
    assert Caso.objects.count() == 0


@pytest.mark.django_db
def test_los_campos_desnormalizados_salen_del_payload(autenticado):
    autenticado.post(reverse("analisis:crear"), VALIDO)

    caso = Caso.objects.get()

    assert caso.engine_version == caso.payload["engine_version"]
    assert caso.dataset_version == caso.payload["dataset_version"]
    assert caso.has_ai_explanation is False


@pytest.mark.django_db
def test_el_detalle_propio_responde_200(autenticado):
    autenticado.post(reverse("analisis:crear"), VALIDO)
    caso = Caso.objects.get()

    respuesta = autenticado.get(reverse("analisis:detalle", kwargs={"pk": caso.pk}))

    assert respuesta.status_code == 200
    assert "DATOS SINTÉTICOS" in respuesta.content.decode()


@pytest.mark.django_db
def test_el_detalle_de_otro_responde_404(client, usuario, otro_usuario):
    """No 403: un 403 confirmaría que ese identificador existe."""
    ajeno = Caso.objects.create(usuario=otro_usuario, titulo="Ajeno", payload={})
    client.force_login(usuario)

    respuesta = client.get(reverse("analisis:detalle", kwargs={"pk": ajeno.pk}))

    assert respuesta.status_code == 404


@pytest.mark.django_db
def test_un_sector_sin_comparables_sigue_siendo_un_resultado(autenticado):
    """Un rango incalculable es un resultado, no un fallo: se persiste igual."""
    respuesta = autenticado.post(
        reverse("analisis:crear"), {**VALIDO, "industry": "pharmaceutical", "payer_country": "FR"}
    )

    assert respuesta.status_code == 302
    assert Caso.objects.count() == 1
