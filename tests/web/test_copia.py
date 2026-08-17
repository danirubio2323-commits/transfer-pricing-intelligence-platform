"""Copia de seguridad y restauración verificada.

**Una copia sin restaurar no es una copia.** Es un fichero del que nadie sabe
nada hasta el día que hace falta, que es el peor momento para averiguarlo.

Por eso lo que se prueba aquí no es «se escribe un fichero», sino que al
restaurarlo están **todas** las filas de **las ocho** tablas — y que si faltara
alguna, el comando lo diría con un código concreto.
"""

from __future__ import annotations

import json
import sqlite3
from decimal import Decimal

import pytest
from django.core.management import call_command

from apps.analisis.models import Caso, CasoContrastado
from apps.comun.tablas import TABLAS
from apps.corpus.models import Ficha
from apps.estudio.models import UnidadEstudio
from apps.evaluacion.models import CasoEvaluacion, EjecucionEvaluacion
from apps.ia.models import LlamadaLLM


@pytest.fixture
def poblada(db, usuario, administrador):
    """Una fila en cada una de las ocho tablas, para que el recuento signifique algo."""
    caso = Caso.objects.create(usuario=usuario, titulo="Caso", payload={})
    CasoContrastado.objects.create(
        slug="p",
        titulo="Precedente",
        payload={},
        comentario_curador="Por qué.",
        publicado=True,
        curado_por=administrador,
    )
    Ficha.objects.create(
        id="f1",
        titulo="Ficha",
        jurisdiccion="ES",
        clase="legislation",
        rango_normativo="Ley",
        cita="Cita",
        tipo_localizador="boe_id",
        localizador="BOE-A-1",
        confianza_verificacion="directed_reading",
        verificada_el="2026-01-01",
        ruta_fichero="x.md",
        hash_fichero="h",
    )
    UnidadEstudio.objects.create(slug="u", titulo="U", resumen="R", cuerpo="C")
    LlamadaLLM.objects.create(
        usuario=usuario,
        proposito="explicacion",
        modelo="m",
        prompt_version="v1",
        latencia_ms=1,
        intento=1,
        coste_eur=Decimal("0"),
    )
    CasoEvaluacion.objects.create(id="c1", descripcion="d", entrada={}, propiedades_esperadas={})
    EjecucionEvaluacion.objects.create(
        sha_commit="abc",
        modelo="m",
        prompt_version="v1",
        casos_totales=1,
        casos_acertados=1,
        tasa_acierto=1.0,
        latencia_p50_ms=1,
        latencia_p95_ms=1,
        detalle=[],
    )
    return caso


def _copiar(tmp_path):
    call_command("copia_seguridad", destino=str(tmp_path))
    return next(tmp_path.glob("*.sqlite3"))


@pytest.mark.django_db(transaction=True)
def test_la_copia_escribe_el_fichero_y_sus_recuentos(poblada, tmp_path):
    copia = _copiar(tmp_path)

    assert copia.exists()
    assert copia.with_suffix(".recuentos.json").exists()


@pytest.mark.django_db(transaction=True)
def test_los_recuentos_cubren_las_ocho_tablas(poblada, tmp_path):
    copia = _copiar(tmp_path)

    cifras = json.loads(copia.with_suffix(".recuentos.json").read_text(encoding="utf-8"))

    assert set(cifras) == set(TABLAS)


@pytest.mark.django_db(transaction=True)
def test_restaurar_en_limpio_coincide_en_las_ocho_tablas(poblada, tmp_path):
    """La prueba que justifica el paso: no que exista un fichero, sino que esté entero."""
    copia = _copiar(tmp_path)

    call_command("restaurar_copia", copia=str(copia), destino=str(tmp_path / "restaurada"))


@pytest.mark.django_db(transaction=True)
def test_una_discrepancia_de_recuentos_sale_con_1(poblada, tmp_path):
    """Y nombra la tabla: un fallo que no dice cuál no sirve de nada."""
    copia = _copiar(tmp_path)
    recuentos = copia.with_suffix(".recuentos.json")
    cifras = json.loads(recuentos.read_text(encoding="utf-8"))
    cifras["casos"] += 99  # se esperan más filas de las que hay
    recuentos.write_text(json.dumps(cifras), encoding="utf-8")

    with pytest.raises(SystemExit) as salida:
        call_command("restaurar_copia", copia=str(copia), destino=str(tmp_path / "r2"))

    assert salida.value.code == 1


@pytest.mark.django_db(transaction=True)
def test_sin_fichero_de_recuentos_sale_con_2(poblada, tmp_path):
    """No es una discrepancia: es que no hay nada contra lo que comparar."""
    copia = _copiar(tmp_path)
    copia.with_suffix(".recuentos.json").unlink()

    with pytest.raises(SystemExit) as salida:
        call_command("restaurar_copia", copia=str(copia), destino=str(tmp_path / "r3"))

    assert salida.value.code == 2


@pytest.mark.django_db(transaction=True)
def test_una_copia_inexistente_sale_con_2(tmp_path):
    with pytest.raises(SystemExit) as salida:
        call_command(
            "restaurar_copia", copia=str(tmp_path / "no-existe.sqlite3"), destino=str(tmp_path)
        )

    assert salida.value.code == 2


@pytest.mark.django_db(transaction=True)
def test_la_copia_es_una_base_de_datos_valida_y_no_un_fichero_truncado(poblada, tmp_path):
    """Se usa la API de copia en línea, no un `cp`: copiar el fichero mientras
    el proceso escribe produce algo corrupto sin avisar."""
    copia = _copiar(tmp_path)

    conexion = sqlite3.connect(str(copia))
    try:
        assert conexion.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert conexion.execute("SELECT COUNT(*) FROM casos").fetchone()[0] >= 1
    finally:
        conexion.close()


def test_las_copias_estan_fuera_del_repositorio():
    """Las copias llevan datos, no código."""
    import subprocess

    hecho = subprocess.run(["git", "check-ignore", "-q", "copias/"], capture_output=True)

    assert hecho.returncode == 0
