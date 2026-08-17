# Epic 02: Análisis y presentación

> Después de esta epic los dos defectos conocidos están corregidos y existe la rebanada vertical
> completa: un usuario rellena el formulario, el motor calcula, el caso se guarda con su propietario,
> la pantalla enseña el rango como protagonista y el informe PDF se descarga con su aviso de datos
> sintéticos intacto.

| | |
|---|---|
| **Epic id** | `02-analisis-y-presentacion` |
| **Tareas** | `E2-T1` … `E2-T7` |
| **Depende de** | `01-cimientos-y-cuentas` |
| **Desbloquea** | `03-gasto-ia-y-contenido`, `04-precedentes-evidencia-y-cierre` |
| **Paralela con** | ninguna. La 03 necesita el listado que se apoya en las plantillas de aquí |

No necesitas ningún otro fichero para completar esta epic. Todo lo de abajo está repetido aquí a
propósito.

---

## Pila

Django 5.2 · Python 3.12 · plantillas de Django · CSS plano con variables generadas desde
`infrastructure/theme.py` · SQLite · ORM de Django para la persistencia y pydantic para el dominio ·
`reportlab` para el informe · ejecución local en Windows 10 con PowerShell.
Gestor de paquetes: `uv`. Python y dependencias fijados en `pyproject.toml` y resueltos en `uv.lock`
— **léelos, nunca adivines una versión**.

| Tarea | Comando |
|---|---|
| Servidor de desarrollo | `uv run python manage.py runserver` |
| Comprobar el proyecto | `uv run python manage.py check` |
| Tipos | `uv run mypy .` |
| Lint | `uv run ruff check .` |
| Pruebas (un fichero) | `uv run pytest tests/web/test_forms.py` |
| **Red de seguridad** | `uv run pytest tests/domain tests/ai tests/report` |
| Tokens de diseño | `uv run python -m scripts.build_tokens` · comprobar: `--check` |

**Gate:** `uv run ruff check . && uv run mypy . && uv run pytest` pasa antes de dar por hecha
cualquier tarea de esta epic.

Ninguna tarea de esta epic necesita un servicio externo ni red. El informe PDF se genera **sin
llamar a ninguna API**, y esa propiedad ya está cubierta por una prueba rescatada.

## Subárbol de directorios

Solo lo que esta epic toca:

```
ai/
  claude_client.py              # EXISTE — se EDITA en E2-T1 (defecto 1)
infrastructure/
  theme.py                      # EXISTE — se EDITA en E2-T2 (defecto 2), solo añadiendo claves
  charts.py                     # EXISTE — solo lectura: genera el SVG del rango
  report/pdf_report.py          # EXISTE — solo lectura: render_report_bytes()
apps/analisis/
  forms.py                      # NUEVO — CasoForm
  services.py                   # NUEVO — crear_caso(); sin HTTP dentro
  views.py                      # NUEVO — formulario, crear, detalle, informe
  urls.py                       # NUEVO
  models.py                     # EXISTE de la epic 01 — solo lectura aquí
apps/comun/
  guardas.py                    # EXISTE de la epic 01 — se USA, no se toca
scripts/
  __init__.py                   # NUEVO — hace de scripts/ un paquete
  build_tokens.py               # NUEVO — theme.COLORS -> static/css/tokens.css
static/css/
  tokens.css                    # NUEVO — GENERADO, y versionado
  app.css                       # NUEVO — escrito a mano, sin un solo color literal
templates/
  base.html                     # NUEVO
  analisis/form.html            # NUEVO
  analisis/detalle.html         # NUEVO
  partials/_benchmark.html      # NUEVO — el rango, protagonista
  partials/_jurisdictions.html  # NUEVO
  partials/_risk_factors.html   # NUEVO
  400.html 403.html 404.html 405.html 500.html   # NUEVOS
tests/web/
  test_forms.py                 # NUEVO
  test_analisis_view.py         # NUEVO
  test_result_template.py       # NUEVO
  test_theme_tokens.py          # NUEVO
  test_informe_view.py          # NUEVO
  test_aislamiento.py           # EXISTE de la epic 01 — se AMPLÍA en E2-T4 y E2-T7
tests/ai/test_explanation_flow.py   # EXISTE — se EDITA en E2-T1, prueba por prueba
```

Todo lo que quede fuera de este subárbol está fuera de alcance. Si una tarea parece exigir editar un
fichero que no está aquí, para y reporta.

## Modelo de datos que se toca aquí

| Entidad | Tabla | Campos que esta epic lee o escribe | Notas |
|---|---|---|---|
| `Caso` | `casos` | Escribe `usuario`, `titulo`, `payload`, `engine_version`, `dataset_version`, `has_ai_explanation`. Lee todos | Creado en la epic 01. **No se añade ni un campo aquí** |

`payload` guarda `AnalysisResult.model_dump(mode="json")` y **es la fuente de verdad**: los tres
campos desnormalizados se derivan de él al guardar, nunca al revés. Todo lo que lea un `Caso` lo
rehidrata con `AnalysisResult.model_validate(obj.payload)` y trabaja sobre el objeto de dominio;
ninguna plantilla lee claves sueltas de `payload`.

## Contratos

**Consumidos** — ya existen, no los reconstruyas:

| De | Interfaz | Garantía |
|---|---|---|
| `01` | `apps.comun.guardas.caso_del_usuario(usuario, pk)` | Devuelve el `Caso` vivo de ese usuario o levanta `Http404`. **Es la única puerta de lectura** |
| `01` | `apps.analisis.models.Caso` | Gestor `objects` que excluye los borrados en suave |
| `01` | `apps.comun.middleware.ExigirAutenticacion` | Toda ruta exige sesión salvo la lista blanca |
| Rescatado | `tp_domain.calculations.arm_length_range.calculate_arm_length_range` | Devuelve un `AnalysisResult` completo, con percentiles, veredictos por jurisdicción y factores de riesgo |
| Rescatado | `tp_domain.models.Transaction` | Valida las invariantes del dominio: jurisdicciones distintas, tipo soportado, importe positivo |
| Rescatado | `infrastructure.charts.benchmark_range_svg(result)` | Devuelve el SVG del rango, o `None` si el benchmark no tiene datos |
| Rescatado | `infrastructure.report.render_report_bytes(result)` | Devuelve el PDF en memoria. **No hace ninguna llamada de red** |
| Rescatado | `infrastructure.theme.COLORS` | Diccionario de la paleta, en hexadecimal |

**Producidos** — las epics siguientes dependen de estas firmas exactas:

| Export | Firma | Lo usa |
|---|---|---|
| `apps.analisis.services` → `crear_caso` | `crear_caso(usuario, transaction, titulo) -> Caso` | `03` (le añade cuota e IA) |
| `apps.analisis.forms` → `CasoForm` | `cleaned_data["transaction"]` es un `tp_domain.models.Transaction` | `03` |
| `ai.claude_client` → `request_explanation` | `request_explanation(result, client=None, model=None)`; exige `model`, devuelve la explicación más el `usage` y el `stop_reason` del proveedor | `03` (registro de `LlamadaLLM`) |
| `templates/base.html` | Bloque `contenido`, pie con `role="contentinfo"` | `03`, `04` |
| `templates/partials/_benchmark.html` | Pinta el rango a partir de un `AnalysisResult` | `04` (precedentes) |
| `scripts/build_tokens.py` | `--check` sale 0 si está sincronizado, 1 si no | `04` (gate de cierre) |

## Convenciones que muerden en esta área

- **Los dos defectos se corrigen antes de que nada nuevo dependa de ellos.** Arreglar la paleta
  después de escribir el CSS obligaría a reescribir el CSS.
- **La ampliación de la paleta es estrictamente aditiva.** Renombrar `surface` rompe `pdf_report.py` y
  las 38 pruebas de `tests/report`, y con ellas el recuento de 180.
- **Los scripts se invocan con `-m`**: `uv run python -m scripts.build_tokens`. La forma directa pone
  `scripts/` en `sys.path[0]` y no encuentra `infrastructure`. Por eso existe `scripts/__init__.py`.
- **`ai/` no importa Django.** El modelo y la clave se le inyectan desde fuera.
- **Ninguna vista importa `tp_domain.calculations` ni consulta `Caso.objects`.** Pasa por
  `services.py` y por la guarda.
- **Un formulario inválido responde 422**, no el 200 habitual de Django.
- **`static/css/app.css` no contiene ni un color literal.**
- **Las pruebas nuevas van a `tests/web/`.** La única excepción es E2-T1, que **sustituye prueba por
  prueba** en `tests/ai/` para que el recuento siga siendo 180.

Reglas completas del proyecto: `CLAUDE.md`. Reglas de área: `.claude/rules/dominio-rescatado.md`,
`.claude/rules/capa-web.md` y `.claude/rules/estilo-visual.md`.

---

## Tareas

En el mismo orden que `tasks.json`.

### `E2-T1` — Defecto 1: el modelo de IA deja de resolverse solo

**Depende de:** `E1-T3` · **Prioridad:** p0

`ai/claude_client.py` resuelve hoy el identificador del modelo en ejecución: si `ANTHROPIC_MODEL` no
está definida, pregunta a la API por el catálogo y elige «el Sonnet más reciente». Rompe la
reproducibilidad —que es la premisa del sistema—, convierte una llamada de red opcional en
obligatoria, y hace imposible tarifar antes de llamar, que es lo que la epic 03 necesita para el tope
de gasto. Borra `resolve_model()` entero, haz `model` obligatorio, quita las ramas de `st.secrets` y
de `dotenv_values`, y **devuelve el `usage` y el `stop_reason` del proveedor sin interpretarlos**:
`ai/` transporta lo que el proveedor dijo, no lo calcula.

**Ficheros**
- `ai/claude_client.py` — edita: borra `resolve_model` y la llamada a `client.models.list`; `model` obligatorio en `request_explanation`; `resolve_api_key()` solo lee del entorno; devuelve `usage` y `stop_reason`; actualiza el docstring del módulo
- `tests/ai/test_explanation_flow.py` — edita: **sustituye prueba por prueba** las que cubrían la resolución dinámica y la precedencia antigua de la clave

**Aceptación**

1. **WHEN** `ai/claude_client.py` is read **THE SYSTEM SHALL** contain no reference to `models.list` and no function named `resolve_model`.
2. **WHEN** `request_explanation` is called with `model=None` **THE SYSTEM SHALL** raise `ClaudeUnavailable` without making any network call.
3. **WHEN** `explain_analysis` is called with `model=None` **THE SYSTEM SHALL** return `None` and SHALL NOT raise.
4. **WHEN** a call succeeds **THE SYSTEM SHALL** return the provider's reported `usage` and `stop_reason` alongside the explanation, uninterpreted, so no token is counted locally.
5. **WHEN** `ai/claude_client.py` is imported **THE SYSTEM SHALL** NOT import `django` or `streamlit`.
6. **WHEN** `uv run pytest tests/domain tests/ai tests/report` runs **THE SYSTEM SHALL** still report exactly 180 passed, every retired test having been replaced by one covering the new behaviour.

**Verify**

```powershell
if ((Get-Content -Raw 'ai/claude_client.py') -match 'models\.list') { throw 'sigue consultando el catalogo de modelos' }
if ((Get-Content -Raw 'ai/claude_client.py') -match 'def resolve_model') { throw 'resolve_model sigue existiendo' }
if ((Get-Content -Raw 'ai/claude_client.py') -match 'import streamlit') { throw 'sigue importando streamlit' }
if ((Get-Content -Raw 'ai/claude_client.py') -match '(?m)^\s*(from|import)\s+django') { throw 'ai/ ha empezado a importar Django' }
uv run python -c "import inspect; from ai.claude_client import request_explanation; assert 'model' in inspect.signature(request_explanation).parameters; print('firma OK')"; if ($LASTEXITCODE -ne 0) { throw 'la firma de request_explanation no es la esperada' }
uv run pytest tests/ai -q; if ($LASTEXITCODE -ne 0) { throw 'las pruebas de la capa de IA fallan' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
$n = (uv run pytest tests/domain tests/ai tests/report --collect-only -q 2>&1 | Select-String -Pattern '^(\d+) tests collected').Matches[0].Groups[1].Value; if ([int]$n -ne 180) { throw "la suite rescatada tiene $n pruebas, se esperaban 180" }
```

**Checkpoint**

```powershell
git add -A; git commit -m "E2-T1: el modelo de IA se fija por configuracion; fuera la resolucion dinamica"
git tag step-08-modelo-fijado
```

### `E2-T2` — Defecto 2: paleta con superficies diferenciadas

**Depende de:** `E1-T3` · **Prioridad:** p0

`COLORS` tiene hoy una sola superficie, `#F7F8FA`. Para un PDF sobre papel blanco bastaba; para una
pantalla hacen falta fondo de página, superficie de tarjeta, superficie hundida, un borde con
contraste suficiente para los controles y un color de foco. **Añade claves, no renombres ninguna**:
renombrar `surface` rompe `pdf_report.py` y las 38 pruebas de informe. No añadas pruebas en
`tests/report`: cambiarían el recuento de 180. La cobertura de los tokens nuevos va en
`tests/web/test_theme_tokens.py`, en E2-T6, porque lo que se comprueba es el contrato entre `theme.py`
y el CSS.

**Ficheros**
- `infrastructure/theme.py` — edita: añade a `COLORS` las claves `background` `#FFFFFF`, `surface_sunken` `#EBEEF3`, `border_strong` `#767676` y `focus` `#1F4E79`, más un comentario con el papel y el ratio de contraste medido de cada superficie

**Aceptación**

1. **WHEN** `infrastructure.theme.COLORS` is imported **THE SYSTEM SHALL** contain the keys `background`, `surface_sunken`, `border_strong` and `focus` with the literal values the design system states.
2. **WHEN** `infrastructure.theme.COLORS` is imported **THE SYSTEM SHALL** still contain every key it had before this task, with the same value.
3. **WHEN** every value in `COLORS` is read **THE SYSTEM SHALL** find each one is a 7-character `#RRGGBB` string.
4. **WHEN** `uv run pytest tests/report tests/domain` runs **THE SYSTEM SHALL** exit 0 with 0 failed and 0 skipped.
5. **WHEN** `uv run pytest tests/domain tests/ai tests/report` runs **THE SYSTEM SHALL** still report exactly 180 passed.

**Verify**

```powershell
uv run python -c "from infrastructure.theme import COLORS; esperado={'background':'#FFFFFF','surface_sunken':'#EBEEF3','border_strong':'#767676','focus':'#1F4E79','ink':'#1A1A1A','muted':'#5A5A5A','rule':'#C8C8C8','surface':'#F7F8FA','band_outer':'#DCE3EC','band_inner':'#9FB3C8','median':'#334E68','ok':'#2E6B4F','warn':'#8A6D1F','risk':'#8C2F2F'}; faltan=[k for k,v in esperado.items() if COLORS.get(k)!=v]; assert not faltan, faltan; malos=[k for k,v in COLORS.items() if not (len(v)==7 and v.startswith('#'))]; assert not malos, malos; print('paleta OK', len(COLORS))"; if ($LASTEXITCODE -ne 0) { throw 'la paleta no tiene las superficies nuevas o ha perdido alguna vieja' }
uv run pytest tests/report tests/domain -q; if ($LASTEXITCODE -ne 0) { throw 'la ampliacion de la paleta ha roto el informe' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
$n = (uv run pytest tests/domain tests/ai tests/report --collect-only -q 2>&1 | Select-String -Pattern '^(\d+) tests collected').Matches[0].Groups[1].Value; if ([int]$n -ne 180) { throw "la suite rescatada tiene $n pruebas, se esperaban 180" }
```

**Checkpoint**

```powershell
git add -A; git commit -m "E2-T2: la paleta gana fondo, superficie hundida, borde de control y foco"
git tag step-09-paleta
```

### `E2-T3` — Formulario de operación

**Depende de:** `E1-T6` · **Prioridad:** p0

Un `forms.Form`, no un `ModelForm`: aquí no se guarda un formulario, se guarda un `AnalysisResult`.
Las opciones de `transaction_type` se generan **desde `SUPPORTED_TRANSACTION_TYPES`**, no se escriben
a mano, para que cuando la fase 2 añada un tipo el desplegable lo recoja solo. El `clean()` construye
el `Transaction` de pydantic y traduce su `ValidationError` a errores de formulario —los de campo, al
campo; los del modelo entero, a error no asociado— de modo que el usuario vea **un solo conjunto de
errores** y no dos validaciones en cascada con mensajes distintos.

**Ficheros**
- `apps/analisis/forms.py` — nuevo; `CasoForm`, con `titulo` opcional derivado de `description`
- `tests/web/test_forms.py` — nuevo

**Aceptación**

1. **WHEN** the form receives a valid payload **THE SYSTEM SHALL** expose a `tp_domain.models.Transaction` in `cleaned_data["transaction"]`.
2. **WHEN** `payer_country` and `recipient_country` are equal **THE SYSTEM SHALL** be invalid and SHALL surface the domain message about two distinct jurisdictions as a non-field error.
3. **WHEN** `transaction_type` is a value outside `SUPPORTED_TRANSACTION_TYPES` **THE SYSTEM SHALL** be invalid and the rendered select SHALL NOT have offered that value.
4. **WHEN** `amount_eur` is `0` or `rate_percent` is `101` **THE SYSTEM SHALL** be invalid with the error attached to that specific field.
5. **WHEN** `effective_date` is missing **THE SYSTEM SHALL** be invalid, because there is no today default.
6. **WHEN** `titulo` is submitted empty **THE SYSTEM SHALL** derive a non-empty title of at most 160 characters from `description`.

**Verify**

```powershell
uv run pytest tests/web/test_forms.py -q; if ($LASTEXITCODE -ne 0) { throw 'las pruebas del formulario fallan' }
if ((Get-Content -Raw 'apps/analisis/forms.py') -notmatch 'SUPPORTED_TRANSACTION_TYPES') { throw 'las opciones de tipo no se derivan del dominio' }
uv run ruff check apps tests/web; if ($LASTEXITCODE -ne 0) { throw 'ruff falla' }
uv run mypy apps config; if ($LASTEXITCODE -ne 0) { throw 'mypy falla' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A; git commit -m "E2-T3: formulario de operacion sobre el Transaction del dominio"
git tag step-10-formulario
```

### `E2-T4` — Vista de análisis: POST, motor, persistencia con propietario

**Depende de:** `E1-T7`, `E2-T3` · **Prioridad:** p0

La rebanada vertical, con plantillas mínimas provisionales que E2-T5 sustituye. `services.py` llama al
motor, vuelca el resultado y crea la fila **con `usuario` puesto**; sin IA todavía —eso es la epic
03— y **sin nada de HTTP dentro**. `detalle` usa la guarda de la epic 01 y no consulta `Caso` por su
cuenta. Amplía `tests/web/test_aislamiento.py` con el caso cruzado del detalle: una ruta con
propietario y sin su prueba de aislamiento es una ruta que nadie ha comprobado.

**Ficheros**
- `apps/analisis/services.py` — nuevo; `crear_caso(usuario, transaction, titulo) -> Caso`, con evento de `structlog`
- `apps/analisis/views.py` — nuevo; `formulario` (GET `/`), `crear` (POST `/casos/`), `detalle` (GET `/casos/<uuid:pk>/`)
- `apps/analisis/urls.py`, `config/urls.py` — nuevo y edita; `app_name = "analisis"` y rutas con nombre
- `tests/web/test_analisis_view.py` — nuevo
- `tests/web/test_aislamiento.py` — edita: añade el caso cruzado del detalle

**Aceptación**

1. **WHEN** `GET /` is requested by an authenticated user **THE SYSTEM SHALL** respond `200` with an empty form.
2. **WHEN** `POST /casos/` receives a valid payload **THE SYSTEM SHALL** respond `302` to the case detail and SHALL create exactly one `Caso` row whose `usuario` is the requesting user.
3. **WHEN** `POST /casos/` receives an invalid payload **THE SYSTEM SHALL** respond `422` and SHALL create zero `Caso` rows.
4. **WHEN** `GET` on the detail of a case owned by another user is requested **THE SYSTEM SHALL** respond `404`, because the guard is the only reader.
5. **WHEN** the persisted row is read back **THE SYSTEM SHALL** have `engine_version`, `dataset_version` and `has_ai_explanation` equal to the values derived from `payload` at save time.
6. **WHEN** a transaction is submitted whose industry matches no comparable **THE SYSTEM SHALL** still respond `302` and persist a case carrying a `no_comparables` risk factor, because an uncomputable range is a result and not a failure.

**Verify**

```powershell
uv run pytest tests/web/test_analisis_view.py tests/web/test_aislamiento.py -q; if ($LASTEXITCODE -ne 0) { throw 'el ciclo de analisis o el aislamiento fallan' }
if ((Get-Content -Raw 'apps/analisis/views.py') -match 'tp_domain\.calculations') { throw 'la vista importa el motor; debe pasar por services.py' }
$sueltas = Select-String -Path (Get-ChildItem 'apps/analisis' -Recurse -Filter '*.py' -File).FullName -Pattern 'Caso\.objects' -ErrorAction SilentlyContinue; if ($sueltas) { throw 'hay consultas directas a Caso.objects fuera de apps/comun' }
uv run python manage.py check; if ($LASTEXITCODE -ne 0) { throw 'el gate de E1-T1 ha dejado de pasar' }
uv run pytest tests/web -q; if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A; git commit -m "E2-T4: POST valida, ejecuta el motor, persiste con propietario y redirige"
git tag step-11-vista-analisis
```

### `E2-T5` — Plantilla base y plantilla de resultado

**Depende de:** `E2-T4` · **Prioridad:** p0

El rango es **el protagonista**: el SVG a ancho completo y por encima de todo lo demás, no un adorno
lateral. Debajo, en este orden: posición y defendibilidad, tarjetas de jurisdicción, factores de
riesgo, fuentes citadas, sección de IA (o su ausencia declarada) y el botón de descarga. Deja en el
pie el hueco del aviso de privacidad que rellena la epic 04. Las plantillas **no calculan nada** y no
escriben ninguna URL a mano.

**Ficheros**
- `templates/base.html` — nuevo; `lang="es"`, enlace de salto, landmarks, pie con `role="contentinfo"` y el aviso de datos sintéticos
- `templates/analisis/form.html` — nuevo
- `templates/analisis/detalle.html` y `templates/partials/{_benchmark,_jurisdictions,_risk_factors}.html` — nuevos
- `templates/{400,403,404,405,500}.html` — nuevos
- `tests/web/test_result_template.py` — nuevo

**Aceptación**

1. **WHEN** a detail page is rendered for a case with comparables **THE SYSTEM SHALL** include an `svg` element for the benchmark range inside `main`.
2. **WHEN** a detail page is rendered for a case with no accepted comparables **THE SYSTEM SHALL** NOT include an `svg` element and SHALL include the text stating no range could be calculated.
3. **WHEN** a detail page is rendered **THE SYSTEM SHALL** contain one jurisdiction card per assessment, each naming its country and its rule label from `infrastructure.theme`.
4. **WHEN** a case has zero risk factors **THE SYSTEM SHALL** render the literal empty-state text, never an empty container.
5. **WHEN** any page is rendered **THE SYSTEM SHALL** contain `lang="es"`, exactly one `h1`, one `main` with id `contenido`, and a skip link whose href is `#contenido`.
6. **WHEN** any authenticated page is rendered **THE SYSTEM SHALL** contain the permanent synthetic-data notice in the footer.

**Verify**

```powershell
uv run pytest tests/web/test_result_template.py -q; if ($LASTEXITCODE -ne 0) { throw 'las pruebas de plantilla fallan' }
$rutasAMano = Select-String -Path (Get-ChildItem 'templates' -Recurse -Filter '*.html' -File).FullName -Pattern 'href="/casos|action="/casos|href="/fuentes|action="/entrar' -ErrorAction SilentlyContinue; if ($rutasAMano) { throw 'hay URLs escritas a mano en las plantillas' }
uv run pytest tests/web -q; if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A; git commit -m "E2-T5: plantilla base y detalle con el rango como protagonista"
git tag step-12-plantillas
```

### `E2-T6` — Tokens de diseño: `theme.py` a CSS

**Depende de:** `E2-T2`, `E2-T5` · **Prioridad:** p0

Cierra el contrato entre pantalla e informe: el CSS deja de tener colores literales y consume
variables generadas desde el mismo diccionario que usa el PDF. `scripts/__init__.py` es lo que hace
que `python -m scripts.build_tokens` encuentre `infrastructure`; la forma directa pondría `scripts/`
en `sys.path[0]` y fallaría. El modo `--check` no escribe nada y sale **0** si el fichero en disco
coincide con lo que generaría, **1** si no; el 2 queda para errores de uso.

**Ficheros**
- `scripts/__init__.py` — nuevo, vacío
- `scripts/build_tokens.py` — nuevo; genera `static/css/tokens.css`, acepta `--check`
- `static/css/tokens.css` — nuevo, generado y **versionado**
- `static/css/app.css` — nuevo; solo `var(--tpip-*)`
- `tests/web/test_theme_tokens.py` — nuevo

**Aceptación**

1. **WHEN** `uv run python -m scripts.build_tokens --check` runs against a synchronised tree **THE SYSTEM SHALL** exit 0 and write nothing.
2. **WHEN** `static/css/tokens.css` is read **THE SYSTEM SHALL** declare one custom property for every key of `infrastructure.theme.COLORS`, with the identical hex value.
3. **WHEN** `static/css/app.css` is searched for a hash followed by three or six hex digits **THE SYSTEM SHALL** find zero matches.
4. **WHEN** `uv run python scripts/build_tokens.py` is run as a plain file path **THE SYSTEM SHALL** fail to import `infrastructure`, which is the documented reason the project invokes scripts with `-m`.
5. **WHEN** `uv run pytest tests/web/test_theme_tokens.py` runs **THE SYSTEM SHALL** exit 0 with 0 failed and 0 skipped.

**Verify**

```powershell
uv run python -m scripts.build_tokens --check; if ($LASTEXITCODE -ne 0) { throw "tokens.css esta desincronizado con theme.py (codigo $LASTEXITCODE)" }
uv run pytest tests/web/test_theme_tokens.py -q; if ($LASTEXITCODE -ne 0) { throw 'las pruebas de tokens fallan' }
$literales = Select-String -Path 'static/css/app.css' -Pattern '#[0-9A-Fa-f]{3,6}\b' -ErrorAction SilentlyContinue; if ($literales) { throw 'app.css contiene colores literales' }
uv run ruff check scripts; if ($LASTEXITCODE -ne 0) { throw 'ruff falla sobre scripts/' }
uv run pytest tests/web -q; if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A; git commit -m "E2-T6: tokens de diseno generados desde theme.py"
git tag step-13-tokens
git ls-files --error-unmatch static/css/tokens.css; if ($LASTEXITCODE -ne 0) { throw 'tokens.css no ha quedado versionado' }
```

### `E2-T7` — Descarga del informe PDF

**Depende de:** `E2-T4`, `E2-T6` · **Prioridad:** p0

La vista obtiene el caso **a través de la guarda**, lo rehidrata y llama a `render_report_bytes`. El
literal que se comprueba **no es una predicción**: `DATOS SINTÉTICOS` son las dos primeras palabras
del `disclaimer` de `TPIP_DATASET_V1` en `tp_domain/sources.py`, y una prueba rescatada ya lo
comprueba hoy sobre el PDF generado en memoria. Aquí se comprueba lo mismo **sobre el PDF que sirve la
web**, que es lo que el usuario se lleva. Amplía `test_aislamiento.py` con el caso cruzado del
informe.

**Ficheros**
- `apps/analisis/views.py` — edita: añade `informe`
- `apps/analisis/urls.py` — edita: la ruta `analisis:informe`
- `templates/analisis/detalle.html` — edita: el botón de descarga
- `tests/web/test_informe_view.py` — nuevo
- `tests/web/test_aislamiento.py` — edita: añade el caso cruzado del informe

**Aceptación**

1. **WHEN** the report of a case is requested by its owner **THE SYSTEM SHALL** respond `200` with content type `application/pdf`.
2. **WHEN** the served PDF is parsed with `pypdf` **THE SYSTEM SHALL** contain the literal `DATOS SINTÉTICOS`, the immovable notice, present in the document the user actually downloads.
3. **WHEN** the response headers are read **THE SYSTEM SHALL** carry `Content-Disposition` with `attachment` and a filename containing the case UUID.
4. **WHEN** the report of a case owned by another user is requested **THE SYSTEM SHALL** respond `404` and SHALL NOT generate a PDF.
5. **WHEN** the report view runs **THE SYSTEM SHALL** make no network call, producing the PDF from the persisted payload alone.
6. **WHEN** the same case is downloaded twice **THE SYSTEM SHALL** produce a document with the same synthetic-data notice both times and SHALL NOT create any new `Caso` row.

**Verify**

```powershell
uv run pytest tests/web/test_informe_view.py tests/web/test_aislamiento.py -q; if ($LASTEXITCODE -ne 0) { throw 'la descarga del informe o su aislamiento fallan' }
uv run pytest tests/web -q; if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'las pruebas de informe rescatadas fallan' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A; git commit -m "E2-T7: descarga del informe PDF desde el caso persistido"
git tag step-14-informe
```

---

## Aceptación de la epic

La epic está hecha cuando todas sus tareas están en `done` **y**:

1. **WHEN** an authenticated user submits a valid operation and then downloads its report **THE SYSTEM SHALL** persist one case, render the range as an `svg`, and serve a PDF containing the literal `DATOS SINTÉTICOS`.
2. **WHEN** a user requests the detail or the report of a case owned by someone else **THE SYSTEM SHALL** respond `404` in both cases.
3. **WHEN** the rescued suite runs **THE SYSTEM SHALL** still report exactly 180 passed, proving neither defect fix cost coverage.
4. **WHEN** `uv run python -m scripts.build_tokens --check` runs **THE SYSTEM SHALL** exit 0, proving screen and report share one palette.

```powershell
uv run ruff check .; if ($LASTEXITCODE -ne 0) { throw 'lint' }
uv run mypy .; if ($LASTEXITCODE -ne 0) { throw 'tipos' }
uv run pytest; if ($LASTEXITCODE -ne 0) { throw 'suite completa' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'red de seguridad' }
uv run python -m scripts.build_tokens --check; if ($LASTEXITCODE -ne 0) { throw 'tokens desincronizados' }
uv run pytest tests/web/test_informe_view.py tests/web/test_aislamiento.py -q; if ($LASTEXITCODE -ne 0) { throw 'informe o aislamiento' }
```

## Trampas

- **Renombrar una clave de `COLORS` en vez de añadir.** Rompe `pdf_report.py` y las 38 pruebas de
  informe, y con ellas el recuento de 180. La ampliación es estrictamente aditiva.
- **Añadir una prueba a `tests/report` para cubrir los tokens nuevos.** Cambia el recuento. Va en
  `tests/web/test_theme_tokens.py`.
- **Ejecutar `python scripts/build_tokens.py` en vez de `python -m scripts.build_tokens`.** Falla con
  un error de importación de `infrastructure` que parece un problema de instalación y no lo es.
- **Llamar al motor desde la vista.** La frontera dice que las vistas solo hacen HTTP y delegan en
  `services.py`. Saltársela funciona hoy y complica cada cambio posterior.
- **Consultar `Caso.objects` en una vista.** La guarda es el único camino, y el `verify` de E2-T4 lo
  comprueba buscando en el código.
- **Devolver 200 con errores de formulario.** Es la convención de Django y aquí es un defecto: el 422
  es lo que hace comprobable por máquina que el formulario rechazó la entrada.
- **Escribir un color literal en `app.css`.** El `verify` de E2-T6 lo detecta, pero lo caro es haberlo
  extendido por veinte reglas antes de que salte.

## Antes de seguir

- [ ] Las siete tareas están en `done` en `tasks.json`; ninguna en `in_progress`.
- [ ] Pasaron **todos** los comandos `verify` de cada tarea, no solo el primero.
- [ ] No se editó ningún comando `verify`, y no se saltó ninguno porque un fichero no existiera.
- [ ] Las siete etiquetas están en git: `step-08-modelo-fijado` … `step-14-informe`.
- [ ] El gate pasa limpio desde la raíz del proyecto.
- [ ] Los seis contratos «Producidos» existen con la firma indicada.
- [ ] No se modificó ningún fichero fuera del subárbol. En particular, de `tp_domain/` no se tocó
      nada, y de `ai/` e `infrastructure/` solo los dos ficheros que las tareas T1 y T2 nombran.
- [ ] `.env.example` no necesitaba variables nuevas: esta epic no añade ninguna.
- [ ] Un commit por tarea, cada uno prefijado con su id, cada uno seguido de su etiqueta.
