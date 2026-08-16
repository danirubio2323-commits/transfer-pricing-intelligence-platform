"""Registro de `Usuario` en el panel de administración.

Un modelo sin registrar es apalancamiento desperdiciado: el panel es la razón
por la que se eligió Django, y es lo que permite dar de alta y de baja cuentas,
y fijar el tope de gasto de cada una, sin escribir código.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.cuentas.models import Usuario

#: Los dos campos propios se añaden a los formularios que trae `UserAdmin`, no
#: sustituyen a los suyos: sin esto existirían en la tabla y serían ineditables.
CAMPOS_PROPIOS = ("Gestión de la cuenta", {"fields": ("tope_gasto_mensual_eur", "notas_admin")})


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (CAMPOS_PROPIOS,)
    add_fieldsets = UserAdmin.add_fieldsets + (CAMPOS_PROPIOS,)
    list_display = ("username", "email", "is_active", "is_staff", "tope_gasto_mensual_eur")
    list_filter = UserAdmin.list_filter + ("tope_gasto_mensual_eur",)
