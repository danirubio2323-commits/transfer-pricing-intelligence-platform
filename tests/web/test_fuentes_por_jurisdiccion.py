"""Cada jurisdicción cita su propia norma.

**Por qué existe este fichero.** El 28 de agosto de 2026 se leyeron los textos
primarios de las cuatro jurisdicciones forales españolas —Álava, Bizkaia,
Gipuzkoa y Navarra— y salió un hallazgo que no era jurídico sino estructural.

Las cuatro dicen, en materia de rango, lo mismo que el territorio común:
ninguna impone regla estadística. Es tentador concluir que modelarlas es
trivial. No lo es, y la razón la dio el usuario, que es quien litiga: **ante la
Hacienda Foral de Bizkaia el fundamento es la Norma Foral 11/2013, no el art.
18 LIS.** Que digan lo mismo no convierte a una en cita válida de la otra.

Y el motor no puede acertar, porque `_RULE_SOURCES` está indexado **por regla**.
Cuatro jurisdicciones con la misma regla reciben por construcción las mismas
fuentes. Añadir Bizkaia hoy produciría un informe que cita el art. 18 LIS a la
Hacienda Foral de Bizkaia: una norma que allí no rige.

Estas pruebas hacen dos cosas distintas:

1. **Un guardarraíl que pasa hoy.** Ninguna jurisdicción modelada cita la norma
   de otra. Con dos jurisdicciones es trivialmente cierto; el día que alguien
   añada una tercera bajo la estructura actual, **se pone roja**. No es una
   deuda anotada: es la valla que impide cometer el error.
2. **Una deuda marcada `xfail(strict=True)`.** Las cuatro forales están
   investigadas y siguen en `NOT_MODELLED`, porque el cambio vive en
   `tp_domain/`, hoy protegido por la lista deny de `.claude/settings.json`.

Corpus de referencia:
`documentation/tax-research/jurisdictions/spain/forales-habilitacion-medidas-estadisticas.md`
"""

from __future__ import annotations

import pytest

from apps.corpus.models import Ficha
from tp_domain.models import BenchmarkRange, PartyRole
from tp_domain.rules.statistical_rules import JURISDICTION_RANGE_RULES, assess
from tp_domain.sources import resolve

#: Fuentes que no pertenecen a ninguna jurisdicción: valen para todas.
TRANSVERSALES = {"OECD", "GLOBAL"}

#: Las cuatro jurisdicciones forales españolas, con su ficha y su norma.
#: Códigos ISO 3166-2:ES, que es un estándar y no una invención de este motor.
FORALES = {
    "ES-VI": ("es-vi-nf37-2013-art42", "Álava"),
    "ES-BI": ("es-bi-nf11-2013-art42", "Bizkaia"),
    "ES-SS": ("es-ss-nf2-2014-art42", "Gipuzkoa"),
    "ES-NA": ("es-na-lf26-2016-art28", "Navarra"),
}

RANGO = BenchmarkRange(
    percentile_10=6.0,
    percentile_25=8.0,
    percentile_50=10.0,
    percentile_75=12.0,
    percentile_90=14.0,
    count_accepted=19,
    count_rejected=6,
)


@pytest.fixture
def corpus_indexado(db):
    from django.core.management import call_command

    call_command("reindexar_corpus", verbosity=0)
    return set(Ficha.objects.values_list("id", flat=True))


# ---------------------------------------------------------------------------
# El guardarraíl. Pasa hoy, y se pone rojo si alguien añade mal una jurisdicción
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("pais", sorted(JURISDICTION_RANGE_RULES))
def test_ningun_veredicto_cita_la_norma_de_otra_jurisdiccion(pais: str) -> None:
    """Una fuente nacional solo vale para su propia jurisdicción.

    Con `ES` y `DE` esto se cumple sin esfuerzo. La prueba no está aquí por
    ellos: está para que **añadir una quinta jurisdicción sin separar las
    fuentes falle en el acto**, en vez de producir un informe que cita a la
    Hacienda Foral de Bizkaia una ley que en Bizkaia no rige.
    """
    veredicto = assess(pais, PartyRole.PAYER, rate=10.0, benchmark=RANGO)

    ajenas = [
        f"{f.id} (es de {f.jurisdiction})"
        for f in resolve(veredicto.source_ids)
        if f.jurisdiction not in TRANSVERSALES and f.jurisdiction != pais
    ]

    assert ajenas == [], f"el veredicto de {pais} cita normas de otra jurisdicción: {ajenas}"


@pytest.mark.parametrize("pais", sorted(JURISDICTION_RANGE_RULES))
def test_toda_jurisdiccion_modelada_cita_al_menos_una_norma_propia(pais: str) -> None:
    """Citar solo las Directrices de la OCDE no es fundamentar.

    Es el error simétrico del anterior y hay que vigilarlo igual: alguien que
    resuelva el problema quitando la norma nacional de la lista compartida
    dejaría a Bizkaia citando únicamente material transversal. Ante una
    Administración tributaria eso no es un fundamento, es una referencia.
    """
    veredicto = assess(pais, PartyRole.PAYER, rate=10.0, benchmark=RANGO)

    propias = [f.id for f in resolve(veredicto.source_ids) if f.jurisdiction == pais]

    assert propias, f"{pais} no cita ninguna norma propia: {veredicto.source_ids}"


# ---------------------------------------------------------------------------
# Lo que el corpus ya tiene listo y el motor todavía no usa
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.parametrize(
    "codigo,ficha,nombre", [(c, f, n) for c, (f, n) in sorted(FORALES.items())]
)
def test_cada_foral_tiene_ficha_con_su_codigo(
    corpus_indexado: set[str], codigo: str, ficha: str, nombre: str
) -> None:
    """La investigación está hecha: cuatro textos primarios leídos, cuatro fichas.

    Esta prueba no espera al motor. Comprueba que el corpus está en condiciones
    de respaldar el alta, que es el requisito previo de `anadir-jurisdiccion`.
    """
    assert ficha in corpus_indexado, f"falta la ficha de {nombre}"

    fila = Ficha.objects.get(id=ficha)
    assert fila.jurisdiccion == codigo, (
        f"la ficha de {nombre} declara jurisdiccion={fila.jurisdiccion!r}, se esperaba {codigo!r}"
    )
    assert fila.confianza_verificacion == "primary_source_verified"


@pytest.mark.xfail(
    strict=True,
    reason=(
        "DEUDA CONOCIDA, 2026-08-28. Las cuatro jurisdicciones forales están "
        "investigadas contra fuente primaria y siguen en NOT_MODELLED. Darlas de "
        "alta exige antes separar las fuentes por jurisdicción en "
        "tp_domain/rules/statistical_rules.py, hoy protegido por la lista deny "
        "de .claude/settings.json. El parche está preparado y verificado en "
        "documentation/decisiones/fuentes-por-jurisdiccion.md. Al aplicarlo esta "
        "prueba pasará, se pondrá roja por pasar, y habrá que retirar el marcador."
    ),
)
def test_las_cuatro_forales_estan_modeladas() -> None:
    """Cuatro jurisdicciones investigadas que el motor todavía trata como ajenas."""
    sin_modelar = sorted(set(FORALES) - set(JURISDICTION_RANGE_RULES))

    assert sin_modelar == [], f"forales investigadas pero no modeladas: {sin_modelar}"
