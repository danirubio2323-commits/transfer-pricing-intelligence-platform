"""Consultas con el propietario ya aplicado.

Todo listado parte de aquí. Ninguna vista escribe `Caso.objects.filter(...)` por
su cuenta: si lo hiciera, el filtro por propietario dependería de que quien la
escribió se acordara, y eso no es una propiedad comprobable.
"""

from __future__ import annotations

from django.db.models import QuerySet

from apps.analisis.models import Caso


def casos_de(usuario) -> QuerySet[Caso]:
    """Los casos vivos de ese usuario, del más reciente al más antiguo."""
    return Caso.objects.filter(usuario=usuario)
