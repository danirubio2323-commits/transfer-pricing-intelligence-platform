# Epic 04: Precedentes, evidencia y cierre

> Después de esta epic existe una biblioteca curada de precedentes, un arnés de evaluación con puerta
> de regresión que sale distinto de cero cuando la calidad baja, una copia de seguridad cuya
> restauración se verifica comparando recuentos de filas, la accesibilidad fijada con pruebas junto al
> aviso de privacidad, los ajustes de producción auditados y la integración continua ejecutando el
> gate completo. Con esto el proyecto está terminado.

| | |
|---|---|
| **Epic id** | `04-precedentes-evidencia-y-cierre` |
| **Tareas** | `E4-T1` … `E4-T6` |
| **Depende de** | `01-cimientos-y-cuentas`, `02-analisis-y-presentacion`, `03-gasto-ia-y-contenido` |
| **Desbloquea** | nada — es la última |
| **Paralela con** | ninguna |

No necesitas ningún otro fichero para completar esta epic. Todo lo de abajo está repetido aquí a
propósito.

---

## Pila

Django 5.2 · Python 3.12 · plantillas de Django · CSS plano con variables generadas desde
`infrastructure/theme.py` · SQLite · ORM de Django para la persistencia y pydantic para el dominio ·
WhiteNoise para los estáticos · ejecución local en Windows 10 con PowerShell; la integración continua
corre en `ubuntu-latest`.
Gestor de paquetes: `uv`. Python y dependencias fijados en `pyproject.toml` y resueltos en `uv.lock`
— **léelos, nunca adivines una versión**.

| Tarea | Comando |
|---|---|
| Servidor de desarrollo | `uv run python manage.py runserver` |
| Comprobar el proyecto | `uv run python manage.py check` |
| Comprobar despliegue | `uv run python manage.py check --deploy --settings=config.settings.production` |
| Tipos | `uv run mypy .` |
| Lint · formato | `uv run ruff check .` · `uv run ruff format --check .` |
| Pruebas (un fichero) | `uv run pytest tests/web/test_copia.py` |
| **Red de seguridad** | `uv run pytest tests/domain tests/ai tests/report` |
| Estáticos | `uv run python manage.py collectstatic --noinput` |
| Reindexar evaluación | `uv run python manage.py reindexar_evaluacion` |
| Arnés de evaluación | `uv run python manage.py evaluar --contra-linea-base` |
| Copia de seguridad | `uv run python manage.py copia_seguridad` |
| Restaurar y verificar | `uv run python manage.py restaurar_copia --copia <ruta> --destino <dir>` |

**Gate:** `uv run ruff check . && uv run mypy . && uv run pytest` pasa antes de dar por hecha
cualquier tarea de esta epic.

**Ninguna prueba de esta epic toca la red.** El arnés de evaluación se ejercita con dobles y con sus
puntuadores deterministas; la integración continua corre **sin clave de API**, de modo que la ruta de
degradación se ejercita en cada push. Si te ves necesitando una clave real para pasar un `verify`, la
prueba está mal escrita.

## Subárbol de directorios

Solo lo que esta epic toca:

```
apps/analisis/
  models.py                     # EXISTE — se AMPLÍA en E4-T1: CasoContrastado
  admin.py                      # EXISTE — se AMPLÍA: acción "Curar como precedente"
  views.py  urls.py             # EXISTEN — se AMPLÍAN: /contrastados/
apps/comun/
  management/commands/
    copia_seguridad.py          # NUEVO — copia EN LÍNEA de SQLite, más el fichero de recuentos
    restaurar_copia.py          # NUEVO — restaura y COMPARA recuentos de las ocho tablas
apps/evaluacion/                # NUEVO — el arnés
  __init__.py  apps.py  admin.py            # NUEVO
  models.py                     # NUEVO — CasoEvaluacion, EjecucionEvaluacion
  puntuadores.py                # NUEVO — de lo más barato a lo más caro
  management/commands/
    reindexar_evaluacion.py     # NUEVO
    evaluar.py                  # NUEVO — --fijar-linea-base, --contra-linea-base
  migrations/__init__.py        # NUEVO
evaluacion/casos/*.json         # NUEVO — el conjunto dorado, EN CONTROL DE VERSIONES
config/settings/
  base.py                       # EXISTE — se AMPLÍA: WhiteNoise y STORAGES
  production.py                 # NUEVO — DEBUG off, cabeceras y cookies seguras
templates/
  base.html                     # EXISTE — se AMPLÍA: el aviso de privacidad en el pie
  analisis/form.html            # EXISTE — se AMPLÍA: el aviso junto al formulario
  analisis/detalle.html         # EXISTE — se AMPLÍA: role="img" y <title> en el SVG
  analisis/contrastados.html    # NUEVO
  analisis/contrastado.html     # NUEVO
  privacidad.html               # NUEVO — la única página nueva de E4-T4
static/css/app.css              # EXISTE — se AMPLÍA: :focus-visible, objetivos 24px, overflow-x
.github/workflows/ci.yml        # NUEVO
README.md                       # EXISTE — se REESCRIBE la puesta en marcha
tests/web/
  test_contrastados.py          # NUEVO
  test_evaluacion.py            # NUEVO
  test_copia.py                 # NUEVO
  test_accesibilidad.py         # NUEVO
  test_seguridad.py             # NUEVO
  test_aislamiento.py           # EXISTE — se AMPLÍA en E4-T1
```

Todo lo que quede fuera de este subárbol está fuera de alcance. Si una tarea parece exigir editar un
fichero que no está aquí, para y reporta.

## Modelo de datos que se toca aquí

| Entidad | Tabla | Campos | Notas |
|---|---|---|---|
| `CasoContrastado` | `casos_contrastados` | `slug` (unique), `titulo`, `caso_origen` (FK `SET_NULL`), `payload` (JSON **congelado**), `comentario_curador`, `publicado`, `curado_por` (FK `PROTECT`), `creado_el` | Visible para **toda** cuenta autenticada. Curar **no desprivatiza**: se copia el `payload`, y el caso original sigue siendo de su dueño |
| `CasoEvaluacion` | `casos_evaluacion` | `id` (slug, PK), `descripcion`, `entrada` (JSON), `propiedades_esperadas` (JSON), `activo` | **Índice reconstruible** desde `evaluacion/casos/*.json`, igual que `Ficha` desde los `.md` |
| `EjecucionEvaluacion` | `ejecuciones_evaluacion` | `ejecutada_el` (indexada), `sha_commit`, `modelo`, `prompt_version`, `casos_totales`, `casos_acertados`, `tasa_acierto`, `coste_total_eur`, `latencia_p50_ms`, `latencia_p95_ms`, `es_linea_base`, `detalle` (JSON) | `sha_commit` es lo que hace reproducible una tasa de acierto. El coste va **junto a** la precisión: una mejora que triplica el coste es una decisión, no una mejora |
| `Caso`, `Usuario`, `Ficha`, `UnidadEstudio`, `LlamadaLLM` | — | Solo se leen, y se cuentan en la copia de seguridad | Ninguna gana campos aquí |

`caso_origen` es `SET_NULL` porque **el precedente sobrevive a su origen**: un caso curado y publicado
no debe evaporarse porque alguien limpie su caso privado.

## Contratos

**Consumidos** — ya existen, no los reconstruyas:

| De | Interfaz | Garantía |
|---|---|---|
| `01` | `apps.comun.guardas.caso_del_usuario(usuario, pk)` | El `Caso` vivo de ese usuario, o `Http404` |
| `01` | `apps.analisis.models.Caso` | Gestor `objects` que excluye los borrados; `todos` que los incluye |
| `01` | `apps.comun.middleware.ExigirAutenticacion` | Toda ruta exige sesión salvo la lista blanca |
| `02` | `templates/base.html` | Bloque `contenido` y pie con `role="contentinfo"` — **con el hueco del aviso de privacidad ya previsto** |
| `02` | `templates/partials/{_benchmark,_jurisdictions,_risk_factors}.html` | Pintan un `AnalysisResult`; un precedente se lee igual que un caso |
| `02` | `scripts/build_tokens.py` | `--check` sale 0 si está sincronizado, **1** si no, 2 en error de uso |
| `03` | `apps.ia.registro.registrar_llamada` | Único escritor de `LlamadaLLM`; acepta `proposito` |
| `03` | `apps.ia.cuota.coste_de(usage, modelo)` | Coste a partir del uso **reportado**; `0` si no hay tarifas |
| `03` | `apps.corpus.models.Ficha`, `apps.estudio.models.UnidadEstudio` | Tablas a contar en la copia |
| Rescatado | `ai.validators` | `MIN_WORDS` y `MAX_WORDS`, y la validación de referencias legales contra el registro emitido |

**Producidos** — nada depende de esta epic: es la última. Lo que produce es el proyecto terminado.

## Convenciones que muerden en esta área

- **Una copia sin restaurar no es una copia.** El criterio no es que exista el fichero, es que la
  restauración en un directorio limpio **coincida en recuento de filas** en las ocho tablas.
- **La copia usa la API de copia en línea de SQLite**, nunca una copia de fichero: copiar
  `db.sqlite3` con el proceso escribiendo produce un fichero corrupto **sin avisar**.
- **La puerta de regresión sale con 1 cuando la tasa baja, no «con algo distinto de cero».** Un error
  de uso también sale distinto de cero, y una puerta escrita así pasaría en vacío para siempre.
- **El conjunto dorado vive en control de versiones**, en `evaluacion/casos/*.json`. Un conjunto que
  solo existe en una base de datos no se revisa en un *pull request*, y entonces deja de ser dorado.
- **Los puntuadores van de lo más barato a lo más caro y paran en el primero que decide.** La mayoría
  de los casos se resuelven en la capa determinista, que no cuesta nada.
- **Toda llamada del arnés lleva `proposito="evaluacion"`.** Sin eso, una pasada consumiría el tope
  mensual de un usuario real.
- **El aviso de privacidad va en dos sitios**, no en uno: el pie de toda página autenticada **y** junto
  al formulario de creación, que es el momento en que el usuario está a punto de escribir el dato.
- **`SESSION_COOKIE_SECURE` y `CSRF_COOKIE_SECURE` solo en producción.** Activarlos en local, donde no
  hay TLS, deja la aplicación inutilizable.
- **La integración continua ejecuta el gate de §20.1, en el mismo orden.** Si una comprobación está en
  el gate, está en CI. Sin excepciones y sin secretos.

Reglas completas del proyecto: `CLAUDE.md`. Reglas de área: `.claude/rules/capa-web.md`,
`.claude/rules/gasto-y-ia.md` y `.claude/rules/estilo-visual.md`.

---

## Tareas

En el mismo orden que `tasks.json`.

### `E4-T1` — `CasoContrastado`: biblioteca curada de precedentes

**Depende de:** `E3-T1` · **Prioridad:** p1

Un `CasoContrastado` es visible para **toda cuenta autenticada**; un `Caso` es privado y lo filtra la
guarda. La acción del panel «Curar como precedente» **copia** el `payload` a una fila nueva en
borrador, con `caso_origen` apuntando al original: curar no desprivatiza nada, y el `payload`
congelado no sigue vivo al caso origen —un precedente que cambia solo no es un precedente—. Reutiliza
los tres parciales de la epic 02: un precedente se lee igual que un caso. Amplía
`tests/web/test_aislamiento.py` para comprobar que curar deja el original tan privado como estaba.

**Ficheros**
- `apps/analisis/models.py` — edita: añade `CasoContrastado`, `db_table = "casos_contrastados"`
- `apps/analisis/admin.py` — edita: registro y acción «Curar como precedente»
- `apps/analisis/views.py`, `apps/analisis/urls.py` — edita: `/contrastados/` y `/contrastados/<slug>/`
- `templates/analisis/contrastados.html`, `templates/analisis/contrastado.html` — nuevos
- `tests/web/test_contrastados.py` — nuevo, y edita `tests/web/test_aislamiento.py`

**Aceptación**

1. **WHEN** a curated case is published **THE SYSTEM SHALL** make it visible at its slug to every authenticated user, not only to its curator.
2. **WHEN** a curated case is not published **THE SYSTEM SHALL** respond `404` at its slug for a non-staff user.
3. **WHEN** a case is curated **THE SYSTEM SHALL** copy its payload and SHALL leave the original case unchanged and still private, so requesting it as another user still returns `404`.
4. **WHEN** the origin case is later soft-deleted **THE SYSTEM SHALL** keep the published precedent readable, with its frozen payload intact.
5. **WHEN** a curated case is rendered **THE SYSTEM SHALL** show its curator comment, because a precedent without the reason it is one is just another row.
6. **WHEN** an anonymous request hits the precedent list **THE SYSTEM SHALL** respond `302` to the login page.

**Verify**

```powershell
uv run python manage.py makemigrations analisis; if ($LASTEXITCODE -ne 0) { throw 'makemigrations falla' }
uv run python manage.py makemigrations --check --dry-run; if ($LASTEXITCODE -ne 0) { throw "quedan cambios de modelo sin migrar (codigo $LASTEXITCODE)" }
uv run python manage.py migrate; if ($LASTEXITCODE -ne 0) { throw 'migrate falla' }
uv run pytest tests/web/test_contrastados.py tests/web/test_aislamiento.py -q; if ($LASTEXITCODE -ne 0) { throw 'la biblioteca de precedentes o el aislamiento fallan' }
uv run pytest tests/web -q; if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A; git commit -m "E4-T1: biblioteca curada de precedentes, copiada y congelada"
git tag step-22-contrastados
```

### `E4-T2` — Arnés de evaluación: conjunto dorado, puntuadores y puerta de CI

**Depende de:** `E3-T3` · **Prioridad:** p1

Sin esto los prompts se petrifican: nadie se atreve a tocarlos porque no hay forma de saber si el
cambio mejora o empeora, y la regresión la acaba descubriendo el usuario en un informe. El conjunto
dorado vive en `evaluacion/casos/*.json`, en el repositorio, para que un cambio se revise en un *pull
request*. Los puntuadores van de barato a caro y **paran en el primero que decide**: comprobaciones
deterministas primero —fuentes dentro del registro emitido, ninguna cifra nueva, extensión dentro de
`MIN_WORDS`/`MAX_WORDS`—, después coincidencias léxicas, y solo si no deciden, un juicio del modelo.
`--contra-linea-base` sale **1** si la tasa baja, **2** si no hay línea base, **0** si iguala o mejora.

El comando `evaluar` acepta **tres** opciones, y la tercera existe para que la puerta se pueda probar
sin esperar a una regresión real: `--fijar-linea-base` marca la ejecución actual como línea base;
`--contra-linea-base` compara contra ella; y `--autocomprobar-regresion` ejecuta el arnés con
puntuadores dobles contra una línea base deliberadamente inalcanzable y **debe salir con 1**. Sin esa
tercera opción, que la puerta *pueda* fallar sería una afirmación sin comprobar.

**Ficheros**
- `evaluacion/casos/*.json` — nuevos; el conjunto dorado versionado
- `apps/evaluacion/{__init__,apps,models,admin}.py` — nuevos; `CasoEvaluacion` y `EjecucionEvaluacion` con `sha_commit`
- `apps/evaluacion/puntuadores.py` — nuevo; las tres capas, en orden de coste
- `apps/evaluacion/management/commands/{reindexar_evaluacion,evaluar}.py` — nuevos. **La línea base
  se fija en esta misma tarea**, con `evaluar --fijar-linea-base`, antes de la primera comparación:
  el modelo de datos declara que existe exactamente una fila con `es_linea_base` verdadero, y sin
  esta invocación nada la establece y `--contra-linea-base` saldría siempre con 2
- `config/settings/base.py` — edita: `"apps.evaluacion"` en `INSTALLED_APPS`; y `tests/web/test_evaluacion.py` — nuevo

**Aceptación**

1. **WHEN** `evaluar --fijar-linea-base` runs **THE SYSTEM SHALL** create exactly one evaluation run marked as the baseline, so later comparisons have something to compare against and do not exit `2`.
2. **WHEN** the harness runs against the baseline and the hit rate equals or exceeds it **THE SYSTEM SHALL** exit `0`.
3. **WHEN** the hit rate falls below the baseline **THE SYSTEM SHALL** exit `1` specifically, so a usage error cannot pass for a regression.
4. **WHEN** no baseline row exists **THE SYSTEM SHALL** exit `2` with a message saying so, distinguishable from both a pass and a regression.
5. **WHEN** an evaluation run is written **THE SYSTEM SHALL** record the commit sha, the total cost and the p50 and p95 latencies next to the hit rate.
6. **WHEN** a case is decided by the deterministic scorer **THE SYSTEM SHALL** NOT invoke any more expensive scorer for that case, and SHALL record zero provider calls for it.

**Verify**

```powershell
uv run python manage.py makemigrations evaluacion; if ($LASTEXITCODE -ne 0) { throw 'makemigrations falla' }
uv run python manage.py migrate; if ($LASTEXITCODE -ne 0) { throw 'migrate falla' }
uv run python manage.py reindexar_evaluacion; if ($LASTEXITCODE -ne 0) { throw 'el reindexado del conjunto dorado falla' }
uv run python manage.py reindexar_evaluacion; if ($LASTEXITCODE -ne 0) { throw 'el reindexado no es idempotente' }
uv run python manage.py evaluar --fijar-linea-base; if ($LASTEXITCODE -ne 0) { throw 'no se ha podido fijar la linea base' }
uv run python manage.py evaluar --contra-linea-base; if ($LASTEXITCODE -ne 0) { throw "comparar contra la linea base recien fijada deberia salir 0 (codigo $LASTEXITCODE)" }
uv run pytest tests/web/test_evaluacion.py -q; if ($LASTEXITCODE -ne 0) { throw 'el arnes de evaluacion falla' }
uv run python manage.py evaluar --autocomprobar-regresion; if ($LASTEXITCODE -ne 1) { throw "con una tasa por debajo de la linea base se esperaba codigo 1, obtenido $LASTEXITCODE" }
uv run pytest tests/web -q; if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A; git commit -m "E4-T2: arnes de evaluacion con conjunto dorado, puntuadores por coste y puerta de CI"
git tag step-23-evaluacion
```

### `E4-T3` — Copia de seguridad y restauración verificada por recuento de filas

**Depende de:** `E1-T6`, `E3-T2`, `E3-T5` · **Prioridad:** p0

Un fichero SQLite en disco sin copia es un fichero que un día no está, y con él se van todos los
casos, todo el gasto registrado y toda la biblioteca de precedentes. Usa la **API de copia en línea de
SQLite** (`sqlite3.Connection.backup`), nunca una copia de fichero: copiar la base con el proceso
escribiendo produce un fichero corrupto sin avisar. Escribe junto a la copia un `.recuentos.json` con
las filas de **cada una de las ocho tablas** — ese fichero es lo que convierte la restauración en
verificable. `restaurar_copia` restaura en un destino limpio y **compara**: sale `0` si todo coincide,
`1` si algún recuento difiere nombrando la tabla y los dos números, y `2` si la copia o su fichero de
recuentos no existen.

**Ficheros**
- `apps/comun/management/commands/copia_seguridad.py` — nuevo
- `apps/comun/management/commands/restaurar_copia.py` — nuevo
- `tests/web/test_copia.py` — nuevo; crea filas en las ocho tablas, copia, restaura y compara

**Aceptación**

1. **WHEN** the backup command runs **THE SYSTEM SHALL** exit `0` and write both a database file and its counts file under the backups directory.
2. **WHEN** the backup is taken **THE SYSTEM SHALL** use SQLite's online backup API, never a file copy, because a file copy of a database being written is silently corrupt.
3. **WHEN** the restore command restores into a clean directory **THE SYSTEM SHALL** exit `0` and the row count of each of the eight tables SHALL equal the count recorded at backup time.
4. **WHEN** a restored table's row count differs from the recorded one **THE SYSTEM SHALL** exit `1` specifically, naming the table and both numbers.
5. **WHEN** the named backup or its counts file does not exist **THE SYSTEM SHALL** exit `2`, distinguishable from a count mismatch.
6. **WHEN** the backups directory is checked against the ignore file **THE SYSTEM SHALL** find it excluded, because backups carry data and not code.

**Verify**

```powershell
uv run python manage.py copia_seguridad; if ($LASTEXITCODE -ne 0) { throw 'la copia de seguridad falla' }
$copia = Get-ChildItem 'copias' -Filter '*.sqlite3' | Sort-Object LastWriteTime | Select-Object -Last 1; if (-not $copia) { throw 'no se ha escrito ninguna copia' }
$copia = Get-ChildItem 'copias' -Filter '*.sqlite3' | Sort-Object LastWriteTime | Select-Object -Last 1; if (-not (Test-Path ($copia.FullName -replace '\.sqlite3$', '.recuentos.json'))) { throw 'falta el fichero de recuentos' }
$copia = Get-ChildItem 'copias' -Filter '*.sqlite3' | Sort-Object LastWriteTime | Select-Object -Last 1; $destino = Join-Path $env:TEMP ("tpip-restauracion-" + [guid]::NewGuid().ToString('N')); uv run python manage.py restaurar_copia --copia $copia.FullName --destino $destino; $c = $LASTEXITCODE; Remove-Item -Recurse -Force $destino -ErrorAction SilentlyContinue; if ($c -ne 0) { throw "la restauracion no coincide en recuentos (codigo $c)" }
git check-ignore -q 'copias'; if ($LASTEXITCODE -ne 0) { throw "copias/ no esta ignorado (codigo $LASTEXITCODE)" }
uv run pytest tests/web/test_copia.py -q; if ($LASTEXITCODE -ne 0) { throw 'las pruebas de copia fallan' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A; git commit -m "E4-T3: copia de seguridad en linea y restauracion verificada por recuento de filas"
git tag step-24-copia
```

### `E4-T4` — Accesibilidad de las plantillas y aviso de privacidad

**Depende de:** `E2-T5`, `E3-T6`, `E3-T7` · **Prioridad:** p0

Aplica los requisitos de accesibilidad a las plantillas que ya existen y cierra el requisito de
transparencia: **el administrador ve los casos de todos los usuarios**, y eso no puede quedar
implícito. El aviso va en **dos sitios**: el pie de toda página autenticada y junto al formulario de
creación, que es el momento en que el usuario está a punto de escribir el dato. Estas comprobaciones
se hacen sobre el **HTML renderizado**, que es donde son observables; lo que un análisis estático no
puede decidir —orden de tabulación real, lector de pantalla, reflujo a 320 px— está en los gates
manuales del blueprint, no aquí.

**Ficheros**
- `templates/base.html` — edita: enlace de salto visible al foco, landmarks, y el aviso de privacidad en el `<footer role="contentinfo">`
- `templates/analisis/form.html` — edita: el mismo aviso antes del formulario; `<label for>` por campo; errores por `aria-describedby` y `role="alert"`; `autocomplete` en el acceso
- `templates/privacidad.html` y su ruta — nuevos; qué se guarda, dónde, cuánto y cómo se pide el borrado
- `static/css/app.css` — edita: `:focus-visible`, objetivos de 24×24 px, `prefers-reduced-motion`, `overflow-x: auto` en tablas
- `templates/analisis/detalle.html` — edita: el SVG con `role="img"` y `<title>`; y `tests/web/test_accesibilidad.py` — nuevo

**Aceptación**

1. **WHEN** any authenticated page is rendered **THE SYSTEM SHALL** contain the privacy notice in a footer with role `contentinfo`, stating that administrators can access any user's cases.
2. **WHEN** the case creation form is rendered **THE SYSTEM SHALL** show that same notice next to the form, before the user types anything.
3. **WHEN** any page is rendered **THE SYSTEM SHALL** contain `lang="es"`, exactly one `h1`, one `main`, one `header`, one `footer`, and a skip link whose href is `#contenido` as the first focusable element.
4. **WHEN** the form page is rendered **THE SYSTEM SHALL** emit a label whose `for` matches the id of every input and select on the page, so there are zero unlabelled controls.
5. **WHEN** the form is rendered after an invalid submission **THE SYSTEM SHALL** express every error as text inside an element with role `alert` or referenced by `aria-describedby`.
6. **WHEN** a detail page with a range is rendered **THE SYSTEM SHALL** emit the svg with role `img` and a non-empty title.

**Verify**

```powershell
uv run pytest tests/web/test_accesibilidad.py -q; if ($LASTEXITCODE -ne 0) { throw 'las comprobaciones de accesibilidad fallan' }
if ((Get-Content -Raw 'static/css/app.css') -notmatch ':focus-visible') { throw 'falta el estilo de foco visible' }
if ((Get-Content -Raw 'static/css/app.css') -notmatch 'prefers-reduced-motion') { throw 'el movimiento no respeta prefers-reduced-motion' }
if ((Get-Content -Raw 'templates/base.html') -notmatch 'role="contentinfo"') { throw 'falta el pie con el aviso de privacidad' }
if (-not (Test-Path 'templates/privacidad.html')) { throw 'falta la pagina de privacidad' }
uv run pytest tests/web -q; if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A; git commit -m "E4-T4: accesibilidad fijada con pruebas y aviso de privacidad visible"
git tag step-25-accesibilidad
```

### `E4-T5` — Seguridad, cabeceras y ajustes de producción

**Depende de:** `E4-T4` · **Prioridad:** p0

`config/settings/production.py` existe **para que la comprobación de seguridad pruebe algo real**:
`check --deploy` sobre un módulo que nadie usa no comprueba nada. Exige `DJANGO_SECRET_KEY` aquí y
solo aquí; en `local.py` sigue habiendo un valor de desarrollo, de modo que **ningún gate anterior se
rompe**. Las marcas seguras de cookie van solo en producción: activarlas en local, sin TLS, deja la
aplicación inutilizable. La comprobación de que producción no arranca sin clave **no se conforma con
«sale distinto de cero»** —un error de uso también lo haría—: comprueba que el fallo **nombra la
variable**.

**Ficheros**
- `config/settings/production.py` — nuevo; `DEBUG = False`, HSTS, `SECURE_SSL_REDIRECT`, `SECURE_CONTENT_TYPE_NOSNIFF`, `SECURE_REFERRER_POLICY`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `X_FRAME_OPTIONS`
- `config/settings/base.py` — edita: WhiteNoise en `MIDDLEWARE` detrás de `SecurityMiddleware`, y `STORAGES`
- `tests/web/test_seguridad.py` — nuevo

**Aceptación**

1. **WHEN** the deploy check runs against the production settings with the secret key set **THE SYSTEM SHALL** exit `0` with zero issues.
2. **WHEN** the production settings are imported without the secret key **THE SYSTEM SHALL** fail at import with an error naming that variable, and SHALL NOT fall back to a default secret.
3. **WHEN** a case is posted without a CSRF token **THE SYSTEM SHALL** respond `403` and create zero `Caso` rows.
4. **WHEN** any response is inspected **THE SYSTEM SHALL** carry `X-Content-Type-Options: nosniff` and `Referrer-Policy: same-origin`.
5. **WHEN** local settings are loaded **THE SYSTEM SHALL** leave the secure session cookie flag false, because enabling it without TLS would make the application unusable locally.
6. **WHEN** the ordinary check runs with the local settings **THE SYSTEM SHALL** still exit `0`, so the development gate does not regress.

**Verify**

```powershell
uv run pytest tests/web/test_seguridad.py -q; if ($LASTEXITCODE -ne 0) { throw 'las pruebas de seguridad fallan' }
$env:DJANGO_SECRET_KEY = 'clave-solo-para-esta-comprobacion-no-usar'; uv run python manage.py check --deploy --settings=config.settings.production; $c = $LASTEXITCODE; Remove-Item Env:\DJANGO_SECRET_KEY; if ($c -ne 0) { throw 'check --deploy senala problemas' }
$salida = uv run python -c "import os; os.environ.pop('DJANGO_SECRET_KEY', None); os.environ['DJANGO_SETTINGS_MODULE']='config.settings.production'; import django; django.setup(); print('ARRANCO SIN CLAVE')" 2>&1 | Out-String; if ($salida -match 'ARRANCO SIN CLAVE') { throw 'produccion arranca sin DJANGO_SECRET_KEY' }
$salida = uv run python -c "import os; os.environ.pop('DJANGO_SECRET_KEY', None); os.environ['DJANGO_SETTINGS_MODULE']='config.settings.production'; import django; django.setup()" 2>&1 | Out-String; if ($salida -notmatch 'DJANGO_SECRET_KEY') { throw "produccion fallo por otro motivo, no por la clave: $salida" }
uv run python manage.py check; if ($LASTEXITCODE -ne 0) { throw 'el gate local se ha roto' }
uv run pytest tests/web -q; if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A; git commit -m "E4-T5: ajustes de produccion, cabeceras de seguridad y WhiteNoise"
git tag step-26-seguridad
git ls-files --error-unmatch config/settings/production.py; if ($LASTEXITCODE -ne 0) { throw 'production.py no ha quedado versionado' }
```

### `E4-T6` — Integración continua, estáticos y cierre

**Depende de:** `E4-T1`, `E4-T2`, `E4-T3`, `E4-T5` · **Prioridad:** p0

La última tarea. CI ejecuta **exactamente** las órdenes del gate global, en el mismo orden, incluida la
puerta de regresión del arnés, y **sin secretos**: sin clave de API, de modo que la ruta de degradación
de la capa de IA se ejercita en cada push. Reescribe la puesta en marcha del `README.md` para `uv` y
Django, documentando el alta de la primera cuenta, los dos reindexados y la copia de seguridad. Y
comprueba que el gate de sincronía de tokens **puede** fallar: se altera `tokens.css` a propósito, se
afirma el código **1** y se restaura.

**Ficheros**
- `.github/workflows/ci.yml` — nuevo; un trabajo en `ubuntu-latest` con `astral-sh/setup-uv`
- `README.md` — edita: fuera `pip install -e .` y `streamlit run ui/app.py`; dentro el alta de cuenta, los reindexados y la copia

**Aceptación**

1. **WHEN** the full acceptance gate is run in order **THE SYSTEM SHALL** exit `0` at every line.
2. **WHEN** the collectstatic command runs **THE SYSTEM SHALL** exit `0` and populate the static root.
3. **WHEN** the generated tokens file is deliberately corrupted **THE SYSTEM SHALL** make the token sync check exit `1` specifically, proving the sync gate can actually fail.
4. **WHEN** `README.md` is read **THE SYSTEM SHALL** contain no reference to streamlit and no editable pip install, and SHALL document creating the first account, both reindex commands and the backup command.
5. **WHEN** the CI workflow is read **THE SYSTEM SHALL** contain every command of the automated acceptance gate, including the evaluation regression gate.
6. **WHEN** this task's checkpoint has run **THE SYSTEM SHALL** list 27 tags matching the step prefix, one per build step.

**Verify**

```powershell
uv run python manage.py collectstatic --noinput; if ($LASTEXITCODE -ne 0) { throw 'collectstatic falla' }
Copy-Item 'static/css/tokens.css' 'static/css/tokens.css.bak'; Add-Content 'static/css/tokens.css' '/* alteracion deliberada */'; uv run python -m scripts.build_tokens --check; $c = $LASTEXITCODE; Move-Item 'static/css/tokens.css.bak' 'static/css/tokens.css' -Force; if ($c -ne 1) { throw "con tokens.css alterado se esperaba codigo 1, obtenido $c" }
uv run python -m scripts.build_tokens --check; if ($LASTEXITCODE -ne 0) { throw 'tokens.css no ha quedado restaurado' }
if ((Get-Content -Raw 'README.md') -match 'streamlit') { throw 'el README sigue hablando de streamlit' }
if ((Get-Content -Raw 'README.md') -match 'pip install -e') { throw 'el README sigue mandando instalar el paquete' }
if (-not (Test-Path '.github/workflows/ci.yml')) { throw 'falta el flujo de integracion continua' }
uv run ruff check .; if ($LASTEXITCODE -ne 0) { throw 'ruff falla' }
uv run ruff format --check .; if ($LASTEXITCODE -ne 0) { throw 'el formato no esta aplicado' }
uv run mypy .; if ($LASTEXITCODE -ne 0) { throw 'mypy falla' }
uv run pytest; if ($LASTEXITCODE -ne 0) { throw 'la suite completa falla' }
```

**Checkpoint**

```powershell
git add -A; git commit -m "E4-T6: integracion continua, estaticos y cierre de la migracion"
git tag step-27-cierre
$etiquetas = (git tag -l 'step-*' | Measure-Object -Line).Lines; if ($etiquetas -ne 27) { throw "hay $etiquetas etiquetas de paso, se esperaban 27" }
git ls-files --error-unmatch .github/workflows/ci.yml; if ($LASTEXITCODE -ne 0) { throw 'el flujo de CI no ha quedado versionado' }
```

---

## Aceptación de la epic

La epic está hecha cuando todas sus tareas están en `done` **y**:

1. **WHEN** the full acceptance gate runs from the project root **THE SYSTEM SHALL** exit `0` on every command, with the rescued suite reporting exactly 180 passed and 27 step tags present in version control.
2. **WHEN** a backup is taken and restored into a clean directory **THE SYSTEM SHALL** match the row count of each of the eight tables, and a mismatch SHALL exit `1`.
3. **WHEN** the evaluation harness runs against the baseline **THE SYSTEM SHALL** exit `0` when the hit rate holds and `1` when it falls, never merely non-zero.
4. **WHEN** any authenticated page is rendered **THE SYSTEM SHALL** carry the privacy notice stating that administrators can access any user's cases.
5. **WHEN** the deploy check runs against the production settings **THE SYSTEM SHALL** exit `0` with zero issues, while the local settings keep the secure cookie flags off.

```powershell
uv run ruff check .; if ($LASTEXITCODE -ne 0) { throw 'lint' }
uv run ruff format --check .; if ($LASTEXITCODE -ne 0) { throw 'formato' }
uv run mypy .; if ($LASTEXITCODE -ne 0) { throw 'tipos' }
uv run pytest; if ($LASTEXITCODE -ne 0) { throw 'suite completa' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'red de seguridad' }
uv run python manage.py evaluar --contra-linea-base; if ($LASTEXITCODE -ne 0) { throw "regresion en la tasa de acierto (codigo $LASTEXITCODE)" }
uv run python manage.py collectstatic --noinput; if ($LASTEXITCODE -ne 0) { throw 'collectstatic' }
$etiquetas = (git tag -l 'step-*' | Measure-Object -Line).Lines; if ($etiquetas -ne 27) { throw "hay $etiquetas etiquetas, se esperaban 27" }
```

## Trampas

- **Copiar `db.sqlite3` con `Copy-Item` en vez de usar la API de copia en línea.** Produce un fichero
  corrupto **sin avisar**, y el fallo aparece el día que hace falta restaurar.
- **Dar la copia por buena porque el fichero existe.** Una copia sin restaurar no es una copia. El
  criterio es el recuento de filas de las ocho tablas.
- **Escribir la puerta de regresión como «sale distinto de cero».** Un error de uso también sale
  distinto de cero: la puerta pasaría en vacío y seguiría pasando después de romperse.
- **Meter el conjunto dorado solo en la base de datos.** Deja de revisarse en *pull requests* y deja de
  ser dorado. Vive en `evaluacion/casos/*.json`.
- **Olvidar `proposito="evaluacion"` en las llamadas del arnés.** Una pasada consumiría el tope
  mensual de un usuario real.
- **Activar `SESSION_COOKIE_SECURE` en local.** Sin TLS, la sesión deja de funcionar y parece un fallo
  de autenticación.
- **Poner el aviso de privacidad solo en el pie.** El momento en que importa es cuando el usuario está
  a punto de escribir el dato, y ese momento es el formulario.
- **Meter una clave de API en los secretos de CI.** CI corre **sin** clave a propósito: es lo que
  mantiene viva la ruta de degradación.

## Antes de seguir

- [ ] Las seis tareas están en `done` en `tasks.json`; ninguna en `in_progress`.
- [ ] Pasaron **todos** los comandos `verify` de cada tarea, no solo el primero.
- [ ] No se editó ningún comando `verify`, y no se saltó ninguno porque un fichero no existiera.
- [ ] Las seis etiquetas están en git: `step-22-contrastados` … `step-27-cierre`, y el total de
      etiquetas `step-*` es **27**.
- [ ] El gate completo pasa limpio desde la raíz del proyecto, con el bundle presente.
- [ ] No se modificó ningún fichero fuera del subárbol.
- [ ] `.env.example` no necesitaba variables nuevas: esta epic no añade ninguna.
- [ ] Un commit por tarea, cada uno prefijado con su id, cada uno seguido de su etiqueta.
- [ ] Los gates manuales del blueprint —pase con teclado, lector de pantalla, zoom al 200%, vuelta
      atrás ensayada— quedan pendientes de comprobar una vez antes de dar el proyecto por lanzado.
      No son gates de construcción y no bloquean esta epic.
