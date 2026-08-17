"""Escrituras de filas con propietario.

La contraparte de `guardas.py` y `consultas.py`. Existe por la misma razón: si
crear un caso se hiciera desde cada servicio que lo necesite, poner el
propietario dependería de que quien lo escribió se acordara. Aquí el argumento
`usuario` es obligatorio y no hay forma de crear un caso huérfano.
"""

from __future__ import annotations

from apps.analisis.models import Caso


def crear_caso_de(usuario, titulo: str, payload: dict) -> Caso:
    """Crea el caso **con dueño**. No hay variante sin él."""
    return Caso.objects.create(usuario=usuario, titulo=titulo, payload=payload)
