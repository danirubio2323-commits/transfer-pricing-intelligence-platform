"""Cierre por omisión: exige sesión en todo salvo una lista blanca explícita.

**La orientación del valor por defecto es la decisión.** Con decoradores por
vista, olvidar uno deja una vista abierta y nadie se entera hasta que alguien la
encuentra. Con este middleware, olvidar añadir una ruta a la lista blanca deja
una vista cerrada: se nota en el acto y el fallo es hacia el lado seguro.

La lista blanca es de prefijos y se declara aquí, en un solo sitio, para que
revisarla sea leer diez líneas y no recorrer todas las vistas del proyecto.
"""

from __future__ import annotations

from collections.abc import Callable

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse

#: Prefijos accesibles sin sesión. Todo lo demás exige estar autenticado.
RUTAS_PUBLICAS: tuple[str, ...] = (
    "/entrar/",
    "/static/",
)


def es_publica(ruta: str) -> bool:
    return any(ruta.startswith(prefijo) for prefijo in RUTAS_PUBLICAS)


class ExigirAutenticacion:
    """Redirige a la página de acceso cualquier petición anónima fuera de la lista blanca."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_authenticated and not es_publica(request.path):
            destino = f"{reverse('cuentas:entrar')}?next={request.get_full_path()}"
            return redirect(destino)
        return self.get_response(request)
