"""El freno de mano: comprueba el gasto **antes** de llamar, nunca después.

La comprobación vive aquí y no dentro del cliente a propósito. Dentro del cliente
ya es tarde en dos sentidos: el objeto está construido, y sobre todo la
comprobación quedaría en el mismo sitio que la llamada, donde nadie puede
verificar que ocurre primero. Aquí es una función con nombre, invocada antes, y
que una prueba puede exigir.
"""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db.models import Sum
from django.utils import timezone

from apps.ia.models import LlamadaLLM

#: Un millón. Las tarifas se publican por millón de tokens.
MTOK = Decimal("1000000")


class CuotaSuperada(Exception):
    """El usuario ha alcanzado su tope mensual. No es un error: es el freno."""


def gasto_del_mes(usuario) -> Decimal:
    """Suma del coste del usuario en el mes natural en curso.

    Mes natural y no ventana móvil: es lo que entiende quien mira una factura.
    """
    ahora = timezone.now()
    total = LlamadaLLM.objects.filter(
        usuario=usuario,
        creada_el__year=ahora.year,
        creada_el__month=ahora.month,
    ).aggregate(total=Sum("coste_eur"))["total"]
    return total or Decimal("0")


def comprobar_cuota(usuario) -> None:
    """Levanta `CuotaSuperada` si ya se alcanzó el tope.

    El límite es **inclusivo por el lado del rechazo**: alcanzarlo ya rechaza. Un
    tope que solo actúa al superarse deja pasar siempre una llamada más, y esa
    llamada es precisamente la que no estaba presupuestada.
    """
    tope = usuario.tope_gasto_mensual_eur
    gastado = gasto_del_mes(usuario)
    if gastado >= tope:
        raise CuotaSuperada(f"Gasto del mes ({gastado} €) alcanza el tope de {tope} €.")


def _tarifa(nombre: str) -> Decimal:
    """Sin tarifa configurada el coste es 0: se registra el uso y no se imputa."""
    return Decimal(str(getattr(settings, nombre, 0) or 0))


def coste_de(usage, modelo: str) -> Decimal:
    """Coste a partir del uso **reportado**, no de una estimación local.

    `modelo` se acepta para que el día que haya más de uno la tarifa pueda
    depender de él sin cambiar la firma ni a los llamantes.
    """
    if usage is None:
        return Decimal("0")

    entrada = Decimal(getattr(usage, "input_tokens", 0) or 0)
    salida = Decimal(getattr(usage, "output_tokens", 0) or 0)
    # La caché se factura aparte; mientras no haya tarifa propia se imputa al
    # precio de entrada, que es lo más cercano y nunca infravalora.
    cache_escritura = Decimal(getattr(usage, "cache_creation_input_tokens", 0) or 0)
    cache_lectura = Decimal(getattr(usage, "cache_read_input_tokens", 0) or 0)

    precio_entrada = _tarifa("PRECIO_ENTRADA_EUR_POR_MTOK")
    precio_salida = _tarifa("PRECIO_SALIDA_EUR_POR_MTOK")

    bruto = (entrada + cache_escritura + cache_lectura) * precio_entrada
    bruto += salida * precio_salida
    return bruto / MTOK
