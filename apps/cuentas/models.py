"""La cuenta de usuario.

Modelo propio desde la primera migración. No es previsión de más: cambiar
`AUTH_USER_MODEL` después de que la base de datos exista obliga a reescribir la
capa de datos entera, porque toda tabla con una clave foránea al usuario
apuntaría a una tabla que deja de existir. Cuesta una columna hoy y una
migración de varios días más tarde.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """La cuenta. Modelo propio desde la primera migración: cambiar AUTH_USER_MODEL
    después es reescribir la capa de datos entera."""

    email = models.EmailField(unique=True)
    tope_gasto_mensual_eur = models.DecimalField(max_digits=8, decimal_places=2, default=5)
    notas_admin = models.TextField(blank=True)

    class Meta:
        db_table = "usuarios"
