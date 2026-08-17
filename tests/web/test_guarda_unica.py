"""La comprobación negativa: la guarda es el único camino.

Las otras pruebas comprueban que la guarda funciona. Esta comprueba algo que
ninguna prueba de comportamiento puede: que **nadie la esquiva**. Una vista que
construya su propia consulta sobre `Caso` puede ser correcta hoy y dejar de
serlo mañana sin que ninguna prueba se entere, porque el fallo no está en lo que
hace sino en lo que deja de hacer.

Por eso se comprueba leyendo el código: es el medio donde esa propiedad es
observable.
"""

from __future__ import annotations

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
VISTAS = RAIZ / "apps" / "analisis"
GUARDAS = RAIZ / "apps" / "comun"


def _fuentes(directorio: Path) -> list[Path]:
    return [f for f in directorio.rglob("*.py") if "migrations" not in f.parts]


def test_ninguna_vista_consulta_Caso_objects_por_su_cuenta():
    """El filtro por propietario no puede depender de que alguien se acuerde."""
    infractores = [
        f.relative_to(RAIZ).as_posix()
        for f in _fuentes(VISTAS)
        if "Caso.objects" in f.read_text(encoding="utf-8")
    ]

    assert infractores == [], (
        f"estas fuentes consultan Caso.objects sin pasar por apps/comun: {infractores}"
    )


def test_la_guarda_existe_con_su_nombre_y_documenta_el_404():
    """Si alguien la renombra o le quita el motivo, esto lo dice."""
    codigo = (GUARDAS / "guardas.py").read_text(encoding="utf-8")

    assert "def caso_del_usuario" in codigo
    assert "404 y no 403" in codigo


#: Llamadas al ORM que aplican el propietario. Se buscan estas y no la cadena
#: `usuario=usuario` a secas, que también aparece en líneas de registro y
#: produciría falsos positivos.
ACOTACIONES_POR_DUENO = (
    ".filter(usuario=",
    ".create(usuario=",
    "get_object_or_404(Caso",
)

#: Los únicos que pueden acotar por propietario. Añadir uno aquí es una decisión
#: deliberada, no un descuido — que es exactamente el punto de esta prueba.
PUERTAS_LEGITIMAS = {
    "apps/comun/guardas.py",
    "apps/comun/consultas.py",
    "apps/comun/escrituras.py",
}


def test_el_acceso_con_propietario_vive_en_un_solo_sitio():
    """Dos puertas son cero puertas: la segunda es la que alguien olvidará cerrar."""
    acotan = [
        f.relative_to(RAIZ).as_posix()
        for f in _fuentes(RAIZ / "apps")
        if any(p in f.read_text(encoding="utf-8") for p in ACOTACIONES_POR_DUENO)
    ]

    assert set(acotan) <= PUERTAS_LEGITIMAS, sorted(set(acotan) - PUERTAS_LEGITIMAS)
