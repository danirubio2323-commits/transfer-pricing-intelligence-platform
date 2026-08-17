"""La biblioteca de precedentes, y la propiedad que la hace segura.

**Curar no desprivatiza.** El precedente lleva una copia del payload; el caso
original sigue siendo de su dueño y sigue detrás de la guarda. Si curar
compartiera la fila en vez de copiarla, publicar un precedente expondría el caso
de alguien — y sería un fallo silencioso, porque la pantalla se vería igual.
"""

from __future__ import annotations

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.analisis.models import Caso, CasoContrastado

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
def caso_de_otro(client, otro_usuario):
    """Un caso real de otra persona, con su payload completo."""
    client.force_login(otro_usuario)
    client.post(reverse("analisis:crear"), VALIDO)
    client.logout()
    return Caso.objects.get()


@pytest.fixture
def precedente(caso_de_otro, administrador):
    return CasoContrastado.objects.create(
        slug="canon-es-de",
        titulo="Canon ES-DE por encima del P75",
        caso_origen=caso_de_otro,
        payload=caso_de_otro.payload,  # copia, no referencia
        comentario_curador="Ilustra el tratamiento asimétrico entre España y Alemania.",
        publicado=True,
        curado_por=administrador,
    )


@pytest.mark.django_db
def test_un_precedente_publicado_lo_ve_cualquier_cuenta(client, usuario, precedente):
    """No solo quien lo curó, ni solo el dueño del caso original."""
    client.force_login(usuario)

    respuesta = client.get(reverse("analisis:contrastado", kwargs={"slug": precedente.slug}))

    assert respuesta.status_code == 200
    assert precedente.titulo in respuesta.content.decode()


@pytest.mark.django_db
def test_un_borrador_responde_404_a_quien_no_administra(client, usuario, precedente):
    precedente.publicado = False
    precedente.save()
    client.force_login(usuario)

    respuesta = client.get(reverse("analisis:contrastado", kwargs={"slug": precedente.slug}))

    assert respuesta.status_code == 404


@pytest.mark.django_db
def test_curar_no_desprivatiza_el_caso_original(client, usuario, precedente, caso_de_otro):
    """La prueba central: el caso sigue siendo de su dueño, y sigue dando 404."""
    client.force_login(usuario)

    assert (
        client.get(reverse("analisis:contrastado", kwargs={"slug": precedente.slug})).status_code
        == 200
    )
    assert (
        client.get(reverse("analisis:detalle", kwargs={"pk": caso_de_otro.pk})).status_code == 404
    )


@pytest.mark.django_db
def test_el_precedente_sobrevive_al_borrado_del_caso_de_origen(
    client, usuario, precedente, caso_de_otro
):
    """Su payload es una copia: no depende de que el original siga existiendo."""
    caso_de_otro.deleted_at = timezone.now()
    caso_de_otro.save()
    client.force_login(usuario)

    respuesta = client.get(reverse("analisis:contrastado", kwargs={"slug": precedente.slug}))

    assert respuesta.status_code == 200
    assert respuesta.context["resultado"].conclusion


@pytest.mark.django_db
def test_se_muestra_el_comentario_del_curador(client, usuario, precedente):
    """Un precedente sin la razón por la que lo es sería una fila más."""
    client.force_login(usuario)

    html = client.get(
        reverse("analisis:contrastado", kwargs={"slug": precedente.slug})
    ).content.decode()

    assert precedente.comentario_curador in html


@pytest.mark.django_db
def test_el_indice_solo_lista_los_publicados(client, usuario, precedente):
    CasoContrastado.objects.create(
        slug="en-borrador",
        titulo="Sin publicar",
        payload={},
        comentario_curador="",
        publicado=False,
        curado_por=precedente.curado_por,
    )
    client.force_login(usuario)

    html = client.get(reverse("analisis:contrastados")).content.decode()

    assert precedente.titulo in html
    assert "Sin publicar" not in html


@pytest.mark.django_db
def test_la_accion_del_panel_copia_el_payload_y_nace_en_borrador(
    client, administrador, caso_de_otro
):
    """Publicar es una segunda decisión, no un efecto secundario de curar."""
    client.force_login(administrador)

    client.post(
        "/admin/analisis/caso/",
        {"action": "curar_como_precedente", "_selected_action": [str(caso_de_otro.pk)]},
        follow=True,
    )

    creado = CasoContrastado.objects.get()
    assert creado.publicado is False
    assert creado.payload == caso_de_otro.payload
    assert creado.caso_origen == caso_de_otro
    assert creado.curado_por == administrador


@pytest.mark.django_db
def test_los_precedentes_estan_detras_de_la_sesion(client, precedente):
    respuesta = client.get(reverse("analisis:contrastados"))

    assert respuesta.status_code == 302
    assert respuesta["Location"].startswith("/entrar/")
