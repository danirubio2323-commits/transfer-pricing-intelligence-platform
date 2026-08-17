"""El único escritor de `LlamadaLLM`.

Una sola puerta, por la misma razón que la guarda de los casos: si cada sitio que
llama al modelo escribiera su propia fila, el día que falte un campo nadie sabría
dónde mirar.
"""

from __future__ import annotations

from decimal import Decimal

from apps.ia.cuota import coste_de
from apps.ia.models import LlamadaLLM


def _entero(usage, nombre: str) -> int:
    return int(getattr(usage, nombre, 0) or 0)


def registrar_llamada(
    *,
    usuario,
    caso=None,
    proposito: str,
    modelo: str,
    prompt_version: str,
    usage=None,
    latencia_ms: int,
    razon_finalizacion: str = "",
    error: str = "",
    intento: int = 1,
) -> LlamadaLLM:
    """Persiste lo que dijo el proveedor, más el coste derivado de ello."""
    return LlamadaLLM.objects.create(
        usuario=usuario,
        caso=caso,
        proposito=proposito,
        modelo=modelo,
        prompt_version=prompt_version,
        tokens_entrada=_entero(usage, "input_tokens"),
        tokens_salida=_entero(usage, "output_tokens"),
        tokens_cache_escritura=_entero(usage, "cache_creation_input_tokens"),
        tokens_cache_lectura=_entero(usage, "cache_read_input_tokens"),
        coste_eur=coste_de(usage, modelo) if usage is not None else Decimal("0"),
        latencia_ms=latencia_ms,
        razon_finalizacion=razon_finalizacion,
        error=error[:200],
        intento=intento,
    )
