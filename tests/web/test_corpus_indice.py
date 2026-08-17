"""El índice del corpus: reconstruible, idempotente y fiel al disco.

La propiedad que se protege aquí no es «la tabla tiene filas», sino que **la
tabla no puede mentir sobre lo que hay en disco**. Un índice que diverge del
corpus es peor que no tenerlo: se consulta creyendo que está al día.
"""

from __future__ import annotations

from pathlib import Path

import frontmatter
import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.corpus.indexador import (
    DIRECTORIO_CORPUS,
    FichaIncompleta,
    RutaFueraDelCorpus,
    leer_ficha,
    recorrer_corpus,
)
from apps.corpus.models import Ficha


def _ficheros_con_frontmatter() -> list[Path]:
    return [p for p in DIRECTORIO_CORPUS.rglob("*.md") if frontmatter.load(p).metadata]


@pytest.mark.django_db
def test_el_indice_tiene_una_fila_por_ficha_real():
    call_command("reindexar_corpus")

    assert Ficha.objects.count() == len(_ficheros_con_frontmatter())


@pytest.mark.django_db
def test_el_readme_queda_fuera_por_no_tener_frontmatter():
    """El criterio es la ausencia de frontmatter, no el nombre: así añadir un
    segundo índice o un borrador no obliga a tocar el indexador."""
    assert leer_ficha(DIRECTORIO_CORPUS / "README.md") is None

    call_command("reindexar_corpus")

    assert not Ficha.objects.filter(ruta_fichero="README.md").exists()


@pytest.mark.django_db
def test_reindexar_dos_veces_deja_el_mismo_estado():
    call_command("reindexar_corpus")
    primera = {(f.id, f.hash_fichero) for f in Ficha.objects.all()}

    call_command("reindexar_corpus")
    segunda = {(f.id, f.hash_fichero) for f in Ficha.objects.all()}

    assert primera == segunda


@pytest.mark.django_db
def test_un_cambio_en_disco_cambia_el_hash():
    """Sin esto, una ficha editada y no reindexada pasaría inadvertida."""
    call_command("reindexar_corpus")
    ruta = _ficheros_con_frontmatter()[0]
    ficha = Ficha.objects.get(ruta_fichero=ruta.relative_to(DIRECTORIO_CORPUS).as_posix())
    original = ruta.read_text(encoding="utf-8")

    try:
        ruta.write_text(original + "\n<!-- alteración deliberada -->\n", encoding="utf-8")
        call_command("reindexar_corpus")
        assert Ficha.objects.get(pk=ficha.pk).hash_fichero != ficha.hash_fichero
    finally:
        ruta.write_text(original, encoding="utf-8")


@pytest.mark.django_db
def test_una_ficha_incompleta_falla_sin_dejar_la_tabla_a_medias(tmp_path, monkeypatch):
    """Un índice reconstruido a la mitad es peor que uno no reconstruido:
    parece completo."""
    call_command("reindexar_corpus")
    antes = Ficha.objects.count()

    corpus_falso = tmp_path / "corpus"
    (corpus_falso / "jurisdictions" / "spain").mkdir(parents=True)
    (corpus_falso / "jurisdictions" / "spain" / "coja.md").write_text(
        '---\ntitulo: "Sin lo demás"\n---\n\nCuerpo.\n', encoding="utf-8"
    )
    monkeypatch.setattr("apps.corpus.indexador.DIRECTORIO_CORPUS", corpus_falso)

    with pytest.raises(CommandError, match="faltan los campos"):
        call_command("reindexar_corpus")

    assert Ficha.objects.count() == antes  # intacta


def test_una_ruta_fuera_del_corpus_se_rechaza_sin_leer():
    with pytest.raises(RutaFueraDelCorpus):
        leer_ficha(DIRECTORIO_CORPUS / ".." / ".." / "manage.py")


def test_sin_jurisdiccion_deducible_ni_declarada_falla(tmp_path, monkeypatch):
    suelta = tmp_path / "suelta.md"
    suelta.write_text(
        "---\n"
        'titulo: "x"\nfuente_primaria: "x"\nrango_normativo: "x"\nclase: "guidelines"\n'
        'tipo_localizador: "offline"\nlocalizador: "x"\nverificada_el: 2026-01-01\n'
        'confianza_verificacion: "directed_reading"\n'
        "---\n\nCuerpo.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("apps.corpus.indexador.DIRECTORIO_CORPUS", tmp_path)

    with pytest.raises(FichaIncompleta, match="jurisdicción"):
        leer_ficha(suelta)


@pytest.mark.django_db
def test_el_identificador_es_el_mismo_que_usa_el_motor():
    """Sin tabla de traducción: la fuente que el motor cita se resuelve directa."""
    call_command("reindexar_corpus")

    assert Ficha.objects.filter(pk="art18-lis-operaciones-vinculadas").exists()


@pytest.mark.django_db
def test_solo_las_resolubles_llevan_url_oficial():
    """Una referencia offline no puede aparecer como si fuera un enlace."""
    call_command("reindexar_corpus")

    for ficha in Ficha.objects.all():
        if ficha.tipo_localizador == "offline":
            assert ficha.url_oficial == ""
        elif ficha.tipo_localizador == "url":
            assert ficha.url_oficial == ficha.localizador


def test_el_recorrido_omite_lo_que_no_es_ficha():
    rutas = {fila.ruta_fichero for fila in recorrer_corpus()}

    assert "README.md" not in rutas
    assert len(rutas) == len(_ficheros_con_frontmatter())
