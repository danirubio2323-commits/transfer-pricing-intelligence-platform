# Epic 03: Gasto, IA y contenido

> Después de esta epic los casos se buscan y se listan, el gasto del modelo está frenado por un tope
> mensual comprobado **antes** de cada llamada, la explicación de IA está conectada y degrada en
> silencio por cinco caminos distintos, y el corpus jurídico está indexado, publicado y enlazado desde
> cada fuente citada, con el material de estudio como entidad aparte.

| | |
|---|---|
| **Epic id** | `03-gasto-ia-y-contenido` |
| **Tareas** | `E3-T1` … `E3-T7` |
| **Depende de** | `01-cimientos-y-cuentas`, `02-analisis-y-presentacion` |
| **Desbloquea** | `04-precedentes-evidencia-y-cierre` |
| **Paralela con** | ninguna. La 04 necesita el listado, el registro de llamadas y el corpus indexado |

No necesitas ningún otro fichero para completar esta epic. Todo lo de abajo está repetido aquí a
propósito.

---

## Pila

Django 5.2 · Python 3.12 · plantillas de Django · CSS plano con variables generadas · SQLite · ORM de
Django para la persistencia y pydantic para el dominio · SDK de `anthropic` · `python-frontmatter` y
`Markdown` para el corpus · ejecución local en Windows 10 con PowerShell.
Gestor de paquetes: `uv`. Python y dependencias fijados en `pyproject.toml` y resueltos en `uv.lock`
— **léelos, nunca adivines una versión**.

| Tarea | Comando |
|---|---|
| Servidor de desarrollo | `uv run python manage.py runserver` |
| Comprobar el proyecto | `uv run python manage.py check` |
| Tipos | `uv run mypy .` |
| Lint | `uv run ruff check .` |
| Pruebas (un fichero) | `uv run pytest tests/web/test_cuota.py` |
| **Red de seguridad** | `uv run pytest tests/domain tests/ai tests/report` |
| Migraciones | `uv run python manage.py makemigrations <app>` · `uv run python manage.py migrate` |
| Reindexar corpus | `uv run python manage.py reindexar_corpus` |

**Gate:** `uv run ruff check . && uv run mypy . && uv run pytest` pasa antes de dar por hecha
cualquier tarea de esta epic.

**Ninguna prueba de esta epic toca la red.** La capa de IA se prueba siempre con dobles inyectados por
parámetro, y en E3-T2 el doble es más exigente todavía: **lanza si alguien lo llama**. Si te ves
necesitando una clave de API real para pasar un `verify`, la prueba está mal escrita.

## Subárbol de directorios

Solo lo que esta epic toca:

```
apps/comun/
  consultas.py                  # EXISTE de la epic 01 — se AMPLÍA en E3-T1
apps/analisis/
  views.py                      # EXISTE — se AMPLÍA: lista, borrar
  urls.py                       # EXISTE — se AMPLÍA
  services.py                   # EXISTE — se AMPLÍA en E3-T3: cuota + IA + registro
apps/ia/                        # NUEVO — el freno de gasto y el registro contable
  __init__.py  apps.py          # NUEVO
  models.py                     # NUEVO — LlamadaLLM
  cuota.py                      # NUEVO — comprobar_cuota(), gasto_del_mes(), coste_de()
  registro.py                   # NUEVO — registrar_llamada(), único escritor
  admin.py                      # NUEVO — LlamadaLLM en solo lectura
  migrations/__init__.py        # NUEVO
apps/corpus/                    # NUEVO — índice citable del corpus
  __init__.py  apps.py          # NUEVO
  models.py                     # NUEVO — Ficha
  indexador.py                  # NUEVO — lee los .md, valida que no se sale del corpus
  views.py  urls.py             # NUEVO
  admin.py                      # NUEVO — Ficha en SOLO LECTURA
  management/commands/reindexar_corpus.py   # NUEVO
  migrations/__init__.py        # NUEVO
apps/estudio/                   # NUEVO — material didáctico, NUNCA citable
  __init__.py  apps.py          # NUEVO
  models.py                     # NUEVO — UnidadEstudio
  views.py  urls.py  admin.py   # NUEVO — admin EDITABLE, al contrario que Ficha
  migrations/__init__.py        # NUEVO
templates/
  analisis/lista.html           # NUEVO — búsqueda, filtro, orden, DOS vacíos, paginación
  analisis/detalle.html         # EXISTE — se AMPLÍA: sección de IA y enlaces a fichas
  corpus/indice.html            # NUEVO
  corpus/ficha.html             # NUEVO
  estudio/indice.html           # NUEVO
  estudio/unidad.html           # NUEVO
ai/claude_client.py             # EXISTE de la epic 02 — solo se USA
documentation/tax-research/     # EXISTE — 9 fichas .md + README.md sin frontmatter.
                                # E3-T4 completa su frontmatter; el CUERPO no se toca nunca
tests/web/
  test_listado.py               # NUEVO
  test_cuota.py                 # NUEVO
  test_ia_degradacion.py        # NUEVO
  test_corpus_indice.py         # NUEVO
  test_corpus.py                # NUEVO
  test_estudio.py               # NUEVO
  test_aislamiento.py           # EXISTE — se AMPLÍA en E3-T1 con el listado
```

Todo lo que quede fuera de este subárbol está fuera de alcance. Si una tarea parece exigir editar un
fichero que no está aquí, para y reporta.

## Modelo de datos que se toca aquí

| Entidad | Tabla | Campos | Notas |
|---|---|---|---|
| `Caso` | `casos` | Lee todos; escribe `deleted_at` al borrar en suave | Creado en la epic 01. **No se le añade ni un campo** |
| `LlamadaLLM` | `llamadas_llm` | `usuario` (FK `PROTECT`, indexada), `caso` (FK `SET_NULL`), `creada_el` (indexada), `proposito`, `modelo`, `prompt_version`, los cuatro contadores de tokens, `coste_eur`, `latencia_ms`, `razon_finalizacion`, `error`, `intento` | Índice compuesto `(usuario, creada_el)`: la comprobación de cuota lo consulta **antes de cada llamada** y es la consulta más sensible a la latencia del sistema |
| `Ficha` | `fichas` | `id` (slug, PK), `titulo`, `jurisdiccion` (indexada), `clase`, `rango_normativo`, `cita`, `pinpoint`, `tipo_localizador`, `localizador`, `url_oficial`, `confianza_verificacion`, `verificada_el`, `ruta_fichero` (**unique**), `hash_fichero`, `actualizada_el` | **Índice reconstruible.** El `.md` en disco es la fuente de verdad. `id` es el mismo identificador que emite `tp_domain/sources.py`, para que una fuente citada resuelva sin tabla de traducción |
| `UnidadEstudio` | `unidades_estudio` | `slug` (unique), `titulo`, `resumen`, `cuerpo`, `orden`, `publicada`, `fichas` (M2M a `Ficha`), marcas de tiempo | Índice compuesto `(publicada, orden)`. **Nunca es fuente citable** |

`Ficha` y `UnidadEstudio` **no llevan `usuario_id`, y no es un olvido**: no son datos de usuario. La
ficha es corpus compartido y la unidad es material publicado. La guarda de propietario no se les
aplica porque no hay nada que aislar.

`proposito` en `LlamadaLLM` distingue `explicacion` de `evaluacion`. Sin ese campo, el coste del arnés
de la epic 04 y el del producto se sumarían en el mismo número, y una pasada de evaluación consumiría
el tope mensual de un usuario real.

## Contratos

**Consumidos** — ya existen, no los reconstruyas:

| De | Interfaz | Garantía |
|---|---|---|
| `01` | `apps.comun.guardas.caso_del_usuario(usuario, pk)` | El `Caso` vivo de ese usuario, o `Http404` |
| `01` | `apps.comun.consultas.casos_de(usuario)` | `QuerySet` ya filtrado por propietario |
| `01` | `apps.cuentas.models.Usuario` | Lleva `tope_gasto_mensual_eur`, por defecto `5.00` |
| `02` | `apps.analisis.services.crear_caso(usuario, transaction, titulo)` | Crea el caso ejecutando el motor. **Esta epic lo amplía**, no lo reescribe |
| `02` | `ai.claude_client.explain_analysis(result, client=None, model=None)` | **No lanza nunca.** Devuelve la explicación validada o `None`. Exige `model`: sin él, se desactiva sin llamar a la red |
| `02` | `ai.claude_client.request_explanation` | Devuelve además el `usage` y el `stop_reason` **reportados por el proveedor**, sin interpretar |
| `02` | `templates/base.html` | Bloque `contenido` y pie con `role="contentinfo"` |
| Rescatado | `tp_domain.sources.SOURCE_REGISTRY` | Registro cerrado de 5 fuentes, con `research_note` apuntando a una ficha |

**Producidos** — la epic 04 depende de estas firmas exactas:

| Export | Firma | Lo usa |
|---|---|---|
| `apps.ia.cuota` → `comprobar_cuota` | `comprobar_cuota(usuario)`, levanta `CuotaSuperada` | `04` (el arnés respeta el mismo freno) |
| `apps.ia.cuota` → `coste_de` | `coste_de(usage, modelo) -> Decimal`, `0` si no hay tarifas | `04` |
| `apps.ia.registro` → `registrar_llamada` | Único escritor de `LlamadaLLM`; acepta `proposito` | `04` (`proposito="evaluacion"`) |
| `apps.ia.models` → `LlamadaLLM` | Tabla `llamadas_llm` | `04` (copia de seguridad, coste del arnés) |
| `apps.corpus.models` → `Ficha` | Tabla `fichas`, `id` compartido con el registro de fuentes | `04` (copia de seguridad) |
| `apps.estudio.models` → `UnidadEstudio` | Tabla `unidades_estudio` | `04` (copia de seguridad) |
| `templates/analisis/lista.html` | Listado paginado con tope de página en servidor | `04` (accesibilidad) |

## Convenciones que muerden en esta área

- **El tope de gasto se construye ANTES de conectar la capa de IA.** E3-T2 va antes que E3-T3 y el
  orden no es negociable: un freno que se instala después de que algo ya rueda es un freno que nunca
  se ha probado en el camino que importa.
- **`comprobar_cuota()` se llama antes de construir el cliente, nunca dentro de él.**
- **Los tokens los reporta el proveedor.** Nada de `tiktoken`, `count_tokens` ni contar palabras: un
  recuento propio diverge del que se factura y el tope acabaría vigilando un número que no se paga.
- **Superar el tope desactiva la sección de IA; nunca bloquea el producto.** El análisis se calcula,
  el caso se persiste y el informe sale completo declarando la ausencia. Es la misma ruta de
  degradación que la falta de clave.
- **`Ficha` es un índice reconstruible y su panel es de SOLO LECTURA.** Una edición allí se perdería
  en el siguiente reindexado, y una tabla que miente es peor que una tabla que no existe.
- **`UnidadEstudio` es editable desde el panel y NUNCA citable.** La ficha tiene rango normativo; la
  unidad es material de aprendizaje. Fusionarlas acabaría con un informe citando material de estudio
  como si fuera Derecho.
- **El tamaño de página lo decide el servidor.** `?por_pagina=` se acepta y se recorta a 100.
- **El borrado es suave.** Ninguna vista llama a `.delete()` sobre un `Caso`.
- **`ai/` sigue sin importar Django.** `apps/analisis/services.py` es el único puente.

Reglas completas del proyecto: `CLAUDE.md`. Reglas de área: `.claude/rules/capa-web.md` y
`.claude/rules/gasto-y-ia.md`.

---

## Tareas

En el mismo orden que `tasks.json`.

### `E3-T1` — Listado de casos: búsqueda, filtro, orden, vacíos y paginación

**Depende de:** `E2-T5`, `E2-T7` · **Prioridad:** p0

Un caso que se guarda pero no se encuentra es un caso perdido. Amplía `casos_de()` para aceptar texto,
jurisdicción y orden, **filtrando siempre por `usuario` primero**: el propietario no es un parámetro
opcional y no hay forma de llamarla sin él. El tamaño de página lo decide el servidor. Y hay **dos
estados vacíos distintos**, que no se pueden confundir: «todavía no has analizado ninguna operación»
frente a «ningún caso coincide con esta búsqueda» — un filtro mal escrito no debe parecer una base de
datos vacía.

**Ficheros**
- `apps/comun/consultas.py` — edita: `casos_de(usuario, *, texto=None, jurisdiccion=None, orden=None)`
- `apps/analisis/views.py` — edita: `lista` (GET `/casos/`) con `Paginator`, y `borrar` (POST `/casos/<uuid>/borrar/`) que pone `deleted_at`
- `apps/analisis/urls.py` — edita: las dos rutas
- `templates/analisis/lista.html` — nuevo
- `tests/web/test_listado.py` — nuevo, y edita `tests/web/test_aislamiento.py` con el caso cruzado del listado

**Aceptación**

1. **WHEN** a user with zero cases opens the case list **THE SYSTEM SHALL** respond `200` with the first-run empty state, and SHALL NOT show the no-matches text.
2. **WHEN** a search matches no case **THE SYSTEM SHALL** respond `200` with the no-matches empty state and a link that clears the filter.
3. **WHEN** user A lists cases and user B owns cases too **THE SYSTEM SHALL** return only A's rows, in every combination of search, filter and ordering.
4. **WHEN** a page size of 100000 is requested **THE SYSTEM SHALL** return at most 100 rows, because the server caps the page size regardless of what the client asks for.
5. **WHEN** a non-numeric page size or a page number beyond the last is requested **THE SYSTEM SHALL** respond `200` with the default page size and the last valid page, never `500`.
6. **WHEN** the owner posts a delete **THE SYSTEM SHALL** set `deleted_at`, keep the row in the database, and make the case return `404` afterwards.

**Verify**

```powershell
uv run pytest tests/web/test_listado.py tests/web/test_aislamiento.py -q; if ($LASTEXITCODE -ne 0) { throw 'el listado o su aislamiento fallan' }
$borradosDuros = Select-String -Path (Get-ChildItem 'apps/analisis' -Recurse -Filter '*.py' -File).FullName -Pattern '\.delete\(\)' -ErrorAction SilentlyContinue; if ($borradosDuros) { throw 'hay un borrado duro en apps/analisis' }
uv run pytest tests/web -q; if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A; git commit -m "E3-T1: listado de casos con busqueda, filtro, orden, vacios y paginacion con tope"
git tag step-15-listado
```

### `E3-T2` — `LlamadaLLM` y tope de gasto comprobado antes de llamar

**Depende de:** `E1-T6`, `E2-T1` · **Prioridad:** p0

**Esta tarea va antes de E3-T3 y el orden no es negociable.** Aquí se construye el freno, con su
prueba, y solo después se conecta el motor que hay que frenar. La prueba central usa **un doble de
cliente que lanza `AssertionError` si alguien lo llama**: si la cuota funciona, ese doble no se toca
nunca, y esa es la única forma de comprobar «antes de cualquier llamada al proveedor» en un medio
donde la propiedad es observable. `coste_de()` calcula a partir del uso **reportado**, no cuenta
tokens; con las tarifas sin fijar devuelve `0` en vez de fallar, porque un sistema sin tarifas
registra uso pero no puede imputar gasto, y decirlo con un cero es más honesto que inventar un precio.

**Ficheros**
- `apps/ia/__init__.py`, `apps/ia/apps.py` — nuevos; `IaConfig`, `label = "ia"`
- `apps/ia/models.py` — nuevo; `LlamadaLLM`, `db_table = "llamadas_llm"`
- `apps/ia/cuota.py` — nuevo; `CuotaSuperada`, `gasto_del_mes()`, `comprobar_cuota()`, `coste_de()`
- `apps/ia/registro.py` y `apps/ia/admin.py` — nuevos; único escritor, y panel en solo lectura
- `config/settings/base.py` — edita: `"apps.ia"` en `INSTALLED_APPS`
- `tests/web/test_cuota.py` — nuevo

**Aceptación**

1. **WHEN** a user whose spend for the current month has reached their monthly cap triggers a request that would call the model **THE SYSTEM SHALL** reject it before any call to the provider, with zero new `LlamadaLLM` rows and zero recorded spend.
2. **WHEN** that rejection happens **THE SYSTEM SHALL** still complete the analysis and persist the case, because the cap disables the AI section and never blocks the product.
3. **WHEN** a call completes **THE SYSTEM SHALL** persist one `LlamadaLLM` row whose four token counters come from the provider's reported usage, never from a local count.
4. **WHEN** `coste_de` is given a usage object **THE SYSTEM SHALL** compute the cost from the configured rates, and with rates unset SHALL yield `0` rather than raising.
5. **WHEN** a user is one cent below the cap **THE SYSTEM SHALL** allow the call, and when exactly at the cap **THE SYSTEM SHALL** reject it, so the boundary is inclusive on the rejection side.
6. **WHEN** spend is summed **THE SYSTEM SHALL** count only rows of the current calendar month and only those belonging to that user.

**Verify**

```powershell
uv run python manage.py makemigrations ia; if ($LASTEXITCODE -ne 0) { throw 'makemigrations falla' }
uv run python manage.py makemigrations --check --dry-run; if ($LASTEXITCODE -ne 0) { throw "quedan cambios de modelo sin migrar (codigo $LASTEXITCODE)" }
uv run python manage.py migrate; if ($LASTEXITCODE -ne 0) { throw 'migrate falla' }
uv run pytest tests/web/test_cuota.py -q; if ($LASTEXITCODE -ne 0) { throw 'el tope de gasto falla' }
$conteoPropio = Select-String -Path (Get-ChildItem 'apps/ia' -Recurse -Filter '*.py' -File).FullName -Pattern 'count_tokens|tiktoken' -ErrorAction SilentlyContinue; if ($conteoPropio) { throw 'apps/ia estima tokens por su cuenta; deben venir del proveedor' }
uv run pytest tests/web -q; if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A; git commit -m "E3-T2: LlamadaLLM y tope de gasto comprobado antes de llamar al proveedor"
git tag step-16-gasto
git ls-files --error-unmatch apps/ia/models.py apps/ia/cuota.py; if ($LASTEXITCODE -ne 0) { throw 'el freno de gasto no ha quedado versionado' }
```

### `E3-T3` — Capa de IA en la vista: degradación silenciosa y llamada registrada

**Depende de:** `E3-T2`, `E2-T7` · **Prioridad:** p0

Aquí el principio rector deja de ser una frase y pasa a ser código: **el motor calcula; el modelo
explica, fundamenta y puede sugerir, pero nunca decide y nunca escribe un número.** Cuando
`services.py` llama al modelo, el `AnalysisResult` ya está calculado entero; la explicación se añade
encima y no puede modificar nada. El orden dentro de `crear_caso` importa y se comprueba: **primero la
cuota, después el cliente.** `services.py` es el único punto del proyecto que conoce a la vez Django y
la capa de IA.

**Ficheros**
- `apps/analisis/services.py` — edita: comprobar cuota, leer `settings.ANTHROPIC_API_KEY` y `settings.ANTHROPIC_MODEL`, llamar a `explain_analysis`, registrar la `LlamadaLLM` con `proposito="explicacion"`, y emitir el evento de `structlog`
- `templates/analisis/detalle.html` — edita: la sección de IA declara su ausencia; cuando la hay, muestra modelo y versión de prompt
- `tests/web/test_ia_degradacion.py` — nuevo; las cinco rutas, todas con dobles

**Aceptación**

1. **WHEN** the API key is unset **THE SYSTEM SHALL** complete the analysis, respond `302`, persist the case with no AI explanation and make no network call.
2. **WHEN** the API key is set but the model id is unset **THE SYSTEM SHALL** behave identically and SHALL make no network call, because the model is never discovered at runtime.
3. **WHEN** the user's monthly cap is already reached **THE SYSTEM SHALL** behave identically, SHALL make no network call and SHALL write no `LlamadaLLM` row.
4. **WHEN** the injected client raises **THE SYSTEM SHALL** still respond `302`, persist the case without an explanation, and record one `LlamadaLLM` row whose error names the failure category and whose cost is zero.
5. **WHEN** the model returns a draft citing a source id the engine did not emit **THE SYSTEM SHALL** persist the case without that explanation, because `AnalysisResult` cannot be constructed with it.
6. **WHEN** a valid draft is returned **THE SYSTEM SHALL** persist the case with its AI explanation, record one `LlamadaLLM` with purpose `explicacion` and the provider's reported token counts, and render the explanation with its model id and prompt version.

**Verify**

```powershell
uv run pytest tests/web/test_ia_degradacion.py -q; if ($LASTEXITCODE -ne 0) { throw 'la degradacion de la capa de IA falla' }
$puentes = Select-String -Path (Get-ChildItem 'ai' -Recurse -Filter '*.py' -File).FullName -Pattern '(?m)^\s*(from|import)\s+django' -ErrorAction SilentlyContinue; if ($puentes) { throw 'ai/ ha empezado a importar Django' }
if ((Get-Content -Raw 'apps/analisis/views.py') -match 'claude_client') { throw 'la vista llama a la capa de IA; debe pasar por services.py' }
$src = Get-Content -Raw 'apps/analisis/services.py'; if ($src.IndexOf('comprobar_cuota') -lt 0) { throw 'services.py no comprueba la cuota' }
$src = Get-Content -Raw 'apps/analisis/services.py'; if ($src.IndexOf('comprobar_cuota') -gt $src.IndexOf('explain_analysis')) { throw 'la cuota se comprueba DESPUES de llamar al modelo' }
uv run pytest tests/web -q; if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A; git commit -m "E3-T3: explicacion de IA aditiva, con degradacion silenciosa y llamada registrada"
git tag step-17-ia
```

### `E3-T4` — Completar el frontmatter de las 9 fichas del corpus

**Depende de:** `E1-T4` · **Prioridad:** p1

**Esta tarea es contenido, no código, y va antes del indexador por un motivo concreto:** el corpus real
todavía no cumple el contrato que `E3-T5` va a exigir. Sus fichas llevan hoy `titulo`,
`fecha_creacion`, `origen`, `fuente_primaria`, `tipo`, `usar_en` y `enlaces` —y ni siquiera las siete
en todas—, mientras que `Ficha` necesita además rango normativo, clase, localizador tipado y fecha de
verificación. Indexar antes haría fallar `E3-T5` contra el repositorio del propio usuario.

**Los siete campos actuales se conservan**: son suyos y sirven a su forma de trabajar en Obsidian. Dos
ya alimentan el índice — `titulo` → `Ficha.titulo` y `fuente_primaria` → `Ficha.cita`.

**La jurisdicción no se escribe: se deduce de la ruta.** `jurisdictions/spain/` → `ES`,
`jurisdictions/germany/` → `DE`, `jurisdictions/eu/` → `EU`, `frameworks/` → `OECD`. `processes/` no
tiene valor por defecto y la ficha debe declararlo en su frontmatter. Un campo explícito siempre
sobrescribe a la ruta.

**`README.md` queda fuera del barrido, y el criterio es la ausencia de frontmatter, no el nombre**: un
fichero sin bloque YAML de cabecera no es una ficha y se omite en silencio. Así, añadir un segundo
índice o un borrador no obliga a tocar el indexador.

Valores por ficha. El vocabulario de `clase`, `tipo_localizador` y `confianza_verificacion` es el que
ya existe en `tp_domain/sources.py`; no se inventa ninguno.

| # | Ficha | `clase` | `rango_normativo` | `tipo_localizador` |
|---|---|---|---|---|
| 1 | `jurisdictions/spain/art18-lis-operaciones-vinculadas.md` | `legislation` | Ley ordinaria | `boe_id` |
| 2 | `jurisdictions/spain/ris-documentacion-masterfile-localfile.md` | `legislation` | Reglamento | `boe_id` |
| 3 | `jurisdictions/germany/astg-rango-intercuartilico-ajuste-mediana.md` | `legislation` | Ley federal alemana | `url` |
| 4 | `jurisdictions/eu/directiva-intereses-canones-2003-49.md` | `legislation` | Directiva de la UE | `url` |
| 5 | `jurisdictions/eu/propuesta-directiva-tp-2023-retirada.md` | `legislation` | Propuesta retirada | `url` |
| 6 | `frameworks/ocde-directrices-2022-marcos-riesgo-dempe-servicios.md` | `guidelines` | Directrices OCDE | `offline` |
| 7 | `frameworks/criterios-seleccion-comparables.md` | `guidelines` | Directrices OCDE | `offline` |
| 8 | `frameworks/safe-harbours-y-htvi.md` | `guidelines` | Directrices OCDE | `offline` |
| 9 | `processes/doctrina-teac-bilateralidad-y-servicios.md` | `case_law` | Doctrina administrativa | `url` |

**Ninguna regla admite inventar un identificador.** Las fichas 1, 3 y 6 ya tienen entrada en el
registro cerrado (`es-lis-art18-4`, `de-astg-1-3a`, `oecd-tpg-2022-cap3`): se copia su `locator`
literal. Las otras seis toman el identificador que su propio cuerpo ya cita, y si no hay uno público
resoluble, su `tipo_localizador` es `offline`. `confianza_verificacion` es
`primary_source_verified` solo si la ficha se leyó contra su texto oficial, y `directed_reading` en
cualquier otro caso: se marca lo que de verdad pasó.

Cuatro fichas no tienen hoy `fuente_primaria` y dos no tienen `tipo`. Se completan también.

**Ficheros**
- `documentation/tax-research/jurisdictions/**/*.md` — edita: **solo el frontmatter**; el cuerpo no se toca
- `documentation/tax-research/frameworks/*.md` — edita: solo el frontmatter
- `documentation/tax-research/processes/*.md` — edita: solo el frontmatter, incluida `jurisdiccion`
- `documentation/tax-research/README.md` — **no se toca**: es el índice y se excluye por no tener frontmatter

**Aceptación**

1. **WHEN** every markdown file under the research directory that carries YAML frontmatter is read **THE SYSTEM SHALL** find exactly 9 of them, each with `titulo`, `fuente_primaria`, `rango_normativo`, `clase`, `tipo_localizador`, `localizador`, `verificada_el` and `confianza_verificacion` present and non-empty.
2. **WHEN** the corpus README is read **THE SYSTEM SHALL** find no YAML frontmatter, so the exclusion criterion is a property of the file and not a hardcoded name.
3. **WHEN** each ficha's `clase`, `tipo_localizador` and `confianza_verificacion` are read **THE SYSTEM SHALL** find every value inside the vocabulary `tp_domain/sources.py` already defines.
4. **WHEN** the three fichas that already have an entry in the closed source registry are read **THE SYSTEM SHALL** find their `localizador` identical, character for character, to the `locator` of that entry.
5. **WHEN** the seven pre-existing frontmatter keys are read **THE SYSTEM SHALL** find them unchanged, because this task only adds keys and removes none.

**Verify**

```powershell
uv run python -c "import frontmatter, pathlib; req={'titulo','fuente_primaria','rango_normativo','clase','tipo_localizador','localizador','verificada_el','confianza_verificacion'}; todos=sorted(pathlib.Path('documentation/tax-research').rglob('*.md')); fichas=[p for p in todos if frontmatter.load(p).metadata]; assert len(fichas)==9, [str(x) for x in fichas]; malas={str(p): sorted(req - set(frontmatter.load(p).metadata)) for p in fichas if req - set(frontmatter.load(p).metadata)}; assert not malas, malas; print('9 fichas completas')"; if ($LASTEXITCODE -ne 0) { throw 'alguna ficha no cumple el contrato del indice' }
uv run python -c "import frontmatter, pathlib; p=pathlib.Path('documentation/tax-research/README.md'); assert not frontmatter.load(p).metadata, 'README.md tiene frontmatter y dejaria de excluirse'; print('README excluido por ausencia de frontmatter')"; if ($LASTEXITCODE -ne 0) { throw 'el criterio de exclusion del README ya no se cumple' }
uv run python -c "import frontmatter, pathlib; from tp_domain.models import SourceKind, LocatorType, VerificationConfidence; ok_c={e.value for e in SourceKind}; ok_l={e.value for e in LocatorType}; ok_v={e.value for e in VerificationConfidence}; malas=[str(p) for p in pathlib.Path('documentation/tax-research').rglob('*.md') if frontmatter.load(p).metadata and not (frontmatter.load(p)['clase'] in ok_c and frontmatter.load(p)['tipo_localizador'] in ok_l and frontmatter.load(p)['confianza_verificacion'] in ok_v)]; assert not malas, malas; print('vocabulario OK')"; if ($LASTEXITCODE -ne 0) { throw 'alguna ficha usa un valor fuera del vocabulario del dominio' }
uv run python -c "import frontmatter, pathlib; from tp_domain.sources import SOURCE_REGISTRY; pares={'jurisdictions/spain/art18-lis-operaciones-vinculadas.md':'es-lis-art18-4','jurisdictions/germany/astg-rango-intercuartilico-ajuste-mediana.md':'de-astg-1-3a','frameworks/ocde-directrices-2022-marcos-riesgo-dempe-servicios.md':'oecd-tpg-2022-cap3'}; malas={r: (frontmatter.load(pathlib.Path('documentation/tax-research')/r)['localizador'], SOURCE_REGISTRY[i].locator) for r, i in pares.items() if frontmatter.load(pathlib.Path('documentation/tax-research')/r)['localizador'] != SOURCE_REGISTRY[i].locator}; assert not malas, malas; print('localizadores alineados con el registro')"; if ($LASTEXITCODE -ne 0) { throw 'un localizador de ficha no coincide con el del registro cerrado' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A; git commit -m "E3-T4: frontmatter completo en las 9 fichas del corpus"
git tag step-18-frontmatter
git ls-files --error-unmatch documentation/tax-research/jurisdictions/spain/art18-lis-operaciones-vinculadas.md; if ($LASTEXITCODE -ne 0) { throw 'las fichas no han quedado versionadas' }
```

### `E3-T5` — `Ficha`: índice citable del corpus, reconstruible desde los `.md`

**Depende de:** `E1-T4`, `E3-T4` · **Prioridad:** p1

Las **9 fichas** de `documentation/tax-research/` —más un `README.md` sin frontmatter, que se
excluye— las **escribe el usuario en Obsidian**, y `E3-T4` acaba de completarlas. Esta tarea las
convierte en un índice consultable **sin dejar de ser ficheros**: el `.md` en disco es la fuente
de verdad y la tabla se reconstruye desde él. Por eso el panel muestra `Ficha` en solo lectura. El
indexador **omite todo fichero sin frontmatter** —así queda fuera el `README.md`—, deduce la
jurisdicción de la ruta, y resuelve la ruta absoluta comprobando que sigue dentro del corpus:
cualquier `..`, ruta absoluta o enlace que se salga se rechaza sin leer nada. El comando es **idempotente**: ejecutarlo dos
veces deja exactamente el mismo estado.

**Ficheros**
- `apps/corpus/__init__.py`, `apps/corpus/apps.py` — nuevos; `CorpusConfig`, `label = "corpus"`
- `apps/corpus/models.py` — nuevo; `Ficha`, `db_table = "fichas"`
- `apps/corpus/indexador.py` — nuevo; recorre los `.md`, lee el frontmatter, calcula el SHA-256, valida la ruta
- `apps/corpus/management/commands/reindexar_corpus.py` y `apps/corpus/admin.py` — nuevos; el segundo, en solo lectura
- `config/settings/base.py` — edita: `"apps.corpus"` en `INSTALLED_APPS`; y `tests/web/test_corpus_indice.py` — nuevo

**Aceptación**

1. **WHEN** the corpus reindex command runs **THE SYSTEM SHALL** exit 0 and leave one `Ficha` row per markdown file under the research directory that carries YAML frontmatter, which is 9, because the README has none and is skipped.
2. **WHEN** the command runs twice in a row **THE SYSTEM SHALL** leave the identical set of rows, with identical file hashes, because it is idempotent.
3. **WHEN** a markdown file changes on disk and the command is re-run **THE SYSTEM SHALL** update that row's file hash, so drift between disk and index is detectable.
4. **WHEN** a ficha's frontmatter is missing a required key **THE SYSTEM SHALL** fail loudly naming the file and the key, and SHALL NOT leave the table half-rebuilt.
5. **WHEN** `Ficha` is opened in the admin **THE SYSTEM SHALL** present every field read-only, because the file on disk is the source of truth.
6. **WHEN** a source id emitted by the engine is looked up in `Ficha` **THE SYSTEM SHALL** resolve without a translation table, because both use the same identifier.

**Verify**

```powershell
uv run python manage.py makemigrations corpus; if ($LASTEXITCODE -ne 0) { throw 'makemigrations falla' }
uv run python manage.py migrate; if ($LASTEXITCODE -ne 0) { throw 'migrate falla' }
uv run python manage.py reindexar_corpus; if ($LASTEXITCODE -ne 0) { throw 'el reindexado falla' }
uv run python manage.py reindexar_corpus; if ($LASTEXITCODE -ne 0) { throw 'el reindexado no es idempotente' }
uv run python -c "import os; os.environ['DJANGO_SETTINGS_MODULE']='config.settings.local'; import django; django.setup(); from pathlib import Path; from apps.corpus.models import Ficha; import frontmatter; n=len([q for q in Path('documentation/tax-research').rglob('*.md') if frontmatter.load(q).metadata]); m=Ficha.objects.count(); assert m==n, (m, n); print('corpus indexado OK', n)"; if ($LASTEXITCODE -ne 0) { throw 'el indice no coincide con los ficheros en disco' }
uv run pytest tests/web/test_corpus_indice.py -q; if ($LASTEXITCODE -ne 0) { throw 'las pruebas del indice fallan' }
uv run pytest tests/web -q; if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A; git commit -m "E3-T5: indice citable del corpus, reconstruible desde los ficheros .md"
git tag step-19-fichas
```

### `E3-T6` — Publicación del corpus y enlace desde las fuentes citadas

**Depende de:** `E2-T5`, `E3-T5` · **Prioridad:** p1

Cierra el círculo de trazabilidad: cada `Source` del registro lleva un `research_note` que apunta a una
ficha, y a partir de aquí ese puntero es un enlace navegable en vez de una ruta impresa. La cabecera
de la ficha sale de la fila de `Ficha`; el cuerpo se lee y se renderiza del `.md`. El enlace se
resuelve por identificador, sin tabla de traducción.

**Ficheros**
- `apps/corpus/views.py`, `apps/corpus/urls.py` — nuevos; `/fuentes/` filtrable por jurisdicción y `/fuentes/<path:ruta>/`
- `templates/corpus/indice.html`, `templates/corpus/ficha.html` — nuevos
- `templates/analisis/detalle.html` — edita: cada fuente citada enlaza a su ficha
- `tests/web/test_corpus.py` — nuevo

**Aceptación**

1. **WHEN** the corpus index is requested by an authenticated user **THE SYSTEM SHALL** respond `200` listing one entry per `Ficha` row, each with its title and its normative rank.
2. **WHEN** an existing ficha path is requested **THE SYSTEM SHALL** respond `200` containing that ficha's title, its citation and its verification date.
3. **WHEN** the requested path does not exist in the corpus **THE SYSTEM SHALL** respond `404` and read no file.
4. **WHEN** the requested path contains a parent-directory segment, is absolute, or resolves outside the research directory **THE SYSTEM SHALL** respond `400` and read no file.
5. **WHEN** a case detail page cites a source **THE SYSTEM SHALL** render a link to that source's ficha, resolved by the shared identifier.
6. **WHEN** an anonymous request hits the corpus index **THE SYSTEM SHALL** respond `302` to the login page, because the corpus is behind the session like everything else.

**Verify**

```powershell
uv run pytest tests/web/test_corpus.py -q; if ($LASTEXITCODE -ne 0) { throw 'la publicacion del corpus falla' }
uv run pytest tests/web -q; if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A; git commit -m "E3-T6: publicacion del corpus y enlace desde las fuentes citadas"
git tag step-20-corpus-web
```

### `E3-T7` — `UnidadEstudio`: módulo de estudio, separado de las fichas

**Depende de:** `E3-T5`, `E3-T6` · **Prioridad:** p1

Contenido didáctico propio, en una entidad **separada de `Ficha`**, y la separación es lo que sostiene
todo lo demás: una ficha es fuente citable **con rango normativo**, una unidad de estudio es material
de aprendizaje. Al contrario que `Ficha`, esta se escribe **desde el panel**: es la segunda vez que el
panel se cobra, porque un jurista no-ingeniero publica su material sin tocar el repositorio. La
invariante es dura y se comprueba: ninguna `UnidadEstudio` puede aparecer jamás en un informe.

**Ficheros**
- `apps/estudio/__init__.py`, `apps/estudio/apps.py` — nuevos; `EstudioConfig`, `label = "estudio"`
- `apps/estudio/models.py` — nuevo; `UnidadEstudio`, `db_table = "unidades_estudio"`, M2M a `Ficha`
- `apps/estudio/admin.py`, `apps/estudio/views.py`, `apps/estudio/urls.py` — nuevos; admin **editable**
- `templates/estudio/indice.html`, `templates/estudio/unidad.html` — nuevos, y `config/settings/base.py` edita `INSTALLED_APPS`
- `tests/web/test_estudio.py` — nuevo

**Aceptación**

1. **WHEN** the study index is requested **THE SYSTEM SHALL** list only published units, ordered by their sequence field and then by title.
2. **WHEN** an unpublished unit's slug is requested directly **THE SYSTEM SHALL** respond `404`.
3. **WHEN** a unit linked to two fichas is rendered **THE SYSTEM SHALL** show a link to each of them.
4. **WHEN** `tp_domain.sources.SOURCE_REGISTRY` is inspected **THE SYSTEM SHALL** contain no identifier belonging to any study unit, because study material is never a citable source.
5. **WHEN** a report is generated for any case **THE SYSTEM SHALL** contain no study unit title or slug anywhere in its text.
6. **WHEN** a unit is created from the admin **THE SYSTEM SHALL** persist it, because unlike a ficha this content is authored in the panel and not on disk.

**Verify**

```powershell
uv run python manage.py makemigrations estudio; if ($LASTEXITCODE -ne 0) { throw 'makemigrations falla' }
uv run python manage.py migrate; if ($LASTEXITCODE -ne 0) { throw 'migrate falla' }
uv run pytest tests/web/test_estudio.py -q; if ($LASTEXITCODE -ne 0) { throw 'el modulo de estudio falla' }
$fugas = Select-String -Path (Get-ChildItem 'tp_domain','infrastructure' -Recurse -Filter '*.py' -File).FullName -Pattern 'UnidadEstudio|apps\.estudio' -ErrorAction SilentlyContinue; if ($fugas) { throw 'el dominio o el informe conocen UnidadEstudio; el material de estudio no es citable' }
uv run pytest tests/web -q; if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A; git commit -m "E3-T7: modulo de estudio, entidad separada de las fichas"
git tag step-21-estudio
```

---

## Aceptación de la epic

La epic está hecha cuando todas sus tareas están en `done` **y**:

1. **WHEN** a user whose monthly cap is exhausted submits an analysis **THE SYSTEM SHALL** persist the case, make no call to the provider, write no `LlamadaLLM` row, and serve the report with the AI section declaring its absence.
2. **WHEN** a user with a valid key and model submits an analysis **THE SYSTEM SHALL** record exactly one `LlamadaLLM` with purpose `explicacion` and the provider's reported token counts.
3. **WHEN** a case detail page cites a source **THE SYSTEM SHALL** link to that source's ficha, and the ficha SHALL render from the markdown file on disk.
4. **WHEN** the corpus reindex command runs twice **THE SYSTEM SHALL** leave the identical set of rows.
5. **WHEN** a report is generated **THE SYSTEM SHALL** contain no study unit title or slug anywhere in its text.

```powershell
uv run ruff check .; if ($LASTEXITCODE -ne 0) { throw 'lint' }
uv run mypy .; if ($LASTEXITCODE -ne 0) { throw 'tipos' }
uv run pytest; if ($LASTEXITCODE -ne 0) { throw 'suite completa' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'red de seguridad' }
uv run python manage.py reindexar_corpus; if ($LASTEXITCODE -ne 0) { throw 'reindexado del corpus' }
uv run pytest tests/web/test_cuota.py tests/web/test_ia_degradacion.py -q; if ($LASTEXITCODE -ne 0) { throw 'cuota o degradacion' }
```

## Trampas

- **Conectar la capa de IA antes de tener el freno.** Es la trampa de esta epic. Un tope añadido
  después es un tope que nunca se ha probado en la petición que sí iba a gastar. E3-T2 va antes que
  E3-T3, siempre.
- **Llamar a `comprobar_cuota()` dentro del cliente en vez de antes de construirlo.** El `verify` de
  E3-T3 lo detecta comparando posiciones en el fichero, pero el defecto real es conceptual: para
  entonces ya se ha decidido gastar.
- **Estimar tokens con un tokenizador local.** Diverge de lo que factura el proveedor y el tope acaba
  vigilando un número que nadie paga.
- **Bloquear el análisis cuando se agota la cuota.** El tope desactiva la sección de IA; el producto
  sigue funcionando. Confundirlo convierte un control de coste en una caída de servicio.
- **Hacer `Ficha` editable en el panel.** Una edición allí se pierde en el siguiente reindexado, y una
  tabla que miente sobre el corpus jurídico es peor que no tener tabla.
- **Fusionar `UnidadEstudio` con `Ficha` con una bandera.** Tarde o temprano un informe cita material
  de estudio como si fuera Derecho.
- **Dejar que el cliente decida el tamaño de página.** `?por_pagina=100000` devuelve la tabla entera y
  convierte el listado en una descarga masiva.
- **Un solo estado vacío en el listado.** Un filtro sin resultados parecería una cuenta sin casos, y
  el usuario cree que ha perdido su trabajo.

## Antes de seguir

- [ ] Las siete tareas están en `done` en `tasks.json`; ninguna en `in_progress`.
- [ ] Pasaron **todos** los comandos `verify` de cada tarea, no solo el primero.
- [ ] No se editó ningún comando `verify`, y no se saltó ninguno porque un fichero no existiera.
- [ ] Las siete etiquetas están en git: `step-15-listado` … `step-21-estudio`.
- [ ] El gate pasa limpio desde la raíz del proyecto.
- [ ] Los siete contratos «Producidos» existen con la firma indicada.
- [ ] No se modificó ningún fichero fuera del subárbol. En particular, de `documentation/tax-research/` solo se tocó el
      **frontmatter** de las 9 fichas, en `E3-T4`. Ni un cuerpo, ni el `README.md`.
- [ ] `.env.example` no necesitaba variables nuevas: `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` y las dos
      `PRECIO_*` ya estaban declaradas allí desde el bundle.
- [ ] Un commit por tarea, cada uno prefijado con su id, cada uno seguido de su etiqueta.
