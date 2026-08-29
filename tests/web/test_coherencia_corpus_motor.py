"""El corpus vigila al motor.

**Por qué existe este fichero.** El 27 de agosto de 2026 el corpus creció de 12 a
21 fichas y una de ellas, el art. 17.7 del Reglamento del IS, demostró que el
veredicto español del motor afirma algo falso. Las 370 pruebas siguieron en
verde, porque **ninguna comprobaba la coherencia entre lo investigado y lo que el
motor dice**. Un gate verde con el motor mintiendo es un testigo falso.

Estas pruebas cierran ese hueco. Comprueban dos clases de cosa:

1. **Coherencia estructural**, que hoy se cumple: toda jurisdicción modelada
   tiene ficha, y toda fuente que una regla invoca existe en el registro cerrado.
2. **Contradicciones conocidas**, marcadas con `xfail(strict=True)`. Fallan a
   propósito y no rompen el gate, pero **el día que alguien las arregle la prueba
   se pone roja por pasar**, y eso obliga a venir aquí a retirar la marca. Es la
   única forma que conozco de dejar una deuda escrita que no se puede olvidar.

Nada de esto vive en `tests/domain`: la suite rescatada mantiene sus 180 y estas
son pruebas nuevas.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from apps.corpus.models import Ficha
from tp_domain.models import BenchmarkRange, PartyRole, RangeRule
from tp_domain.rules.statistical_rules import (
    _RULE_SOURCES,
    JURISDICTION_RANGE_RULES,
    assess,
)
from tp_domain.sources import SOURCE_REGISTRY

RAIZ = Path(__file__).resolve().parents[2]

#: Un rango cualquiera, solo para poder construir un veredicto y leerlo.
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
    """El índice reconstruido desde los `.md`, que son la fuente de verdad."""
    from django.core.management import call_command

    call_command("reindexar_corpus", verbosity=0)
    return set(Ficha.objects.values_list("id", flat=True))


# ---------------------------------------------------------------------------
# Coherencia estructural
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_toda_jurisdiccion_modelada_tiene_ficha(corpus_indexado):
    """Modelar un país sin haberlo investigado es inventar Derecho comparado.

    La disciplina `NOT_MODELLED` lo impide al añadir; esta prueba lo impide
    también al conservar, que es el caso que nadie vigilaba.
    """
    con_ficha = set(Ficha.objects.values_list("jurisdiccion", flat=True))

    sin_ficha = set(JURISDICTION_RANGE_RULES) - con_ficha

    assert sin_ficha == set(), f"jurisdicciones modeladas sin ficha: {sorted(sin_ficha)}"


def test_toda_fuente_que_invoca_una_regla_esta_en_el_registro():
    """`_RULE_SOURCES` no puede citar lo que el registro cerrado no tiene."""
    invocadas = {sid for ids in _RULE_SOURCES.values() for sid in ids}

    fantasmas = invocadas - set(SOURCE_REGISTRY)

    assert fantasmas == set(), f"fuentes invocadas que no existen: {sorted(fantasmas)}"


@pytest.mark.django_db
def test_toda_fuente_juridica_invocada_tiene_ficha_de_investigacion(corpus_indexado):
    """El dataset sintético se exceptúa: no es Derecho y no lleva ficha."""
    invocadas = {sid for ids in _RULE_SOURCES.values() for sid in ids}
    juridicas = {s for s in invocadas if SOURCE_REGISTRY[s].kind.value != "dataset"}

    sin_respaldo = juridicas - corpus_indexado

    assert sin_respaldo == set(), f"reglas apoyadas en fuentes sin ficha: {sorted(sin_respaldo)}"


def test_cada_regla_del_enum_declara_sus_fuentes():
    """Una regla sin fuentes produciría un veredicto que no cita nada."""
    sin_fuentes = [r.name for r in RangeRule if not _RULE_SOURCES.get(r)]

    assert sin_fuentes == [], sin_fuentes


# ---------------------------------------------------------------------------
# Contradicciones conocidas entre el corpus y el motor
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.xfail(
    strict=True,
    reason=(
        "DEUDA CONOCIDA, 2026-08-27. El veredicto español dice que la Ley no impone "
        "regla estadística y calla que el art. 17.7 del Reglamento habilita usarlas. "
        "El texto vive en tp_domain/rules/statistical_rules.py, hoy protegido por la "
        "lista deny de .claude/settings.json. Al corregirlo esta prueba pasará, se "
        "pondrá roja por pasar, y habrá que venir a retirar este marcador."
    ),
)
def test_el_veredicto_espanol_no_contradice_al_corpus(corpus_indexado):
    """El corpus tiene ficha del art. 17.7 RIS; el motor lo ignora.

    Ver `documentation/tax-research/jurisdictions/spain/`
    `ris-art17-comparabilidad-medidas-estadisticas.md`.
    """
    assert "es-ris-art17" in corpus_indexado, "la ficha del art. 17 RIS debería estar indexada"

    # DENTRO del rango: es la rama que contiene la frase falsa. Con un tipo fuera
    # el motor dice otra cosa, incompleta pero no incorrecta, y la prueba pasaría
    # sin haber comprobado nada.
    veredicto = assess("ES", PartyRole.PAYER, rate=10.0, benchmark=RANGO)

    assert "no impone regla estadística" not in veredicto.consequence


@pytest.mark.xfail(
    strict=True,
    reason=(
        "DEUDA CONOCIDA, 2026-08-28. Fuera del rango, el veredicto español dice que "
        "la corrección «depende de la valoración caso por caso de la Inspección». Es "
        "vago hasta la inutilidad, y la nota del Departamento de Inspección de la "
        "AEAT sobre el rango de plena competencia permite decir algo mucho más útil: "
        "de ordinario se ajusta a la mediana, y para hacerlo la Inspección debe "
        "motivar los defectos de comparabilidad. Vive en tp_domain/, hoy protegido "
        "por la lista deny de .claude/settings.json."
    ),
)
def test_espana_fuera_del_rango_nombra_el_punto_de_ajuste_de_la_practica():
    """Fuera del rango, el veredicto tiene que nombrar la mediana. No calcularla.

    **Esta prueba cambió de forma el 28 de agosto de 2026, y conviene decir por
    qué.** Antes exigía que `adjusted_rate` dejara de ser `None` para España.
    La nota de la AEAT hizo ver que eso era el error contrario: ese campo
    significa *el tipo que la norma impone*, y en España no lo impone ninguna.
    Rellenarlo igualaría la casilla española con la alemana —donde el §1.3a sí
    lo impone— y borraría la asimetría que justifica el producto entero.

    Lo que sí falta es que la **prosa** nombre la mediana con sus condiciones.
    Un número no admite condiciones; una frase sí.

    Ver `documentation/tax-research/processes/aeat-nota-rango-plena-competencia.md`.
    """
    veredicto = assess("ES", PartyRole.PAYER, rate=4.0, benchmark=RANGO)

    # El campo se queda como está: es la decisión, no la deuda.
    assert veredicto.adjusted_rate is None

    assert "mediana" in veredicto.consequence
    assert "defectos de comparabilidad" in veredicto.consequence


# ---------------------------------------------------------------------------
# Lo que la revisión cruzada del consejo encontró y nadie de la mesa vio
# ---------------------------------------------------------------------------


def test_el_conjunto_dorado_congela_el_texto_del_veredicto():
    """**Aviso, no reproche.** Corregir el motor pondrá el arnés en rojo.

    Los casos dorados guardan la explicación esperada palabra por palabra. Dos de
    los cinco contienen la frase que hay que cambiar, de modo que **el arnés se
    quejará por acertar**. Esta prueba no falla: deja constancia de cuántos
    ficheros habrá que regenerar, para que la sorpresa no llegue después.
    """
    dorados = sorted((RAIZ / "evaluacion" / "casos").glob("*.json"))
    afectados = [
        d.name for d in dorados if "no impone regla estadística" in d.read_text(encoding="utf-8")
    ]

    assert dorados, "no hay conjunto dorado que comprobar"
    # Si este número cambia sin que nadie lo espere, es que alguien tocó el
    # conjunto dorado o el veredicto sin mirar al otro.
    assert len(afectados) == 2, f"ficheros dorados afectados: {afectados}"


@pytest.mark.django_db
def test_los_casos_guardados_congelan_el_veredicto_en_su_payload(usuario):
    """Lo mismo, hacia atrás: el informe se rehidrata del `payload`.

    Un caso analizado ayer conserva su texto dentro del JSON guardado, así que
    **corregir el motor no corrige los PDF ya emitidos**. Quien reimprima un caso
    antiguo volverá a leer la frase vieja.

    Esta prueba fija esa propiedad para que quede escrita, no para reprocharla:
    el `payload` es deliberadamente inmutable, y esa es la decisión correcta —
    un informe tiene que poder reproducirse tal como se emitió.
    """
    from apps.comun.escrituras import crear_caso_de

    veredicto = assess("ES", PartyRole.PAYER, rate=10.0, benchmark=RANGO)
    congelado = veredicto.consequence

    caso = crear_caso_de(usuario, "Congelado", {"assessments": [veredicto.model_dump(mode="json")]})
    recargado = caso.payload["assessments"][0]["consequence"]

    assert recargado == congelado

    # Y la consecuencia práctica, dicha en una afirmación:
    assert "El Art. 18.4 LIS" in recargado or "Art. 18.4" in recargado, (
        "si esto falla, el texto del veredicto cambió y los casos antiguos "
        "siguen llevando el anterior: hay que decidir qué se hace con ellos"
    )


def test_ninguna_ficha_del_corpus_carece_de_fecha_de_verificacion():
    """El corpus caduca en silencio si una ficha no dice cuándo se comprobó."""
    fichas = sorted((RAIZ / "documentation" / "tax-research").rglob("*.md"))
    sin_fecha = [
        f.name
        for f in fichas
        if f.name != "README.md"
        and not re.search(r"^verificada_el:\s*\S", f.read_text(encoding="utf-8"), re.M)
    ]

    assert sin_fecha == [], sin_fecha
