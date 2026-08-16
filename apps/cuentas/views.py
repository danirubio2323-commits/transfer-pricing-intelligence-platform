"""Acceso, cierre de sesión y cambio de contraseña.

El mensaje de error del acceso es **el mismo** para usuario inexistente,
contraseña incorrecta y cuenta inactiva. Distinguirlos convertiría el formulario
en un detector de qué cuentas existen.
"""

from __future__ import annotations

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

#: Un solo texto para los tres motivos de rechazo.
ERROR_GENERICO = "Usuario o contraseña incorrectos."

#: A dónde va una cuenta recién autenticada. Literal y no `reverse()`: el listado
#: de casos lo crea el paso 15 y este paso no puede depender de que ya exista.
DESTINO_TRAS_ENTRAR = "/casos/"


def _destino_seguro(request: HttpRequest) -> str:
    """Un `next` que apunte fuera se ignora: es una redirección abierta."""
    siguiente = request.POST.get("next") or request.GET.get("next") or ""
    if siguiente and url_has_allowed_host_and_scheme(
        siguiente, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return siguiente
    return DESTINO_TRAS_ENTRAR


def entrar(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        formulario = AuthenticationForm(request, data=request.POST)
        if formulario.is_valid():
            login(request, formulario.get_user())
            return redirect(_destino_seguro(request))
        return render(
            request,
            "cuentas/entrar.html",
            {"error": ERROR_GENERICO, "next": request.POST.get("next", "")},
            status=422,
        )
    return render(request, "cuentas/entrar.html", {"next": request.GET.get("next", "")})


def salir(request: HttpRequest) -> HttpResponse:
    """Solo POST: con GET, un enlace o una imagen podrían cerrar la sesión de alguien."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    logout(request)
    return redirect("cuentas:entrar")


def cambiar_contrasena(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        formulario = PasswordChangeForm(user=request.user, data=request.POST)
        if formulario.is_valid():
            usuario = formulario.save()
            # Rota la clave de sesión: la cookie anterior deja de autenticar.
            update_session_auth_hash(request, usuario)
            return redirect("cuentas:contrasena")
        return render(request, "cuentas/contrasena.html", {"formulario": formulario}, status=422)
    return render(
        request, "cuentas/contrasena.html", {"formulario": PasswordChangeForm(user=request.user)}
    )
