"""El listado: un caso que se guarda pero no se encuentra es un caso perdido."""

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
LISTA = "/casos/"


def _crear(usuario, cuantos=1, prefijo="Caso"):
    from apps.comun.escrituras import crear_caso_de

    return [crear_caso_de(usuario, f"{prefijo} {i}", {}) for i in range(cuantos)]


@pytest.fixture
def autenticado(client, usuario):
    client.force_login(usuario)
    return client


@pytest.mark.django_db
def test_sin_casos_se_ve_el_vacio_de_primera_vez_y_no_el_de_busqueda(autenticado):
    """Son dos situaciones distintas y confundirlas desorienta."""
    html = autenticado.get(LISTA).content.decode()

    assert "Todavía no has analizado ninguna operación" in html
    assert "Ningún caso coincide" not in html


@pytest.mark.django_db
def test_una_busqueda_sin_resultados_ofrece_limpiar_el_filtro(autenticado, usuario):
    _crear(usuario, 2)

    html = autenticado.get(LISTA, {"q": "no-existe-esto"}).content.decode()

    assert "Ningún caso coincide" in html
    assert "Limpiar el filtro" in html


@pytest.mark.django_db
def test_el_listado_solo_muestra_los_propios(autenticado, usuario, otro_usuario):
    _crear(usuario, 1, "Mío")
    _crear(otro_usuario, 1, "Suyo")

    html = autenticado.get(LISTA).content.decode()

    assert "Mío 0" in html
    assert "Suyo 0" not in html


@pytest.mark.django_db
@pytest.mark.parametrize(
    "consulta", [{}, {"q": "Caso"}, {"orden": "titulo"}, {"jurisdiccion": "ES"}]
)
def test_el_aislamiento_aguanta_en_toda_combinacion(autenticado, usuario, otro_usuario, consulta):
    """El propietario es el primer filtro, no uno más entre otros."""
    _crear(usuario, 1, "Mío")
    _crear(otro_usuario, 3, "Suyo")

    html = autenticado.get(LISTA, consulta).content.decode()

    assert "Suyo" not in html


@pytest.mark.django_db
def test_el_servidor_recorta_el_tamano_de_pagina(autenticado, usuario):
    """Un cliente no puede pedir la tabla entera pasando un número grande."""
    _crear(usuario, 105)

    respuesta = autenticado.get(LISTA, {"por_pagina": 100000})

    assert len(respuesta.context["pagina"].object_list) <= 100


@pytest.mark.django_db
def test_un_tamano_no_numerico_cae_al_defecto_y_no_revienta(autenticado, usuario):
    _crear(usuario, 25)

    respuesta = autenticado.get(LISTA, {"por_pagina": "abc"})

    assert respuesta.status_code == 200
    assert len(respuesta.context["pagina"].object_list) == 20


@pytest.mark.django_db
def test_una_pagina_mas_alla_de_la_ultima_devuelve_la_ultima(autenticado, usuario):
    _crear(usuario, 3)

    respuesta = autenticado.get(LISTA, {"pagina": 999})

    assert respuesta.status_code == 200


@pytest.mark.django_db
def test_borrar_es_suave_y_deja_el_caso_inaccesible(autenticado, usuario):
    """La fila sigue en la base de datos: un análisis borrado es auditable."""
    caso = _crear(usuario, 1)[0]

    respuesta = autenticado.post(reverse("analisis:borrar", kwargs={"pk": caso.pk}))

    assert respuesta.status_code == 302
    assert Caso.todos.filter(pk=caso.pk).exists()
    assert Caso.todos.get(pk=caso.pk).deleted_at is not None
    assert autenticado.get(reverse("analisis:detalle", kwargs={"pk": caso.pk})).status_code == 404


@pytest.mark.django_db
def test_borrar_con_get_responde_405(autenticado, usuario):
    """Con GET, un enlace borraría al pulsarlo o al precargarlo."""
    caso = _crear(usuario, 1)[0]

    assert autenticado.get(reverse("analisis:borrar", kwargs={"pk": caso.pk})).status_code == 405


@pytest.mark.django_db
def test_no_se_puede_borrar_el_caso_de_otro(client, usuario, otro_usuario):
    ajeno = _crear(otro_usuario, 1)[0]
    client.force_login(usuario)

    assert client.post(reverse("analisis:borrar", kwargs={"pk": ajeno.pk})).status_code == 404
    assert Caso.todos.get(pk=ajeno.pk).deleted_at is None
