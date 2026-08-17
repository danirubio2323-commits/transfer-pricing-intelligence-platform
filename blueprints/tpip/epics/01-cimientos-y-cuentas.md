# Epic 01: Cimientos y cuentas

> Después de esta epic existe un proyecto de Django que arranca, con la suite rescatada de 180
> pruebas en verde, cuentas de usuario con modelo propio, acceso cerrado por omisión, la entidad
> `Caso` con propietario, y una guarda única que hace que el caso de otro usuario responda 404.

| | |
|---|---|
| **Epic id** | `01-cimientos-y-cuentas` |
| **Tareas** | `E1-T1` … `E1-T7` |
| **Depende de** | nada — empieza aquí |
| **Desbloquea** | `02-analisis-y-presentacion`, `03-gasto-ia-y-contenido`, `04-precedentes-evidencia-y-cierre` |
| **Paralela con** | ninguna. Todo lo demás depende del modelo de usuario que se fija aquí |

No necesitas ningún otro fichero para completar esta epic. Todo lo de abajo está repetido aquí a
propósito.

---

## Pila

Django 5.2 · Python 3.12 · plantillas de Django · CSS plano · SQLite · ORM de Django para la
persistencia y pydantic para el dominio · `django.contrib.auth` con modelo de usuario propio ·
ejecución local en Windows 10 con PowerShell.
Gestor de paquetes: `uv`. Python y dependencias fijados en `pyproject.toml` y resueltos en `uv.lock`
— **léelos, nunca adivines una versión**.

| Tarea | Comando |
|---|---|
| Instalar | `uv sync` |
| Servidor de desarrollo | `uv run python manage.py runserver` |
| Comprobar el proyecto | `uv run python manage.py check` |
| Tipos | `uv run mypy .` |
| Lint | `uv run ruff check .` |
| Pruebas (un fichero) | `uv run pytest tests/web/test_acceso.py` |
| **Red de seguridad** | `uv run pytest tests/domain tests/ai tests/report` |
| Migraciones | `uv run python manage.py makemigrations <app>` · `uv run python manage.py migrate` |

**Gate:** `uv run ruff check . && uv run mypy . && uv run pytest` pasa antes de dar por hecha
cualquier tarea de esta epic.

Ninguna tarea de esta epic necesita un servicio externo. SQLite es un fichero que crea el propio
Django, y `pytest-django` fabrica y destruye la base de datos de prueba por su cuenta. Si una tarea te
parece que necesita levantar algo, la frontera de la epic está mal: para y reporta.

## Subárbol de directorios

Solo lo que esta epic toca:

```
manage.py                       # NUEVO — fija DJANGO_SETTINGS_MODULE = "config.settings.local"
config/
  __init__.py                   # NUEVO
  settings/
    __init__.py                 # NUEVO
    base.py                     # NUEVO — configuración tipada con pydantic-settings
    local.py                    # NUEVO — DEBUG on, hosts locales
  logging.py                    # NUEVO — structlog
  urls.py                       # NUEVO
  wsgi.py  asgi.py              # NUEVO
apps/
  __init__.py                   # NUEVO
  comun/
    __init__.py                 # NUEVO
    middleware.py               # NUEVO — ExigirAutenticacion: cierre por omisión
    guardas.py                  # NUEVO — caso_del_usuario(), la única puerta de lectura
    consultas.py                # NUEVO — casos_de(), filtra por propietario primero
  cuentas/
    __init__.py  apps.py        # NUEVO
    models.py                   # NUEVO — Usuario, el modelo de AUTH_USER_MODEL
    admin.py                    # NUEVO — Usuario registrado sobre UserAdmin
    views.py  urls.py           # NUEVO — entrar, salir, cambiar contraseña
    migrations/__init__.py      # NUEVO — la PRIMERA migración del proyecto
  analisis/
    __init__.py  apps.py        # NUEVO
    models.py                   # NUEVO — Caso y CasoVivoManager
    admin.py                    # NUEVO — Caso sobre Caso.todos
    migrations/__init__.py      # NUEVO
templates/
  cuentas/entrar.html           # NUEVO
  cuentas/contrasena.html       # NUEVO
tests/
  web/__init__.py               # NUEVO — obligatorio: sin él pytest no ve la raíz
  web/test_settings.py          # NUEVO
  web/test_rescate.py           # NUEVO
  web/test_cuentas.py           # NUEVO
  web/test_acceso.py            # NUEVO
  web/test_caso.py              # NUEVO
  web/test_aislamiento.py       # NUEVO — crece en las epics 02 y 04
  web/test_guarda_unica.py      # NUEVO
tp_domain/  ai/  infrastructure/  # EXISTEN — solo lectura en esta epic
tests/domain/  tests/ai/  tests/report/  # EXISTEN — solo se ejecutan, no se tocan
ui/                             # EXISTE — se BORRA en E1-T3
requirements.txt                # EXISTE — se BORRA en E1-T3
```

Todo lo que quede fuera de este subárbol está fuera de alcance. Si una tarea parece exigir editar un
fichero que no está aquí, para y reporta: significa que la frontera de la epic está mal.

## Modelo de datos que se toca aquí

| Entidad | Tabla | Campos que esta epic crea o lee | Notas |
|---|---|---|---|
| `Usuario` | `usuarios` | Hereda de `AbstractUser`, más `email` (**unique**), `tope_gasto_mensual_eur` (`Decimal(8,2)`, por defecto `5.00`) y `notas_admin` | `AUTH_USER_MODEL = "cuentas.Usuario"`. **Su migración es la primera del proyecto** |
| `Caso` | `casos` | `id` (UUID, PK), `usuario` (FK **not null**, indexada, `PROTECT`), `titulo`, `created_at`, `deleted_at`, `engine_version`, `dataset_version`, `has_ai_explanation`, `payload` (JSON) | Índice compuesto `(usuario, -created_at)`. `UniqueConstraint` parcial sobre `(usuario, titulo)` con `condition=Q(deleted_at__isnull=True)`. `objects` excluye los borrados; `todos` los incluye y solo lo usa el panel |

`payload` guarda `AnalysisResult.model_dump(mode="json")` y **es la fuente de verdad**: los otros tres
campos se derivan de él al guardar, nunca al revés. Todo lo que lea un `Caso` lo rehidrata con
`AnalysisResult.model_validate(obj.payload)` y trabaja sobre el objeto de dominio.

## Contratos

**Consumidos** — ya existen, no los reconstruyas:

| De | Interfaz | Garantía |
|---|---|---|
| Código rescatado | `tp_domain.models.AnalysisResult` | Modelo pydantic. Su validador rechaza el objeto si cualquier `source_ids` cita un id que el motor no emitió |
| Código rescatado | `tp_domain.sources.SOURCE_REGISTRY` | Diccionario cerrado de **5** fuentes citables |
| Código rescatado | `tp_domain.calculations.arm_length_range.calculate_arm_length_range` | Devuelve un `AnalysisResult` completo. No lo llames todavía: es de la epic 02 |

**Producidos** — las epics siguientes dependen de estas firmas exactas. Cambiar una las rompe:

| Export | Firma | Lo usa |
|---|---|---|
| `apps.cuentas.models` → `Usuario` | `AUTH_USER_MODEL = "cuentas.Usuario"` | `02`, `03`, `04` — toda FK a `settings.AUTH_USER_MODEL` |
| `apps.analisis.models` → `Caso` | Gestor por defecto `objects` que excluye `deleted_at`; `todos` que lo incluye | `02`, `03`, `04` |
| `apps.comun.guardas` → `caso_del_usuario` | `caso_del_usuario(usuario, pk) -> Caso`, levanta `Http404` | `02` (detalle, informe), `03` (listado) |
| `apps.comun.consultas` → `casos_de` | `casos_de(usuario, *, texto=None, jurisdiccion=None, orden=None) -> QuerySet` | `03` (listado buscable) |
| `apps.comun.middleware` → `ExigirAutenticacion` | Middleware que exige sesión salvo lista blanca | `02`, `03`, `04` |

## Convenciones que muerden en esta área

- **`AUTH_USER_MODEL` no se puede cambiar después de migrar.** Es la única decisión de todo el
  proyecto con una sola oportunidad. Por eso E1-T1 comprueba que **no hay ninguna migración aplicada**
  y E1-T4 aplica la de `cuentas` la primera.
- **El cierre de sesión es por omisión, vía middleware, no con decoradores.** Olvidar un decorador
  deja una vista abierta; olvidar añadir una ruta a la lista blanca la deja cerrada. El fallo tiene
  que ser el seguro.
- **404, nunca 403, para un recurso ajeno.** Un 403 confirma que el identificador existe.
- **El código rescatado no se toca en esta epic.** `tp_domain/`, `ai/` e `infrastructure/` solo se
  ejecutan. Las 180 pruebas son la evidencia de que la migración no ha roto nada.
- **Las pruebas nuevas van a `tests/web/`**, nunca a `tests/domain`, `tests/ai` ni `tests/report`:
  añadir una allí cambiaría el recuento de 180 y rompería el gate de E1-T3 hacia atrás.
- **`tests/web/__init__.py` es obligatorio.** Sin él, pytest no inserta la raíz del proyecto en
  `sys.path` para esa carpeta y ninguna prueba puede importar `config` ni `apps`.

Reglas completas del proyecto: `CLAUDE.md`. Reglas de área: `.claude/rules/capa-web.md` y
`.claude/rules/dominio-rescatado.md`. Los dos están en la raíz del proyecto — el constructor los copió
desde `workspace/` antes de la tarea uno.

---

## Tareas

En el mismo orden que `tasks.json`. Ese orden es el orden de construcción: se trabaja de arriba abajo
y no se reordena por prioridad ni por lo que parezca rápido.

### `E1-T1` — Esqueleto de Django ejecutable

**Depende de:** nada · **Prioridad:** p0

Crea el proyecto a mano, sin `django-admin startproject`: la plantilla del generador trae cosas que
aquí se deciden una a una. `INSTALLED_APPS` lleva `admin`, `auth`, `contenttypes`, `sessions`,
`messages` y `staticfiles` — las cinco primeras porque este producto tiene cuentas y panel, y el panel
es la razón por la que se eligió Django. **No ejecutes `migrate` en esta tarea**: la primera migración
que se aplica al proyecto tiene que ser la de `cuentas` con `AUTH_USER_MODEL` ya declarado (E1-T4), y
aplicar antes las tablas de `auth` con el usuario por defecto es exactamente el estado del que Django
no sabe salir.

**Ficheros**
- `manage.py` — nuevo; con la línea literal `os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")`
- `config/__init__.py`, `config/settings/__init__.py` — nuevos, vacíos
- `config/settings/base.py` — nuevo; `INSTALLED_APPS`, `MIDDLEWARE`, `TEMPLATES`, `DATABASES` (SQLite en `BASE_DIR / "db.sqlite3"`), `STATIC_ROOT = BASE_DIR / "staticfiles"`, `LANGUAGE_CODE = "es-es"`, `TIME_ZONE = "Europe/Madrid"`, `USE_TZ = True`
- `config/settings/local.py` — nuevo; `DEBUG = True`, `ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver"]`, `SECRET_KEY` de desarrollo comentado como tal
- `config/urls.py`, `config/wsgi.py`, `config/asgi.py` — nuevos

**Aceptación**

1. **WHEN** `uv run python manage.py check` runs **THE SYSTEM SHALL** exit 0 and report zero issues.
2. **WHEN** `manage.py` is read **THE SYSTEM SHALL** contain the literal `config.settings.local` as the default value of `DJANGO_SETTINGS_MODULE`, identical to the value `pyproject.toml` declares for pytest.
3. **WHEN** `config.settings.local` is imported **THE SYSTEM SHALL** expose `INSTALLED_APPS` containing `django.contrib.admin`, `django.contrib.auth`, `django.contrib.sessions`, `django.contrib.contenttypes` and `django.contrib.messages`.
4. **WHEN** the project is inspected **THE SYSTEM SHALL** have applied zero migrations, because the first migration must be `cuentas`.
5. **WHEN** `uv run ruff check config manage.py` runs **THE SYSTEM SHALL** exit 0.
6. **WHEN** `uv run python manage.py check --list-tags` runs **THE SYSTEM SHALL** exit 0, proving the entry point is executable and not merely syntactically valid.

**Verify** — cada línea sale con 0 cuando la tarea es correcta; que la última salga con 0 es lo que la
da por hecha. Desde la raíz del proyecto.

```powershell
uv run python manage.py check; if ($LASTEXITCODE -ne 0) { throw 'manage.py check no sale 0' }
uv run python manage.py check --list-tags; if ($LASTEXITCODE -ne 0) { throw 'manage.py no es ejecutable' }
if (-not ((Get-Content -Raw 'manage.py') -match '"DJANGO_SETTINGS_MODULE",\s*"config\.settings\.local"')) { throw 'manage.py no fija config.settings.local' }
if (-not ((Get-Content -Raw 'pyproject.toml') -match 'DJANGO_SETTINGS_MODULE\s*=\s*"config\.settings\.local"')) { throw 'pyproject.toml no fija config.settings.local' }
uv run python -c "import os; os.environ['DJANGO_SETTINGS_MODULE']='config.settings.local'; import django; django.setup(); from django.conf import settings; faltan=[a for a in ('django.contrib.admin','django.contrib.auth','django.contrib.sessions','django.contrib.contenttypes','django.contrib.messages') if a not in settings.INSTALLED_APPS]; assert not faltan, faltan; print('INSTALLED_APPS OK')"; if ($LASTEXITCODE -ne 0) { throw 'faltan aplicaciones de contrib' }
$aplicadas = (uv run python manage.py showmigrations --plan 2>&1 | Select-String -Pattern '^\[X\]').Count; if ($aplicadas -ne 0) { throw "hay $aplicadas migraciones aplicadas; no debe haber ninguna antes de E1-T4" }
uv run ruff check config manage.py; if ($LASTEXITCODE -ne 0) { throw 'ruff falla sobre el codigo nuevo' }
```

**Checkpoint**

```powershell
git add -A; git commit -m "E1-T1: esqueleto de Django ejecutable"
git tag step-01-esqueleto
git ls-files --error-unmatch manage.py config/settings/local.py; if ($LASTEXITCODE -ne 0) { throw 'el commit no ha recogido el esqueleto' }
```

### `E1-T2` — Configuración tipada y registro estructurado

**Depende de:** `E1-T1` · **Prioridad:** p0

Sustituye las constantes provisionales por una clase `Settings` de `pydantic_settings.BaseSettings`
con `SettingsConfigDict(env_file=".env", extra="ignore")`. **Este es el único punto del proyecto que
lee `.env`**, y por eso es el mecanismo de carga de variables de entorno de todo el sistema: ni
`manage.py`, ni pytest, ni los scripts lo leen por su cuenta. Todos los campos llevan valor por
defecto salvo la clave, que lo recibe en `local.py`: **ninguna variable es obligatoria en desarrollo**,
y eso es lo que impide que un paso posterior rompa el gate de uno anterior exigiendo un secreto de un
servicio que aún no se ha integrado.

**Ficheros**
- `config/settings/base.py` — edita: la clase `Settings` con `django_secret_key`, `django_debug`, `django_allowed_hosts`, `anthropic_api_key`, `anthropic_model`, `precio_entrada_eur_por_mtok`, `precio_salida_eur_por_mtok`
- `config/settings/local.py` — edita: lee de esa clase; mantiene el valor de desarrollo de la clave
- `config/logging.py` — nuevo; `configure_logging()` con `structlog` sobre `logging`
- `tests/web/__init__.py` — nuevo, vacío, **obligatorio**
- `tests/web/test_settings.py` — nuevo

**Aceptación**

1. **WHEN** `config.settings.local` is imported with an empty environment and no `.env` file **THE SYSTEM SHALL** load successfully and SHALL NOT raise a missing-variable error.
2. **WHEN** `ANTHROPIC_API_KEY` is absent **THE SYSTEM SHALL** expose `settings.ANTHROPIC_API_KEY` as `None` rather than an empty string, so the AI layer can tell unset from set to nothing.
3. **WHEN** `DJANGO_ALLOWED_HOSTS` contains `a.example,b.example` **THE SYSTEM SHALL** expose `ALLOWED_HOSTS` as a list of two entries, not a single comma-joined string.
4. **WHEN** `configure_logging()` runs and a bound logger emits an event **THE SYSTEM SHALL** produce a record carrying the bound keys.
5. **WHEN** `uv run pytest tests/web/test_settings.py` runs **THE SYSTEM SHALL** exit 0 with 0 failed and 0 skipped.
6. **WHEN** `uv run python manage.py check` runs **THE SYSTEM SHALL** still exit 0, so the previous task's gate does not regress.

**Verify**

```powershell
uv run pytest tests/web/test_settings.py -q; if ($LASTEXITCODE -ne 0) { throw 'las pruebas de configuracion fallan' }
uv run python -c "import os; [os.environ.pop(k, None) for k in ('DJANGO_SECRET_KEY','DJANGO_DEBUG','DJANGO_ALLOWED_HOSTS','ANTHROPIC_API_KEY','ANTHROPIC_MODEL')]; os.environ['DJANGO_SETTINGS_MODULE']='config.settings.local'; import django; django.setup(); from django.conf import settings; assert isinstance(settings.ALLOWED_HOSTS, list); print('config OK')"; if ($LASTEXITCODE -ne 0) { throw 'la configuracion exige alguna variable' }
uv run python manage.py check; if ($LASTEXITCODE -ne 0) { throw 'el gate de E1-T1 ha dejado de pasar' }
uv run ruff check config tests/web; if ($LASTEXITCODE -ne 0) { throw 'ruff falla' }
uv run mypy config; if ($LASTEXITCODE -ne 0) { throw 'mypy falla sobre config/' }
```

**Checkpoint**

```powershell
git add -A; git commit -m "E1-T2: configuracion tipada con pydantic-settings y structlog"
git tag step-02-configuracion
git ls-files --error-unmatch config/logging.py tests/web/__init__.py; if ($LASTEXITCODE -ne 0) { throw 'el commit no ha recogido la configuracion' }
```

### `E1-T3` — Retirada de Streamlit y red de seguridad en verde

**Depende de:** `E1-T2` · **Prioridad:** p0

Esta tarea convierte «el 92% del código sobrevive» en un hecho comprobado en vez de una afirmación. No
escribas lógica nueva: retira la capa que se sustituye y ejecuta la suite rescatada entera contra las
versiones fijadas. **Es donde se descubriría un cambio de comportamiento de `reportlab` 5.0 sobre el
informe escrito para 4.x**; si las 38 pruebas de `tests/report` fallan aquí, para y reporta — no
adaptes el código rescatado a un comportamiento nuevo sin decisión.

**Ficheros**
- `ui/app.py`, `ui/__init__.py` — **borrar**; es lo único que importaba `streamlit`
- `requirements.txt` — **borrar**; lo sustituyen `pyproject.toml` y `uv.lock`
- `tpip.egg-info/` — **borrar**; residuo de `pip install -e .`, que ya no se usa
- `tests/web/test_rescate.py` — nuevo

**Aceptación**

1. **WHEN** `uv run pytest tests/domain tests/ai tests/report` runs **THE SYSTEM SHALL** report exactly 180 passed, 0 failed and 0 skipped.
2. **WHEN** the repository is searched for `import streamlit` **THE SYSTEM SHALL** find zero occurrences outside `blueprints/`.
3. **WHEN** `ui/` is looked for on disk **THE SYSTEM SHALL** NOT find it.
4. **WHEN** `tp_domain.sources.SOURCE_REGISTRY` is imported **THE SYSTEM SHALL** contain exactly the 5 source ids the engine can cite.
5. **WHEN** `uv run ruff check .` runs from the project root with the bundle present **THE SYSTEM SHALL** exit 0, proving the `blueprints` exclusion in `pyproject.toml` holds.

**Verify**

```powershell
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad rescatada NO esta en verde' }
$n = (uv run pytest tests/domain tests/ai tests/report --collect-only -q 2>&1 | Select-String -Pattern '^(\d+) tests collected').Matches[0].Groups[1].Value; if ([int]$n -ne 180) { throw "la suite rescatada tiene $n pruebas, se esperaban 180" }
if (Test-Path 'ui') { throw 'ui/ sigue existiendo' }
if (Test-Path 'requirements.txt') { throw 'requirements.txt sigue existiendo' }
$hits = Select-String -Path (Get-ChildItem -Recurse -Filter '*.py' -File | Where-Object { $_.FullName -notmatch '\\(\.venv|blueprints)\\' }).FullName -Pattern 'import streamlit' -SimpleMatch -ErrorAction SilentlyContinue; if ($hits) { throw 'queda alguna importacion de streamlit' }
uv run python -c "from tp_domain.sources import SOURCE_REGISTRY; assert len(SOURCE_REGISTRY) == 5, len(SOURCE_REGISTRY); print('registro OK')"; if ($LASTEXITCODE -ne 0) { throw 'el registro cerrado de fuentes ha cambiado' }
uv run ruff check .; if ($LASTEXITCODE -ne 0) { throw 'ruff falla desde la raiz con el bundle presente' }
```

**Checkpoint**

```powershell
git add -A; git commit -m "E1-T3: retirada de Streamlit; la suite rescatada de 180 pruebas queda en verde"
git tag step-03-rescate
```

### `E1-T4` — Modelo de usuario propio, `AUTH_USER_MODEL` y panel de administración

**Depende de:** `E1-T3` · **Prioridad:** p0

**Es la tarea con una sola oportunidad de todo el proyecto.** `AUTH_USER_MODEL` no se puede cambiar
después de la migración inicial sin reescribir la capa de datos entera —toda tabla con una clave
foránea al usuario apunta a una tabla que deja de existir—, así que la primera migración que este
proyecto aplica es la de `apps.cuentas`, y ninguna otra antes. Registra `Usuario` en `admin.py` sobre
`UserAdmin`: el panel es la razón por la que se eligió Django, y esta es la primera vez que se cobra.

**Ficheros**
- `apps/__init__.py`, `apps/cuentas/__init__.py` — nuevos, vacíos
- `apps/cuentas/apps.py` — nuevo; `CuentasConfig`, `name = "apps.cuentas"`, `label = "cuentas"`
- `apps/cuentas/models.py` — nuevo; `Usuario(AbstractUser)` con `email` único, `tope_gasto_mensual_eur` y `notas_admin`, `db_table = "usuarios"`
- `apps/cuentas/admin.py` — nuevo; registra `Usuario` sobre `UserAdmin`
- `config/settings/base.py` — edita: `AUTH_USER_MODEL = "cuentas.Usuario"` y `"apps.cuentas"` en `INSTALLED_APPS`
- `tests/web/conftest.py` — nuevo; **los *fixtures* compartidos de toda la suite web**: `usuario`,
  `otro_usuario` y `administrador`. Se crean aquí porque este es el primer paso en el que existe
  la tabla de usuarios, y desde el paso 5 **todas** las pruebas de `tests/web/` los piden. Sin este
  fichero la suite entera falla con `fixture 'usuario' not found`, que se lee como una instalación
  rota y no lo es.
- `tests/web/test_cuentas.py` — nuevo

**Aceptación**

1. **WHEN** `settings.AUTH_USER_MODEL` is read **THE SYSTEM SHALL** be exactly `cuentas.Usuario`.
2. **WHEN** `uv run python manage.py migrate` runs against a fresh database **THE SYSTEM SHALL** exit 0 with `cuentas.0001_initial` applied before `admin.0001_initial` and before any table carrying a foreign key to the user — las migraciones de `auth` que crean grupos y permisos van necesariamente antes, porque `AbstractUser` depende de ellas, and `makemigrations --check --dry-run` **SHALL** then exit 0 — no model change left unmigrated.
3. **WHEN** two users are created with the same `email` **THE SYSTEM SHALL** raise an integrity error.
4. **WHEN** a `Usuario` is created without specifying `tope_gasto_mensual_eur` **THE SYSTEM SHALL** default it to `5.00`.
5. **WHEN** the admin registry is inspected **THE SYSTEM SHALL** have `cuentas.Usuario` registered.
6. **WHEN** any test in `tests/web/` requests the `usuario`, `otro_usuario` or `administrador` fixture **THE SYSTEM SHALL** resolve it from `tests/web/conftest.py`.

**Verify**

```powershell
uv run python manage.py makemigrations cuentas; if ($LASTEXITCODE -ne 0) { throw 'makemigrations falla' }
uv run python manage.py migrate; if ($LASTEXITCODE -ne 0) { throw 'migrate falla' }
uv run python manage.py makemigrations --check --dry-run; if ($LASTEXITCODE -ne 0) { throw "quedan cambios de modelo sin migrar (codigo $LASTEXITCODE)" }
uv run python manage.py migrate --check; if ($LASTEXITCODE -ne 0) { throw 'la base de datos no esta al dia' }
uv run python -c "import os; os.environ['DJANGO_SETTINGS_MODULE']='config.settings.local'; import django; django.setup(); from django.conf import settings; from django.contrib import admin; from apps.cuentas.models import Usuario; assert settings.AUTH_USER_MODEL=='cuentas.Usuario', settings.AUTH_USER_MODEL; assert Usuario in admin.site._registry, 'Usuario no esta registrado en el admin'; print('AUTH_USER_MODEL y admin OK')"; if ($LASTEXITCODE -ne 0) { throw 'AUTH_USER_MODEL o el registro en el admin no son los esperados' }
uv run pytest tests/web -q; if ($LASTEXITCODE -ne 0) { throw 'las pruebas de cuentas fallan' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A; git commit -m "E1-T4: modelo de usuario propio, AUTH_USER_MODEL y panel de administracion"
git tag step-04-cuentas
git ls-files --error-unmatch apps/cuentas/models.py apps/cuentas/admin.py; if ($LASTEXITCODE -ne 0) { throw 'el modelo de usuario no ha quedado versionado' }
```

### `E1-T5` — Acceso: entrar, salir, cambiar contraseña y cierre por omisión

**Depende de:** `E1-T4` · **Prioridad:** p0

El middleware `ExigirAutenticacion` es la pieza importante, y su orientación es la decisión: exige
sesión en **todo** salvo una lista blanca explícita (`/entrar/`, estáticos y páginas de error).
Olvidar un decorador dejaría una vista abierta; olvidar añadir una ruta a la lista blanca la deja
cerrada, que es el fallo seguro. El mensaje de error del acceso es **genérico e idéntico** para
usuario inexistente, contraseña incorrecta y cuenta inactiva: distinguirlos revelaría qué cuentas
existen. `/salir/` es solo `POST`, para que nadie cierre la sesión de otro con un enlace o una imagen.

**Ficheros**
- `apps/comun/__init__.py`, `apps/comun/middleware.py` — nuevos; `ExigirAutenticacion`
- `apps/cuentas/views.py`, `apps/cuentas/urls.py` — nuevos; `/entrar/`, `/salir/`, `/cuenta/contrasena/`
- `config/settings/base.py` — edita: el middleware, `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `SESSION_COOKIE_AGE = 43200`, `SESSION_EXPIRE_AT_BROWSER_CLOSE`, `SESSION_COOKIE_HTTPONLY`, `SESSION_COOKIE_SAMESITE`
- `templates/cuentas/entrar.html`, `templates/cuentas/contrasena.html` — nuevos
- `tests/web/test_acceso.py` — nuevo

**Aceptación**

1. **WHEN** an anonymous request hits any URL other than `/entrar/`, the static files or an error page **THE SYSTEM SHALL** respond `302` to `/entrar/` carrying the original path in `next`.
2. **WHEN** `/entrar/` receives wrong credentials, a username that does not exist, or an inactive account **THE SYSTEM SHALL** respond `422` with the same generic message in all three cases.
3. **WHEN** `/entrar/` receives valid credentials with a `next` pointing at an external host **THE SYSTEM SHALL** ignore it and redirect to the case list instead.
4. **WHEN** `/salir/` receives a `GET` **THE SYSTEM SHALL** respond `405` and SHALL NOT end the session.
5. **WHEN** a password is changed successfully **THE SYSTEM SHALL** rotate the session key so the old session cookie no longer authenticates.
6. **WHEN** `uv run pytest tests/web/test_acceso.py` runs **THE SYSTEM SHALL** exit 0 with 0 failed and 0 skipped.

**Verify**

```powershell
uv run pytest tests/web/test_acceso.py -q; if ($LASTEXITCODE -ne 0) { throw 'las pruebas de acceso fallan' }
uv run python -c "import os; os.environ['DJANGO_SETTINGS_MODULE']='config.settings.local'; import django; django.setup(); from django.conf import settings; assert any('ExigirAutenticacion' in m for m in settings.MIDDLEWARE), settings.MIDDLEWARE; print('middleware OK')"; if ($LASTEXITCODE -ne 0) { throw 'el middleware de cierre por omision no esta instalado' }
uv run pytest tests/web -q; if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A; git commit -m "E1-T5: acceso, cierre de sesion y cierre por omision via middleware"
git tag step-05-acceso
```

### `E1-T6` — Entidad `Caso`: propietario, título y borrado suave

**Depende de:** `E1-T4` · **Prioridad:** p0

El modelo `Caso` con `usuario` **no nulo, indexado y `PROTECT`**. Esa columna es lo que hace decidible
el aislamiento: sin ella, «de quién es esta fila» no tiene respuesta. `PROTECT` y no `CASCADE` porque
borrar una cuenta con casos tiene que **fallar ruidosamente**, no llevarse los casos por delante — dar
de baja es `is_active = False`. Registra `Caso` en el panel usando `Caso.todos` como consulta base:
eso es lo que hace del aviso de privacidad un hecho y no una advertencia teórica.

**Ficheros**
- `apps/analisis/__init__.py`, `apps/analisis/apps.py` — nuevos; `AnalisisConfig`, `label = "analisis"`
- `apps/analisis/models.py` — nuevo; `Caso` y `CasoVivoManager`, `db_table = "casos"`, índice compuesto y `UniqueConstraint` parcial
- `apps/analisis/admin.py` — nuevo; `Caso` sobre `Caso.todos`, con filtro por usuario
- `config/settings/base.py` — edita: `"apps.analisis"` en `INSTALLED_APPS`
- `tests/web/test_caso.py` — nuevo

**Aceptación**

1. **WHEN** a `Caso` is saved and read back **THE SYSTEM SHALL** rehydrate it through `AnalysisResult.model_validate` without raising.
2. **WHEN** a `Caso` is created **THE SYSTEM SHALL** require a non-null `usuario`, and an attempt to save without one SHALL raise an integrity error.
3. **WHEN** a `Caso` has `deleted_at` set **THE SYSTEM SHALL** exclude it from `Caso.objects` and SHALL include it in `Caso.todos`.
4. **WHEN** `delete()` is called on a `Usuario` that owns at least one `Caso` **THE SYSTEM SHALL** raise `ProtectedError` and delete nothing.
5. **WHEN** `uv run python manage.py makemigrations --check --dry-run` runs **THE SYSTEM SHALL** exit 0.
6. **WHEN** `engine_version`, `dataset_version` and `has_ai_explanation` are read back **THE SYSTEM SHALL** find them equal to the values inside `payload`, derived at save time.

**Verify**

```powershell
uv run python manage.py makemigrations analisis; if ($LASTEXITCODE -ne 0) { throw 'makemigrations falla' }
uv run python manage.py makemigrations --check --dry-run; if ($LASTEXITCODE -ne 0) { throw "quedan cambios de modelo sin migrar (codigo $LASTEXITCODE)" }
uv run python manage.py migrate; if ($LASTEXITCODE -ne 0) { throw 'migrate falla' }
uv run python manage.py migrate --check; if ($LASTEXITCODE -ne 0) { throw 'la base de datos no esta al dia' }
uv run python -c "import os; os.environ['DJANGO_SETTINGS_MODULE']='config.settings.local'; import django; django.setup(); from django.db.models import PROTECT; from apps.analisis.models import Caso; f=Caso._meta.get_field('usuario'); assert not f.null, 'usuario admite null'; assert f.db_index, 'usuario no esta indexado'; assert f.remote_field.on_delete is PROTECT, f.remote_field.on_delete; print('usuario_id OK')"; if ($LASTEXITCODE -ne 0) { throw 'la clave foranea al usuario no cumple lo exigido' }
uv run pytest tests/web -q; if ($LASTEXITCODE -ne 0) { throw 'las pruebas de Caso fallan' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A; git commit -m "E1-T6: entidad Caso con propietario, titulo y borrado suave"
git tag step-06-caso
git ls-files --error-unmatch apps/analisis/models.py apps/analisis/admin.py; if ($LASTEXITCODE -ne 0) { throw 'el modelo Caso no ha quedado versionado' }
```

### `E1-T7` — Guarda de autorización única y aislamiento con 404

**Depende de:** `E1-T5`, `E1-T6` · **Prioridad:** p0

Una sola función con nombre, `caso_del_usuario(usuario, pk)`, por la que pasa todo lector de un `Caso`.
No repartas la condición por las vistas: una comprobación duplicada en siete sitios es una que un día
falta en el octavo, y ese octavo **no da error, devuelve los datos de otro**. Al ser una función con
nombre se puede buscar quién la llama y quién no, y esa búsqueda es un criterio de aceptación. Devuelve
**404 y no 403**: un 403 confirmaría que el identificador existe y permitiría enumerar la base de
datos ajena sin ver una fila.

**Ficheros**
- `apps/comun/guardas.py` — nuevo; `caso_del_usuario(usuario, pk)` con `get_object_or_404(Caso, pk=pk, usuario=usuario)` y el docstring que explica el 404
- `apps/comun/consultas.py` — nuevo; `casos_de(usuario)` devuelve el `QuerySet` ya filtrado
- `tests/web/test_aislamiento.py` — nuevo; dos usuarios, un caso cada uno, cada intento cruzado
- `tests/web/test_guarda_unica.py` — nuevo; la comprobación negativa sobre el código

**Aceptación**

1. **WHEN** user A requests the detail of a case owned by user B **THE SYSTEM SHALL** respond `404`, not `403`, because a `403` would confirm the id exists.
2. **WHEN** user A requests a `pk` that exists in no table **THE SYSTEM SHALL** respond `404`, indistinguishable from the previous case.
3. **WHEN** user A lists their cases and user B owns cases too **THE SYSTEM SHALL** return only A's rows.
4. **WHEN** a case has `deleted_at` set and its owner requests it **THE SYSTEM SHALL** respond `404`.
5. **WHEN** `apps/analisis/` source is searched **THE SYSTEM SHALL** find zero `Caso.objects` accesses outside `apps/comun/`, so the guard is the only path.
6. **WHEN** `uv run pytest tests/web/test_aislamiento.py tests/web/test_guarda_unica.py` runs **THE SYSTEM SHALL** exit 0 with 0 failed and 0 skipped.

**Verify**

```powershell
uv run pytest tests/web/test_aislamiento.py tests/web/test_guarda_unica.py -q; if ($LASTEXITCODE -ne 0) { throw 'el aislamiento por propietario falla' }
if (-not (Test-Path 'apps/comun/guardas.py')) { throw 'falta apps/comun/guardas.py' }
if ((Get-Content -Raw 'apps/comun/guardas.py') -notmatch 'def caso_del_usuario') { throw 'la guarda no tiene el nombre acordado' }
$sueltas = Select-String -Path (Get-ChildItem 'apps/analisis' -Recurse -Filter '*.py' -File).FullName -Pattern 'Caso\.objects' -ErrorAction SilentlyContinue; if ($sueltas) { throw 'hay consultas directas a Caso.objects fuera de apps/comun' }
uv run pytest tests/web -q; if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A; git commit -m "E1-T7: guarda de autorizacion unica y aislamiento con 404"
git tag step-07-guarda
```

---

## Aceptación de la epic

La epic está hecha cuando todas sus tareas están en `done` **y**:

1. **WHEN** the full gate runs from the project root **THE SYSTEM SHALL** exit 0 on every command, with the rescued suite reporting exactly 180 passed.
2. **WHEN** two users exist and each owns one case **THE SYSTEM SHALL** answer `404` to every cross request — detail, list and delete — and never `403`.
3. **WHEN** an anonymous request hits any URL other than `/entrar/` **THE SYSTEM SHALL** redirect to `/entrar/` rather than serving content.
4. **WHEN** `settings.AUTH_USER_MODEL` is read **THE SYSTEM SHALL** be `cuentas.Usuario`, and the `cuentas` migration SHALL be the first one applied.

```powershell
uv run ruff check .; if ($LASTEXITCODE -ne 0) { throw 'lint' }
uv run mypy .; if ($LASTEXITCODE -ne 0) { throw 'tipos' }
uv run pytest; if ($LASTEXITCODE -ne 0) { throw 'suite completa' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'red de seguridad' }
uv run pytest tests/web/test_aislamiento.py tests/web/test_guarda_unica.py -q; if ($LASTEXITCODE -ne 0) { throw 'aislamiento' }
uv run python -c "import os; os.environ['DJANGO_SETTINGS_MODULE']='config.settings.local'; import django; django.setup(); from django.conf import settings; assert settings.AUTH_USER_MODEL=='cuentas.Usuario'; print('OK')"; if ($LASTEXITCODE -ne 0) { throw 'AUTH_USER_MODEL' }
```

## Trampas

- **Aplicar `migrate` antes de E1-T4.** Deja las tablas de `auth` creadas contra el usuario por
  defecto, y de ahí Django no sabe salir sin intervención manual de días. Por eso E1-T1 comprueba
  explícitamente que hay **cero** migraciones aplicadas.
- **Añadir una prueba a `tests/domain`, `tests/ai` o `tests/report`.** Cambia el recuento de 180 y
  rompe hacia atrás el gate de E1-T3, que se vuelve a ejecutar en cada tarea posterior. Las pruebas
  nuevas van a `tests/web/`, siempre.
- **Olvidar `tests/web/__init__.py`.** Sin él pytest no inserta la raíz del proyecto en `sys.path` y
  las pruebas fallan con un error de importación que parece un problema de instalación y no lo es.
- **Devolver 403 en vez de 404.** Es la trampa más fácil de caer porque 403 «significa» no autorizado.
  Confirma que el identificador existe, y con eso se enumera la base de datos de otro usuario.
- **Filtrar por propietario en la vista en lugar de en la guarda.** Funciona la primera vez y falla la
  octava, en silencio.
- **Usar `CASCADE` en la clave foránea al usuario.** Convierte un borrado accidental desde el panel en
  una pérdida de datos fiscales. `PROTECT` obliga a que la baja sea `is_active = False`.

## Antes de seguir

- [ ] Las siete tareas están en `done` en `tasks.json`; ninguna en `in_progress`.
- [ ] Pasaron **todos** los comandos `verify` de cada tarea, no solo el primero.
- [ ] No se editó ningún comando `verify`, y no se saltó ninguno porque un fichero no existiera.
- [ ] Las siete etiquetas están en git: `step-01-esqueleto` … `step-07-guarda`.
- [ ] El gate pasa limpio desde la raíz del proyecto.
- [ ] Los cinco contratos «Producidos» existen con la firma indicada.
- [ ] No se modificó ningún fichero fuera del subárbol; en particular, nada de `tp_domain/`,
      `ai/` ni `infrastructure/`.
- [ ] `.env.example` no necesitaba variables nuevas: esta epic no añade ninguna. Las tres
      `DJANGO_SUPERUSER_*` ya estaban declaradas allí desde el bundle.
- [ ] Un commit por tarea, cada uno prefijado con su id, cada uno seguido de su etiqueta.
