"""Configuración de producción. **Se niega a arrancar sin clave de firma.**

La diferencia con `local.py` no es de grado: allí la clave tiene un valor de
desarrollo explícito y marcado como tal, para que ningún gate se rompa por pedir
un secreto que todavía no hace falta. Aquí no hay valor por defecto y no puede
haberlo. Una clave de firma con un valor de reserva no es una clave: cualquiera
que lea el repositorio puede firmar sesiones y tokens CSRF válidos.

Por eso el fallo es **en la importación** y **nombra la variable**. Reventar al
arrancar es ruidoso y se arregla en un minuto; arrancar con una clave conocida
es silencioso y no se descubre nunca.

Todo lo demás de este fichero da por supuesto que hay TLS delante. La v1 se
ejecuta en local (apartado 2) y por eso `local.py` no activa ninguna de estas marcas:
`SESSION_COOKIE_SECURE` sin HTTPS deja la aplicación inservible, y una medida de
seguridad que obliga a desactivarla para trabajar acaba desactivada también el
día que se despliega.
"""

from __future__ import annotations

from django.core.exceptions import ImproperlyConfigured
from pydantic import ValidationError

from config.settings.base import *  # noqa: F403
from config.settings.base import Settings

try:
    ajustes = Settings()  # type: ignore[call-arg]  # sale del entorno, no del código
except ValidationError as error:  # pragma: no cover - se comprueba por subproceso
    raise ImproperlyConfigured(
        "Falta DJANGO_SECRET_KEY. En producción no tiene valor por defecto y no "
        "puede tenerlo: una clave de reserva escrita en el repositorio permite a "
        "cualquiera firmar sesiones y tokens CSRF válidos. Genera una con:\n"
        '  uv run python -c "import secrets; print(secrets.token_urlsafe(64))"\n'
        f"Detalle: {error}"
    ) from error

SECRET_KEY = ajustes.django_secret_key

#: No se lee de la configuración: en producción `DEBUG` no es una opción. Con él
#: activado, cualquier excepción devuelve la traza, la configuración y las
#: consultas SQL a quien haya provocado el error.
DEBUG = False

ALLOWED_HOSTS = ajustes.allowed_hosts

ANTHROPIC_API_KEY = ajustes.anthropic_api_key
ANTHROPIC_MODEL = ajustes.anthropic_model
PRECIO_ENTRADA_EUR_POR_MTOK = ajustes.precio_entrada_eur_por_mtok
PRECIO_SALIDA_EUR_POR_MTOK = ajustes.precio_salida_eur_por_mtok

# --- Transporte -------------------------------------------------------------

#: Un año. Menos que eso y un navegador que visita el sitio una vez al mes
#: vuelve a hacer la primera petición en claro cada vez.
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True

# --- Cabeceras --------------------------------------------------------------

#: El navegador no adivina el tipo de un fichero. Sin esto, un fichero subido
#: que el navegador decida leer como HTML se ejecuta como HTML.
SECURE_CONTENT_TYPE_NOSNIFF = True

#: `same-origin`: el identificador de un caso viaja en la URL, y el `Referer`
#: se lo entregaría a cualquier sitio enlazado desde una ficha del corpus.
SECURE_REFERRER_POLICY = "same-origin"

#: La aplicación no se enmarca. Ni siquiera desde sí misma: no hay un solo
#: iframe en las plantillas, así que `DENY` no quita nada y cierra el
#: clickjacking sobre los formularios de borrado.
X_FRAME_OPTIONS = "DENY"

# --- Cookies ----------------------------------------------------------------

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# --- Estaticos --------------------------------------------------------------

#: Con manifiesto: `collectstatic` pone huella a cada fichero y `{% static %}`
#: falla **al construir** si una plantilla referencia uno que no existe. Ese es
#: el momento barato para enterarse; sin manifiesto, el 404 llega en produccion
#: y en silencio. En `base.py` no puede estar: exigiria haber ejecutado
#: `collectstatic` antes de poder correr una sola prueba.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
