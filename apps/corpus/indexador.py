"""Construye el índice del corpus leyendo los `.md` de disco.

Tres decisiones que gobiernan este módulo:

**Un fichero sin frontmatter no es una ficha y se omite en silencio.** El
criterio es la ausencia del bloque YAML, no el nombre: así queda fuera el
`README.md` del corpus, y añadir mañana un segundo índice o un borrador no
obliga a tocar este código.

**Falta un campo obligatorio, falla ruidosamente y no deja la tabla a medias.**
Un índice reconstruido a la mitad es peor que uno que no se reconstruyó: parece
completo.

**La ruta se resuelve y se comprueba que sigue dentro del corpus.** Cualquier
`..`, ruta absoluta o enlace que se salga se rechaza antes de leer nada.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import frontmatter
from django.conf import settings

#: Dónde vive el corpus. Todo lo que se indexe tiene que estar debajo.
DIRECTORIO_CORPUS = Path(settings.BASE_DIR) / "documentation" / "tax-research"

#: Campos que una ficha debe traer. Sin alguno, no se indexa nada.
OBLIGATORIOS = (
    "titulo",
    "fuente_primaria",
    "rango_normativo",
    "clase",
    "tipo_localizador",
    "localizador",
    "verificada_el",
    "confianza_verificacion",
)

#: La jurisdicción se deduce de la carpeta, porque el corpus ya está organizado
#: por jurisdicción. `processes/` no tiene valor por defecto: su ficha lo declara.
JURISDICCION_POR_DIRECTORIO = {
    "jurisdictions/spain": "ES",
    "jurisdictions/germany": "DE",
    "jurisdictions/eu": "EU",
    "frameworks": "OECD",
}


class FichaIncompleta(Exception):
    """Una ficha no cumple el contrato del índice."""


class RutaFueraDelCorpus(Exception):
    """Se ha intentado indexar algo que no está bajo el directorio del corpus."""


@dataclass(frozen=True)
class FilaFicha:
    """Lo que el indexador extrae de un fichero, antes de tocar la base de datos."""

    id: str
    titulo: str
    jurisdiccion: str
    clase: str
    rango_normativo: str
    cita: str
    pinpoint: str
    tipo_localizador: str
    localizador: str
    url_oficial: str
    confianza_verificacion: str
    verificada_el: object
    ruta_fichero: str
    hash_fichero: str


def _dentro_del_corpus(ruta: Path) -> Path:
    """Resuelve y comprueba. Lo que se salga, no se lee."""
    resuelta = ruta.resolve()
    raiz = DIRECTORIO_CORPUS.resolve()
    if not resuelta.is_relative_to(raiz):
        raise RutaFueraDelCorpus(f"{ruta} queda fuera de {raiz}")
    return resuelta


def _jurisdiccion_de(relativa: Path, metadatos: dict) -> str:
    """El frontmatter manda si lo declara; si no, la carpeta."""
    declarada = metadatos.get("jurisdiccion")
    if declarada:
        return str(declarada)

    partes = relativa.as_posix()
    for prefijo, codigo in JURISDICCION_POR_DIRECTORIO.items():
        if partes.startswith(prefijo + "/"):
            return codigo

    raise FichaIncompleta(
        f"{relativa}: no se puede deducir la jurisdicción de la ruta y el "
        "frontmatter no la declara."
    )


def _hash(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def leer_ficha(ruta: Path) -> FilaFicha | None:
    """Devuelve la fila, o `None` si el fichero no es una ficha."""
    absoluta = _dentro_del_corpus(ruta)
    documento = frontmatter.load(absoluta)

    if not documento.metadata:
        return None  # no es una ficha: es un índice, una nota o un borrador

    relativa = absoluta.relative_to(DIRECTORIO_CORPUS.resolve())

    faltan = [campo for campo in OBLIGATORIOS if not documento.metadata.get(campo)]
    if faltan:
        raise FichaIncompleta(f"{relativa}: faltan los campos {faltan}")

    meta = documento.metadata
    localizador = str(meta["localizador"])
    return FilaFicha(
        id=relativa.stem,
        titulo=str(meta["titulo"]),
        jurisdiccion=_jurisdiccion_de(relativa, meta),
        clase=str(meta["clase"]),
        rango_normativo=str(meta["rango_normativo"]),
        cita=str(meta["fuente_primaria"]),
        pinpoint=str(meta.get("pinpoint", "")),
        tipo_localizador=str(meta["tipo_localizador"]),
        localizador=localizador,
        # Solo es URL oficial si de verdad resuelve por sí sola.
        url_oficial=localizador if str(meta["tipo_localizador"]) == "url" else "",
        confianza_verificacion=str(meta["confianza_verificacion"]),
        verificada_el=meta["verificada_el"],
        ruta_fichero=relativa.as_posix(),
        hash_fichero=_hash(absoluta),
    )


def recorrer_corpus() -> list[FilaFicha]:
    """Todas las fichas del corpus, ordenadas por ruta para que el orden sea estable.

    Se leen **todas** antes de escribir nada: si una está incompleta, la
    excepción sale antes de haber tocado la tabla.
    """
    filas = []
    for ruta in sorted(DIRECTORIO_CORPUS.rglob("*.md")):
        fila = leer_ficha(ruta)
        if fila is not None:
            filas.append(fila)
    return filas
