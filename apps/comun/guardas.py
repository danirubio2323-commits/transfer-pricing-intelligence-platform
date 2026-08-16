"""La única puerta de lectura de un `Caso` con propietario.

Una condición repetida en cada vista es una condición que algún día alguien
olvidará en una sola de ellas, y esa sola basta. Aquí hay una función con
nombre, se llama desde todas partes, y es lo que se puede probar y auditar.
"""

from __future__ import annotations

from django.shortcuts import get_object_or_404

from apps.analisis.models import Caso


def caso_del_usuario(usuario, pk):
    """Devuelve el Caso vivo de ESE usuario, o levanta Http404.

    404 y no 403, deliberadamente: un 403 confirmaría que el id existe y que
    pertenece a otro. El 404 no distingue "no existe" de "no es tuyo", que es
    exactamente la propiedad que se quiere."""
    return get_object_or_404(Caso, pk=pk, usuario=usuario)
