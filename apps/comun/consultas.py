"""Consultas con el propietario ya aplicado.

Todo listado parte de aquí. Ninguna vista escribe `Caso.objects.filter(...)` por
su cuenta: si lo hiciera, el filtro por propietario dependería de que quien la
escribió se acordara, y eso no es una propiedad comprobable.
"""

from __future__ import annotations

from django.db.models import Q, QuerySet

from apps.analisis.models import Caso

#: Los órdenes admitidos. Un valor fuera de aquí cae al primero, en vez de
#: llegar al ORM: `order_by` acepta cualquier cadena y filtraría por un campo
#: que el usuario elija.
ORDENES = {
    "reciente": "-created_at",
    "antiguo": "created_at",
    "titulo": "titulo",
}
ORDEN_POR_DEFECTO = "reciente"


def casos_de(
    usuario,
    *,
    texto: str = "",
    jurisdiccion: str = "",
    orden: str = ORDEN_POR_DEFECTO,
) -> QuerySet[Caso]:
    """Los casos vivos de ese usuario, filtrados y ordenados.

    **El propietario no es un parámetro opcional.** Es el primer `filter` y no
    hay forma de llamar a esta función sin él: el aislamiento no puede depender
    de que quien la use pase el argumento correcto.
    """
    consulta = Caso.objects.filter(usuario=usuario)

    if texto:
        consulta = consulta.filter(titulo__icontains=texto)

    if jurisdiccion:
        # Las jurisdicciones viven dentro del payload; se busca en el título y
        # en el volcado, que es donde el motor las dejó.
        codigo = jurisdiccion.upper()
        consulta = consulta.filter(
            Q(payload__transaction__payer_country=codigo)
            | Q(payload__transaction__recipient_country=codigo)
        )

    return consulta.order_by(ORDENES.get(orden, ORDENES[ORDEN_POR_DEFECTO]))
