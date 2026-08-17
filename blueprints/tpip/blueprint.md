# TPIP — Transfer Pricing Intelligence Platform — Blueprint

> Generado por The Architect el 2026-08-15
> Forma: aplicación web de un solo inquilino sobre un motor de cálculo existente (migración de interfaz)
> Pista de ejecución: Python · `uv` · Django 5.2 · Windows 10 + PowerShell
> Modo de emisión: bundle (`./blueprints/tpip/`) — 27 pasos de construcción
> Versión del blueprint: 1
> Versiones verificadas por última vez: 2026-08-15 — procedencia por paquete en §11

**Principio rector de todo el documento, literal:**

> **El motor calcula; el modelo explica, fundamenta y puede sugerir, pero nunca decide y nunca escribe un número.**

Cualquier paso, plantilla, prompt o criterio de aceptación que contradiga esa frase es un defecto del
blueprint, no una decisión del constructor.

---

## 1. Visión del proyecto y No-Goals

### Visión

TPIP contrasta el tipo de un canon intragrupo contra un rango de plena competencia y dice, por cada
jurisdicción implicada, qué le pasa a ese tipo **según el Derecho de esa jurisdicción**. El mismo
canon, con los mismos comparables, recibe tratamiento distinto en España (Art. 18.4 LIS: sin regla
estadística legal) y en Alemania (§1.3a AStG: rango intercuartílico obligatorio y ajuste de oficio a
la mediana). Esa asimetría —no el percentil— es el producto. El resultado sale en pantalla y en un
informe PDF que se basta solo: portada con la naturaleza del dataset, resumen ejecutivo, gráfico del
rango, base jurídica por jurisdicción y anexo completo de comparables aceptados y rechazados con el
motivo de cada rechazo.

Esta versión **no construye el motor**: el motor existe, está probado y se queda. Lo que se construye
es su interfaz. TPIP nació como una aplicación de Streamlit; Streamlit impone su propio modelo de
ejecución (el script entero se reevalúa en cada interacción), su propio lenguaje visual y su propia
forma de gestionar secretos, y las tres cosas empezaron a decidir cómo tenía que ser el producto. La
migración a Django devuelve el control de las URL, de las plantillas, del ciclo petición/respuesta y
de la configuración a código que se lee de arriba abajo. **El 92% del Python actual sobrevive intacto**
—dominio, reglas, fuentes, capa de IA e infraestructura de informe— y las **180 pruebas que hoy pasan
son la red de seguridad de la migración**: si dejan de pasar, la migración ha roto algo.

### Usuarios

| Persona | A qué viene | Frecuencia |
|---|---|---|
| Asesor de precios de transferencia (usuario único, en su equipo) | Contrastar un tipo de canon propuesto y llevarse un PDF con la base jurídica por jurisdicción | Semanal, por operación analizada |
| El propio autor, manteniendo el sistema | Añadir una jurisdicción o una ficha jurídica sin romper el motor ni el informe | Mensual |

### Objetivos — alcance de la v1

1. La aplicación web de Django reproduce, sin pérdida funcional, todo lo que hacía la aplicación de
   Streamlit: formulario de operación, resultado con el rango como protagonista, factores de riesgo,
   tratamiento por jurisdicción y descarga del informe PDF.
2. Cada análisis queda persistido y tiene URL propia, de modo que el PDF que se descarga es
   exactamente el análisis que se vio en pantalla —incluida su sección de IA— y no un recálculo.
3. El lenguaje visual de la pantalla y el del informe salen de una sola fuente (`infrastructure/theme.py`),
   con una comprobación automática que falla si divergen.
4. Los dos defectos conocidos quedan corregidos: la resolución dinámica del modelo en
   `ai/claude_client.py:78` y la paleta de superficie única en `infrastructure/theme.py`.
5. El corpus de investigación jurídica (`documentation/tax-research/`, 9 fichas con frontmatter, más un `README.md` que no lo es) se
   publica dentro de la aplicación, de forma que cada fuente citada por el motor enlaza a la ficha que
   la sustenta.

### No-Goals — explícitamente fuera de alcance en la v1

**Esta tabla es la valla del alcance.** Un constructor autónomo con una frontera ambigua construye la
ambigüedad, y cada función de más es una superficie nueva que puede tumbar el gate de aceptación.

| No se construye | Por qué ahora no | Se revisa cuando |
|---|---|---|
| Auto-registro de cuentas | **Hay cuentas** (§8) y el esquema es multiusuario desde la primera migración, pero las da de alta y de baja una persona desde el panel. El auto-registro exigiría verificación por correo y no habilita nada mientras las cuentas se decidan a mano | Haya que dar de alta a alguien a quien no se le puede entregar la contraseña en persona |
| Recuperación de contraseña por correo y servidor SMTP saliente | Es la dependencia que arrastraría el punto anterior. La ruta de recuperación de la v1 es que el administrador la restablezca desde el panel, y así se dice en la propia pantalla de acceso | Exista auto-registro, o el administrador deje de estar disponible |
| Proveedor de identidad externo (OAuth, SSO) | Añade una dependencia de red y un flujo de consentimiento para gestionar un puñado de cuentas que caben en una tabla | El sistema deje de tener un administrador único |
| API JSON pública | Nadie la consume. Una API es un contrato que hay que versionar y mantener, y hoy no hay cliente | Exista un consumidor real distinto del navegador |
| Comparables reales (Orbis, Amadeus, Bloomberg) | Requiere licencia comercial y presupuesto. Sin ellos ningún resultado es utilizable ante una administración, y eso está declarado en el propio informe | Haya licencia contratada de una base comercial |
| Tipos de operación distintos del canon (servicios intragrupo, intereses, dividendos, reparto de costes) | Ya está bloqueado en el dominio (`SUPPORTED_TRANSACTION_TYPES`). Compararlos contra el margen operativo del dataset produce veredictos sin significado económico | Cada tipo tenga su propia rama de cálculo y sus propios comparables |
| Jurisdicciones más allá de ES y DE | El mapa crece ficha a ficha, nunca por analogía. Suponer "sin regla" para un país no estudiado es inventar Derecho comparado | Exista la ficha de investigación de esa jurisdicción, con fuente primaria verificada |
| Tailwind, Node, bundler, framework de front, **conmutador** de tema | **Restricción textual del usuario: *"no quiero algo que yo no llegue a entender"*.** Una cadena de construcción de front introduce un segundo ecosistema, un segundo gestor de paquetes y un paso de compilación entre lo que se escribe y lo que se ve. El CSS de este proyecto se lee tal cual está en disco | El usuario decida que quiere aprender ese ecosistema, no antes |
| Pruebas E2E con navegador (Playwright, Selenium) | Añade un runtime de Node, binarios de navegador y una fuente de intermitencia. El cliente de pruebas de Django cubre el ciclo petición/respuesta completo, que es donde está el riesgo real | La aplicación tenga JavaScript con estado propio |
| PostgreSQL o cualquier servidor de base de datos | SQLite es un fichero. No hay concurrencia, no hay operaciones, no hay nada que administrar | Haya más de un proceso escribiendo a la vez |

**El constructor no debe implementar nada de esta tabla**, aunque parezca un añadido pequeño mientras
trabaja en un paso adyacente. Si un paso parece exigir un No-Goal, eso es un defecto del blueprint:
hay que parar y reportarlo, nunca ampliar el alcance.

### Métricas de éxito

| Métrica | Objetivo | Cómo se mide |
|---|---|---|
| Red de seguridad intacta | 180 pruebas rescatadas pasando, 0 fallos, 0 omitidas, al final del paso 27 | `uv run pytest tests/domain tests/ai tests/report` |
| Paridad funcional con Streamlit | Las 6 rutas de §5 responden su estado documentado | Suite `tests/web/`, gate §20.1 |
| Coherencia pantalla/informe | El CSS de tokens está sincronizado con `infrastructure/theme.py` | `uv run python -m scripts.build_tokens --check` sale 0 |
| Aviso de datos sintéticos presente | El literal `DATOS SINTÉTICOS` aparece en el PDF descargado por la web | `tests/web/test_informe_view.py`, paso 14 |

---

## 2. Pila tecnológica

**Pista de ejecución: Python + `uv`.** Esta tabla nombra *elecciones*, no versiones. Cada versión
fijada vive en §11 y en ningún otro sitio de la prosa —no se repite aquí y no se mantiene una segunda
copia.

Las versiones proceden del informe de `stack-researcher` producido en esta sesión (2026-08-15), que es
la autoridad, y están ya materializadas en el `pyproject.toml` emitido en §19.6. Ninguna se ha escrito
de memoria.

| Capa | Elección | Por qué esta, frente a qué |
|---|---|---|
| Lenguaje / runtime | Python 3.12, gestionado por `uv` | El motor ya es Python y no se reescribe. `uv` frente a `pip` + `venv` a mano: resuelve, fija y crea el entorno en un comando, y es el único que puede instalar el propio intérprete 3.12 en una máquina con 3.11 |
| Framework web | Django 5.2 | Frente a FastAPI: aquí no hay API, hay páginas. Django trae formularios con validación y renderizado, plantillas, ORM, migraciones, ficheros estáticos y comprobaciones de despliegue sin pegar cinco librerías. Frente a Flask: lo mismo, pero habría que elegir y montar cada pieza |
| Estilo | CSS plano con propiedades personalizadas, generadas desde `infrastructure/theme.py` | Frente a Tailwind: exige Node y un paso de compilación (No-Goal). Frente a CSS escrito a mano sin generación: la paleta acabaría duplicada entre pantalla e informe, que es exactamente el defecto que `theme.py` existe para impedir |
| Capa de componentes | Plantillas de Django con `{% include %}` y `{% block %}` | Frente a un framework de componentes: introduce un runtime de JavaScript para una aplicación sin estado de cliente |
| Base de datos | SQLite (fichero `db.sqlite3`) | Frente a PostgreSQL: un usuario, un proceso, cero operaciones. Frente a no persistir nada: el PDF tiene que ser el mismo análisis que se vio, incluida su sección de IA, y recalcular significaría una segunda llamada al modelo con otra redacción |
| Acceso a datos | ORM de Django para una sola entidad; pydantic para todo el dominio | El dominio ya está tipado con pydantic y validado; el ORM solo guarda y devuelve el volcado JSON de ese dominio. No se traduce el dominio a modelos de Django: sería mantener dos veces el mismo vocabulario |
| Autenticación | `django.contrib.auth` con modelo de usuario propio (`cuentas.Usuario`) declarado en `AUTH_USER_MODEL` desde la primera migración | Frente a un proveedor externo: gestionar un puñado de cuentas no justifica una dependencia de red ni un flujo de consentimiento. Frente al usuario por defecto de Django: cambiar `AUTH_USER_MODEL` después de migrar es una reconstrucción de la capa de datos, así que se paga la columna el primer día (§8) |
| Trabajo en segundo plano | Ninguno; la llamada a la IA es síncrona dentro de la petición | Frente a Celery: exige un broker y un proceso más. Un análisis tarda menos de lo que el usuario espera mirando la pantalla, y la capa de IA ya degrada sola si tarda o falla |
| Pagos | NO APLICA | No hay cobro |
| Almacenamiento de ficheros | Ninguno: el PDF se genera en memoria y se sirve en la respuesta | Frente a guardarlo: un PDF regenerado desde el análisis persistido es idéntico y no hay que gestionar retención de ficheros |
| Correo / notificaciones | Ninguno | No hay nada que notificar a nadie |
| Alojamiento | Ejecución local en Windows (`manage.py runserver`), con `config/settings/production.py` preparado y comprobado por `check --deploy` pero sin plataforma contratada | Frente a desplegar: no hay usuario remoto. Los ajustes de producción existen para que la comprobación de seguridad sea real, no para desplegar hoy |
| Registro de eventos | `structlog` a consola | Frente al `logging` de la biblioteca estándar a secas: los eventos del análisis (jurisdicciones, posición, resultado de la capa de IA) se leen mucho mejor estructurados, y `structlog` se apoya en `logging`, no lo sustituye |
| Ficheros estáticos | WhiteNoise | Sirve estáticos desde el propio proceso de Django, sin nginx delante. Frente a `runserver` a pelo: `runserver` no sirve estáticos con `DEBUG=False`, y entonces la comprobación de producción no probaría nada |
| Gestor de paquetes | `uv` | Ver runtime |
| Pruebas | `pytest` + `pytest-django` | El motor ya tiene 180 pruebas en pytest. Cambiar a `unittest` de Django obligaría a reescribirlas, que es justamente lo que la red de seguridad impide |
| Lint y formato | `ruff` | Un solo binario para lint, orden de imports y formato. Frente a flake8 + isort + black: tres herramientas y tres configuraciones |
| Tipos | `mypy` | Solo sobre el código nuevo (`apps/`, `config/`, `scripts/`, `manage.py`); el código rescatado está excluido en el `pyproject.toml` emitido |

### Comprobación de compatibilidad

Contrastado contra `knowledge/stack-compatibility.md`: **no hay ninguna combinación marcada como
incompatible**. El repositorio no registra conflictos conocidos para Python + Django + `uv`; su única
entrada relevante para Python (una canalización de datos alojada en un PaaS de contenedores frente a
un host por petición) no aplica aquí, porque esto es una aplicación local. No ha hecho falta ninguna
sustitución.

Sí hay dos incompatibilidades **dentro del propio repositorio actual**, y las resuelve §10:

1. El `pyproject.toml` que hoy hay en la raíz es de la etapa Streamlit (setuptools, `requires-python
   >=3.10`, dependencia de `streamlit`). El emitido en §19.6 no se puede copiar encima sin archivar
   primero el antiguo. §10 lo archiva a `pyproject.toml.pre-django`, una sola vez y de forma
   idempotente.
2. El `.venv` actual lleva Python 3.11.9, que no satisface `requires-python >= 3.12`. §10 lo detecta
   por `pyvenv.cfg` y lo recrea.

---

## 3. Estructura de directorios

```
transfer-pricing-intelligence-platform/
  manage.py                      # punto de entrada de Django. Fija DJANGO_SETTINGS_MODULE =
                                 # "config.settings.local" (mismo literal que pyproject.toml)
  pyproject.toml                 # emitido en §19.6 — dependencias, ruff, mypy, pytest
  uv.lock                        # lo genera `uv sync`; se versiona
  .env.example                   # emitido en §19.6 — todas las claves, todos los valores vacíos
  .env                           # NUNCA versionado; lo crea el bootstrap copiando .env.example
  .gitignore                     # emitido en §19.6 — incluye blueprints/ y la excepción !.env.example
  db.sqlite3                     # base de datos local; ignorada por git
  staticfiles/                   # salida de collectstatic (STATIC_ROOT); ignorada por git

  config/                        # el proyecto de Django. Nada de lógica de negocio vive aquí
    __init__.py
    settings/
      __init__.py
      base.py                    # configuración tipada con pydantic-settings; ÚNICO punto que lee .env
      local.py                   # desarrollo: DEBUG on, host local
      production.py              # DEBUG off, cabeceras y cookies seguras — lo audita `check --deploy`
    logging.py                   # configuración de structlog
    urls.py                      # raíz de URLs; delega en cada app
    wsgi.py
    asgi.py

  apps/                          # aplicaciones de Django. Una por superficie, no por entidad
    __init__.py
    comun/                       # lo transversal. Sin modelos ni rutas propias
      __init__.py
      middleware.py              # ExigirAutenticacion: cierre por omisión (§8), paso 5
      guardas.py                 # caso_del_usuario() — la ÚNICA puerta de lectura de un Caso
      consultas.py               # casos_de() — filtra por propietario antes que por nada más
      management/commands/       # copia_seguridad.py y restaurar_copia.py, paso 24
    cuentas/                     # la cuenta. Su migración es la PRIMERA del proyecto (§4.5)
      __init__.py  apps.py  admin.py  urls.py  views.py
      models.py                  # Usuario — el modelo de AUTH_USER_MODEL, paso 4
      migrations/                # las genera `manage.py makemigrations`; nunca se escriben a mano
        __init__.py
    analisis/                    # formulario, motor, persistencia, resultado, informe, precedentes
      __init__.py  apps.py  admin.py  urls.py
      models.py                  # Caso y CasoContrastado (§4), pasos 6 y 22
      migrations/__init__.py
      forms.py                   # traduce el POST a un tp_domain.models.Transaction
      services.py                # motor -> cuota -> persistencia -> capa de IA. Sin HTTP dentro
      views.py                   # solo HTTP: recibe, delega en services, responde
    corpus/                      # índice citable del corpus de investigación jurídica
      __init__.py  apps.py  admin.py  urls.py  views.py
      models.py                  # Ficha (§4), paso 19
      indexador.py               # lee documentation/tax-research/**.md con frontmatter
      management/commands/reindexar_corpus.py
      migrations/__init__.py
    estudio/                     # material didáctico. NUNCA citable en un informe
      __init__.py  apps.py  admin.py  urls.py  views.py
      models.py                  # UnidadEstudio (§4), paso 21
      migrations/__init__.py
    ia/                          # registro de llamadas y freno de gasto
      __init__.py  apps.py  admin.py
      models.py                  # LlamadaLLM (§4), paso 16
      cuota.py                   # comprobar_cuota() — se llama ANTES de construir el cliente
      registro.py                # el único escritor de LlamadaLLM
      migrations/__init__.py
    evaluacion/                  # arnés de evaluación y puerta de regresión
      __init__.py  apps.py  admin.py
      models.py                  # CasoEvaluacion y EjecucionEvaluacion (§4), paso 23
      puntuadores.py             # de lo más barato a lo más caro; paran en el primero que decide
      management/commands/       # reindexar_evaluacion.py y evaluar.py
      migrations/__init__.py

  templates/                     # DIRS de plantillas a nivel de proyecto (no por app)
    base.html                    # esqueleto, salto al contenido, landmarks
    cuentas/
      entrar.html
      contrasena.html
    analisis/
      form.html                  # el aviso de privacidad va aquí, además del pie (§8, paso 25)
      lista.html                 # búsqueda, filtro, orden, vacíos y paginación (paso 15)
      detalle.html
      contrastados.html
      contrastado.html
    corpus/
      indice.html
      ficha.html
    estudio/
      indice.html
      unidad.html
    privacidad.html              # el detalle del aviso de §8, paso 25
    partials/
      _benchmark.html            # el rango, protagonista de la página
      _risk_factors.html
      _jurisdictions.html
    400.html  403.html  404.html  405.html  500.html

  static/
    css/
      tokens.css                 # GENERADO por scripts/build_tokens.py desde infrastructure/theme.py.
                                 # Se versiona, y un gate falla si queda desincronizado
      app.css                    # escrito a mano; solo consume las variables de tokens.css

  scripts/
    __init__.py                  # hace de scripts/ un paquete: los scripts se invocan con -m (§19.6)
    build_tokens.py              # theme.COLORS -> static/css/tokens.css. Modo --check para el gate

  tp_domain/                     # RESCATADO — 1.133 líneas. Solo se toca lo que diga un paso
    __init__.py
    models.py                    # vocabulario del dominio en pydantic
    sources.py                   # registro cerrado de fuentes citables
    comparables.json             # dataset sintético v1
    calculations/
      __init__.py
      arm_length_range.py        # el motor
    rules/
      __init__.py
      statistical_rules.py       # mapa jurisdicción -> regla estadística

  ai/                            # RESCATADO — 638 líneas
    __init__.py
    claude_client.py             # el paso 8 corrige aquí el defecto de resolución dinámica
    schemas.py
    validators.py
    prompts/
      explain_analysis_v1.md     # el prompt versionado; el nombre del fichero ES la versión

  infrastructure/                # RESCATADO — 913 líneas
    __init__.py
    theme.py                     # el paso 9 corrige aquí la paleta de superficie única
    charts.py                    # SVG del rango para la pantalla
    report/
      __init__.py
      pdf_report.py              # el informe PDF con reportlab

  documentation/
    tax-research/                # 9 fichas .md con frontmatter + README.md sin él.
                                 # El paso 18 lo completa; el 19 lo indexa; el 20 lo publica

  tests/
    __init__.py
    conftest.py
    domain/                      # RESCATADO — 89 pruebas
    ai/                          # RESCATADO — 53 pruebas
    report/                      # RESCATADO — 38 pruebas
    web/                         # NUEVO — todo lo que añade esta migración
      __init__.py                # obligatorio: sin él pytest no inserta la raíz en sys.path (§19.6)
      conftest.py                # fixtures usuario / otro_usuario / administrador — paso 4

  .claude/                       # emitido en §19.6 / §19.3
    settings.json
    rules/
    skills/
  .github/workflows/ci.yml       # lo escribe el paso 27
  blueprints/tpip/               # ESTE bundle. Excluido en ruff, mypy y pytest, e ignorado por git
```

**Reglas de frontera**

- `tp_domain/` no importa nada de Django, de `apps/`, de `infrastructure/` ni de `ai/`. Es el núcleo:
  todo apunta hacia dentro. Un `import django` en `tp_domain/` es un defecto.
- `ai/` importa de `tp_domain/` y de nada más del proyecto. **No importa Django**: a partir del paso 8,
  su configuración (clave y modelo) se le inyecta desde fuera en vez de descubrirla ella. Esa es la
  corrección del defecto 1.
- `infrastructure/` importa de `tp_domain/`. No importa de `apps/` ni de Django.
- `apps/*/views.py` solo hace HTTP: lee la petición, llama a `services.py`, devuelve una respuesta.
  Ninguna vista importa `tp_domain.calculations` directamente.
- `apps/analisis/services.py` es el único sitio que junta motor, persistencia, cuota y capa de IA.
- Toda lectura de una fila con propietario pasa por `apps/comun/guardas.py`. Ninguna vista
  construye una consulta sobre `Caso` por su cuenta.
- `static/css/app.css` no contiene ni un color literal: solo `var(--tpip-*)` de `tokens.css`.
- Ninguna plantilla calcula nada. Si hay que derivar un valor, se deriva en `services.py`.

**Convención de resolución de módulos.** Todo el proyecto usa **imports absolutos desde la raíz**
(`from tp_domain.models import Transaction`, `from apps.analisis.forms import TransactionForm`). No
hay alias de rutas, no hay imports relativos entre paquetes de primer nivel y **el proyecto no se
instala como paquete** (`[tool.uv] package = false` en el `pyproject.toml` emitido). Esa convención
solo está medio escrita aquí: **su reconciliación contra cada contexto que carga módulos está en la
matriz de convención de resolución de §19.6**, que es donde se dice qué hace que funcione en la
aplicación, en las pruebas, en los scripts sueltos y en la construcción de estáticos. El caso que
obliga a mirarla es el de los scripts: `python scripts/build_tokens.py` **no encuentra** `infrastructure`,
y `python -m scripts.build_tokens` sí.

**Un fichero dibujado en este árbol no queda creado por dibujarlo.** Cada uno tiene exactamente uno de
dos orígenes: lo escribe un paso de §9 nombrándolo en su lista **Do**, o se emite como fichero real
bajo `workspace/` en §19.6 y aterriza con la copia guardada que hace §10 antes del paso 1. `pyproject.toml`,
`.gitignore`, `.env.example` y `.claude/settings.json` tienen el segundo origen; todo lo demás, el primero.

**Valores que este árbol comparte con ficheros emitidos** —`config.settings.local`, `staticfiles/`,
`db.sqlite3`, `static/css/tokens.css`, `blueprints/`— están conciliados literal a literal en la tabla
*Conciliación de valores entre artefactos* de §19.6. Este árbol copia esos literales de allí y no
decide ninguno por su cuenta.

---

## 4. Modelo de datos

El dominio de cálculo de TPIP **ya está modelado**, en pydantic, dentro de `tp_domain/models.py`, y
esta migración no lo reescribe: sigue siendo el vocabulario del motor y viaja dentro de cada caso como
volcado JSON. Lo que se añade encima son **ocho entidades persistidas** que son las que convierten un
motor de cálculo en un producto con cuentas, casos buscables, corpus citable, material de estudio,
control de gasto y evidencia de regresión.

### 4.0 Reglas de esquema que valen para las ocho tablas

Se enuncian una vez aquí y no se repiten entidad por entidad.

| Regla | Cómo se materializa | Por qué |
|---|---|---|
| **`usuario_id` en toda tabla de usuario**, con índice y `not null` | `ForeignKey(settings.AUTH_USER_MODEL, on_delete=PROTECT, db_index=True)`, sin `null=True` | *"De quién es esta fila"* tiene que tener respuesta desde la primera fila que se escribe. Retrofitarlo después es reescribir la capa de datos |
| **Marcas de tiempo con zona horaria, almacenadas en UTC** | `USE_TZ = True` en `config/settings/base.py` y `DateTimeField` en todas partes; Django guarda en UTC y convierte a `Europe/Madrid` solo al presentar | Un informe fiscal lleva fechas. Una marca sin zona es una marca que cambia de significado al cambiar de máquina |
| **Borrado suave con índice único parcial** | `UniqueConstraint(..., condition=Q(deleted_at__isnull=True))` en toda tabla con borrado suave y clave natural | Sin la condición, una fila borrada sigue ocupando su identificador para siempre y no se puede volver a usar. Con ella, el identificador se libera al borrar y sigue siendo único entre las filas vivas |
| **Nombres de tabla en plural y `snake_case`** | `db_table` explícito en cada `Meta` | Django los derivaría como `analisis_caso`, `cuentas_usuario`: prefijo de aplicación y singular. Fijarlos a mano los hace legibles desde una consola de SQL y estables si una aplicación se renombra |

Los nombres de tabla, fijados: `usuarios` · `casos` · `fichas` · `unidades_estudio` ·
`casos_contrastados` · `llamadas_llm` · `casos_evaluacion` · `ejecuciones_evaluacion`.

### 4.1 Entidades

**`Usuario`** — la cuenta. Vive en `apps/cuentas/models.py` y hereda de `AbstractUser`.

| Campo | Tipo | Restricciones | Significado |
|---|---|---|---|
| `id` | `BigAutoField` | PK (heredado) | — |
| `username`, `password`, `is_active`, `is_staff`, `is_superuser`, `date_joined`, `last_login` | heredados de `AbstractUser` | — | Alta, baja y permisos los gestiona el administrador desde el panel |
| `email` | `EmailField` | **unique**, not null | `AbstractUser` lo trae opcional y no único; aquí es el identificador de contacto real |
| `tope_gasto_mensual_eur` | `DecimalField(8,2)` | not null, `default=5.00` | El freno de mano de §17. Se comprueba **antes** de cada llamada al proveedor |
| `notas_admin` | `TextField` | blank | Para quien administra: por qué se dio de alta esta cuenta |

**Por qué un modelo propio desde el primer día, aunque en la v1 haya un solo usuario.** Cambiar
`AUTH_USER_MODEL` después de la migración inicial no es una migración: es reescribir la capa de datos
entera, porque toda tabla con una clave foránea al usuario apunta a una tabla que deja de existir.
Django lo documenta como una operación de varios días. La columna de hoy cuesta una línea; la
migración de mañana cuesta el proyecto. **La baja de una cuenta es `is_active = False`, nunca un
`DELETE`**: un `DELETE` chocaría con los `PROTECT` de abajo, que es exactamente lo que se quiere.

---

**`Caso`** — un análisis ejecutado y guardado, propiedad de un usuario. `apps/analisis/models.py`.
Es la entidad que en la etapa anterior se llamaba `Analysis`; gana propietario, título y borrado suave.

| Campo | Tipo | Restricciones | Significado |
|---|---|---|---|
| `id` | `UUIDField` | PK, `default=uuid.uuid4`, no editable | Aparece en una ruta; un contador delataría cuántos casos hay |
| `usuario` | `ForeignKey` → `settings.AUTH_USER_MODEL` | **not null**, **indexado**, `on_delete=PROTECT`, `related_name="casos"` | El propietario. **Es lo que hace decidible el aislamiento**: sin esta columna, "de quién es esta fila" no tiene respuesta |
| `titulo` | `CharField(160)` | not null | Lo escribe el usuario; si lo deja vacío, se deriva de `description` recortada. Es lo que se busca y lo que se lista |
| `created_at` | `DateTimeField` | `auto_now_add`, indexado | — |
| `deleted_at` | `DateTimeField` | **null**, indexado | Borrado suave. Un caso borrado desaparece de listados y vistas pero conserva sus `LlamadaLLM`, que son el registro de gasto |
| `engine_version` | `CharField(16)` | not null | Derivado de `payload` al guardar |
| `dataset_version` | `CharField(16)` | not null | Derivado de `payload` al guardar |
| `has_ai_explanation` | `BooleanField` | `default=False` | Derivado de `payload` al guardar |
| `payload` | `JSONField` | not null | `AnalysisResult.model_dump(mode="json")`. **Es la fuente de verdad**; los tres campos anteriores se derivan de él, nunca al revés |

**Regla de rehidratación:** todo lo que lea un `Caso` reconstruye el objeto de dominio con
`AnalysisResult.model_validate(obj.payload)` y trabaja sobre él. Ninguna plantilla lee claves sueltas
de `payload`.

**Gestores:** `Caso.objects` excluye las filas con `deleted_at` no nulo; `Caso.todos` las incluye y lo
usa **solo** el panel de administración. El gestor por defecto es el que filtra, para que olvidarse del
filtro sea imposible en vez de improbable.

---

**`Ficha`** — el índice citable del corpus de investigación jurídica. `apps/corpus/models.py`.

**El `.md` en disco es la fuente de verdad; esta tabla es un índice reconstruible.** El usuario escribe
sus fichas en Obsidian, dentro de `documentation/tax-research/`, y la aplicación las lee. El comando
`reindexar_corpus` vacía la tabla y la reconstruye desde los ficheros; por eso el panel de
administración la muestra **en solo lectura**: una edición allí se perdería en el siguiente reindexado,
y una tabla que miente es peor que una tabla que no existe.

El vocabulario no se inventa: se reutiliza el que ya existe en `tp_domain/sources.py`.

| Campo | Tipo | Restricciones | Significado |
|---|---|---|---|
| `id` | `CharField(80)` | PK | El mismo identificador que usa el registro cerrado del motor (`es-lis-art18-4`), para que una fuente citada por el motor resuelva a su ficha sin tabla de traducción |
| `fecha_creacion`, `origen`, `tipo`, `usar_en`, `enlaces` | `CharField` / `TextField` / `JSONField` | blank | **Los campos que el usuario ya tenía en su frontmatter y que se conservan tal cual.** No los consume el motor, pero se indexan para que la ficha en pantalla enseñe lo mismo que el fichero en Obsidian |
| `titulo` | `CharField(200)` | not null | Del frontmatter `titulo` |
| `jurisdiccion` | `CharField(8)` | not null, indexado | `ES` · `DE` · `EU` · `OECD`. **Se deduce de la ruta del fichero** —`jurisdictions/spain/` → `ES`, `frameworks/` → `OECD`— y un campo explícito en el frontmatter la sobrescribe. No estaba en el frontmatter original y no hacía falta añadirla: el corpus ya está organizado por jurisdicción |
| `clase` | `CharField(24)` | choices derivadas de `SourceKind` | `legislation` · `guidelines` · `case_law` · `dataset` |
| `rango_normativo` | `CharField(80)` | not null | *"Ley ordinaria"*, *"Reglamento"*, *"Directrices OCDE"*, *"Doctrina administrativa"*. **Es lo que distingue una ficha de una unidad de estudio**: la ficha tiene rango |
| `cita` | `TextField` | not null | La cita completa y formateada |
| `pinpoint` | `CharField(120)` | blank | El punto exacto: artículo, apartado, párrafo |
| `tipo_localizador` | `CharField(16)` | choices derivadas de `LocatorType` | `boe_id` · `url` · `offline` · `internal` |
| `localizador` | `CharField(300)` | not null | El identificador o la ruta concretos |
| `url_oficial` | `URLField(400)` | blank | Opcional: no toda fuente tiene URL profunda resoluble |
| `confianza_verificacion` | `CharField(32)` | null, choices derivadas de `VerificationConfidence` | `primary_source_verified` · `directed_reading`. Nulo solo para `clase=dataset` |
| `verificada_el` | `DateField` | not null | Del frontmatter |
| `ruta_fichero` | `CharField(300)` | **unique**, not null | Ruta relativa dentro del corpus. Es la clave de reconstrucción |
| `hash_fichero` | `CharField(64)` | not null | SHA-256 del `.md`. Permite detectar que un fichero cambió sin reindexar |
| `actualizada_el` | `DateTimeField` | `auto_now` | Cuándo la indexó el comando |

---

**`UnidadEstudio`** — material didáctico propio. `apps/estudio/models.py`.

**Es una entidad separada de `Ficha`, y la separación es load-bearing.** Una ficha es una **fuente
citable con rango normativo**; una unidad de estudio es **material de aprendizaje** que su autor
escribe para entender algo. Meterlas en la misma tabla con una bandera invitaría, tarde o temprano, a
que un informe cite material de estudio como si fuera Derecho. La invariante es dura: **ninguna
`UnidadEstudio` puede aparecer jamás en `AnalysisResult.sources` ni en el informe PDF.**

| Campo | Tipo | Restricciones | Significado |
|---|---|---|---|
| `id` | `BigAutoField` | PK | — |
| `slug` | `SlugField(80)` | **unique** | Su URL |
| `titulo` | `CharField(200)` | not null | — |
| `resumen` | `CharField(300)` | not null | Qué se aprende aquí; se muestra en el índice |
| `cuerpo` | `TextField` | not null | Markdown, editado desde el panel de administración |
| `orden` | `PositiveIntegerField` | `default=0` | Un itinerario tiene secuencia; la alfabética no sirve |
| `publicada` | `BooleanField` | `default=False` | Se escribe en borrador y se publica cuando está |
| `fichas` | `ManyToManyField` → `Ficha` | blank, `related_name="unidades"` | Una unidad **puede enlazar** a las fichas que estudia. La flecha va en este sentido y no al revés: la ficha no sabe que alguien la estudia |
| `creada_el`, `actualizada_el` | `DateTimeField` | `auto_now_add` / `auto_now` | — |

---

**`CasoContrastado`** — biblioteca curada de precedentes. `apps/analisis/models.py`.

Distinta de `Caso`: un `Caso` es **privado de su usuario** y lo filtra la guarda de §8; un
`CasoContrastado` es **visible para toda cuenta autenticada** y lo publica un administrador. Curar un
caso **no lo desprivatiza**: se copia su `payload` congelado, y el caso original sigue siendo de quien
era.

| Campo | Tipo | Restricciones | Significado |
|---|---|---|---|
| `id` | `BigAutoField` | PK | — |
| `slug` | `SlugField(80)` | **unique** | Su URL |
| `titulo` | `CharField(160)` | not null | — |
| `caso_origen` | `ForeignKey` → `Caso` | **null**, `on_delete=SET_NULL` | De qué caso privado se curó. Nulo si aquel se borró de verdad: el precedente sobrevive a su origen |
| `payload` | `JSONField` | not null | **Copia congelada.** No sigue vivo al caso origen: un precedente que cambia solo no es un precedente |
| `comentario_curador` | `TextField` | not null | Por qué este caso merece estar aquí. Sin esto es una fila más |
| `publicado` | `BooleanField` | `default=False` | — |
| `curado_por` | `ForeignKey` → `settings.AUTH_USER_MODEL` | not null, `on_delete=PROTECT` | Quién lo publicó |
| `creado_el` | `DateTimeField` | `auto_now_add` | — |

---

**`LlamadaLLM`** — el registro de cada llamada al proveedor. `apps/ia/models.py`.

**El uso lo reporta el proveedor; nunca se estiman tokens contándolos por nuestra cuenta.** Un recuento
propio diverge del que factura el proveedor, y entonces el tope de gasto vigila un número que no es el
que se paga.

| Campo | Tipo | Restricciones | Significado |
|---|---|---|---|
| `id` | `BigAutoField` | PK | — |
| `usuario` | `ForeignKey` → `settings.AUTH_USER_MODEL` | not null, indexado, `PROTECT` | A quién se le imputa el gasto |
| `caso` | `ForeignKey` → `Caso` | null, `SET_NULL` | Qué caso la originó. Nulo para las llamadas del arnés de evaluación |
| `creada_el` | `DateTimeField` | `auto_now_add`, indexado | — |
| `proposito` | `CharField(32)` | not null, indexado | Para qué se llamó: `explicacion` (la sección narrativa de un caso) o `evaluacion` (una pasada del arnés del paso 23). Sin este campo, el coste del arnés y el del producto se suman en el mismo número y el tope de gasto de un usuario lo consumiría una evaluación |
| `modelo` | `CharField(80)` | not null | El identificador exacto que se usó |
| `prompt_version` | `CharField(40)` | not null | De `ai/schemas.py` |
| `tokens_entrada` | `PositiveIntegerField` | `default=0` | `usage.input_tokens`, **reportado por el proveedor** |
| `tokens_salida` | `PositiveIntegerField` | `default=0` | `usage.output_tokens`, reportado |
| `tokens_cache_escritura` | `PositiveIntegerField` | `default=0` | Reportado; se registra aunque hoy no se use caché, para que activarla no exija migración |
| `tokens_cache_lectura` | `PositiveIntegerField` | `default=0` | Reportado |
| `coste_eur` | `DecimalField(10,6)` | not null, `default=0` | Calculado a partir de los tokens reportados y la tarifa configurada |
| `latencia_ms` | `PositiveIntegerField` | not null | Medido alrededor de la llamada |
| `razon_finalizacion` | `CharField(32)` | blank | El `stop_reason` del proveedor |
| `error` | `CharField(200)` | blank | **La categoría** del fallo cuando no hubo respuesta, nunca el contenido |
| `intento` | `PositiveSmallIntegerField` | not null | 1 o 2 — `MAX_ATTEMPTS` del cliente rescatado |

---

**`CasoEvaluacion`** — un caso del conjunto dorado. `apps/evaluacion/models.py`.

Igual que `Ficha`: **el conjunto dorado vive en control de versiones**, en `evaluacion/casos/*.json`, y
la tabla lo indexa. Se reconstruye con `reindexar_evaluacion`. Un conjunto dorado que solo existe en
una base de datos no se revisa en un *pull request*, y entonces deja de ser dorado.

| Campo | Tipo | Restricciones | Significado |
|---|---|---|---|
| `id` | `CharField(60)` | PK | El nombre del fichero sin extensión |
| `descripcion` | `CharField(200)` | not null | Qué comportamiento fija este caso |
| `entrada` | `JSONField` | not null | Un `AnalysisResult` congelado que se le da al modelo |
| `propiedades_esperadas` | `JSONField` | not null | Lo que la explicación debe cumplir: fuentes que debe citar, fuentes que no puede citar, cifras que no puede introducir, extensión |
| `activo` | `BooleanField` | `default=True` | Un caso se retira sin borrarlo, para que la comparación con la línea base siga leyéndose |

---

**`EjecucionEvaluacion`** — una pasada completa del arnés. `apps/evaluacion/models.py`.

| Campo | Tipo | Restricciones | Significado |
|---|---|---|---|
| `id` | `BigAutoField` | PK | — |
| `ejecutada_el` | `DateTimeField` | `auto_now_add`, indexado | — |
| `sha_commit` | `CharField(40)` | not null | El commit exacto del repositorio en el que se ejecutó, obtenido con `git rev-parse HEAD`. **Sin él, una tasa de acierto no es reproducible**: no se sabría contra qué código ni contra qué conjunto dorado se midió |
| `modelo` | `CharField(80)` | not null | Contra qué modelo se ejecutó |
| `prompt_version` | `CharField(40)` | not null | Contra qué prompt |
| `casos_totales` | `PositiveIntegerField` | not null | Casos activos en esta pasada |
| `casos_acertados` | `PositiveIntegerField` | not null | — |
| `tasa_acierto` | `FloatField` | not null | Derivado y desnormalizado: es lo que la puerta de CI compara contra la línea base, y hacerlo sin abrir el detalle importa |
| `coste_total_eur` | `DecimalField(10,6)` | not null | **El coste va junto a la precisión**: una mejora de precisión que triplica el coste es una decisión, no una mejora |
| `latencia_p50_ms`, `latencia_p95_ms` | `PositiveIntegerField` | not null | Igual razonamiento |
| `es_linea_base` | `BooleanField` | `default=False` | Exactamente una fila con `True`. Es contra la que compara la puerta de CI |
| `detalle` | `JSONField` | not null | Por caso: acertado o no, qué puntuador lo decidió y por qué |

### 4.2 Relaciones

```
Usuario —(1:N, PROTECT)→ Caso                       un caso siempre tiene dueño
Usuario —(1:N, PROTECT)→ LlamadaLLM                 el gasto siempre tiene a quién imputarse
Usuario —(1:N, PROTECT)→ CasoContrastado            (curado_por)
Caso    —(1:N, SET_NULL)→ LlamadaLLM                la llamada sobrevive al borrado real del caso
Caso    —(0..1:N, SET_NULL)→ CasoContrastado        (caso_origen) el precedente sobrevive a su origen
Ficha   —(M:N)→ UnidadEstudio                       una unidad estudia varias fichas; la ficha no lo sabe
```

**`PROTECT` en todo lo que cuelga de un usuario, y es deliberado.** Borrar una cuenta con casos tiene
que **fallar ruidosamente**, no llevarse los casos por delante ni dejarlos huérfanos. La baja de una
cuenta es `is_active = False` (§8), que corta el acceso y conserva la evidencia. Un `CASCADE` aquí
sería un borrado de datos fiscales a un clic de distancia en un panel de administración.

`SET_NULL` donde la fila hija tiene valor propia sin su padre: una `LlamadaLLM` es registro de gasto y
vale aunque el caso ya no esté; un `CasoContrastado` es un precedente publicado y no debe evaporarse
porque alguien limpie su caso privado.

**`Ficha` y `CasoEvaluacion` no tienen `usuario_id` y no es un olvido:** no son datos de usuario. La
ficha es corpus compartido —índice de ficheros del repositorio— y el caso de evaluación es un artefacto
de ingeniería. La guarda de §8 no se les aplica porque no hay nada que aislar.

### 4.3 Índices

| Tabla | Índice | Para qué consulta |
|---|---|---|
| `analisis_caso` | `(usuario, -created_at)` compuesto | **La consulta central del producto**: el listado de casos de un usuario, ordenado por fecha. Sin él, cada carga del listado recorre la tabla entera |
| `analisis_caso` | `deleted_at` | El gestor por defecto filtra por este campo en **todas** las consultas |
| `analisis_caso` | `titulo` | La búsqueda del listado (paso 15) |
| `cuentas_usuario` | `email` (unique, implícito) | Alta y comprobación de unicidad |
| `corpus_ficha` | `jurisdiccion` | El filtro del índice del corpus |
| `corpus_ficha` | `ruta_fichero` (unique, implícito) | La reconstrucción del índice busca por ruta |
| `ia_llamadallm` | `(usuario, creada_el)` compuesto | La comprobación de cuota suma el gasto del mes de un usuario, y ocurre **antes de cada llamada**: es la consulta más sensible a la latencia de todo el sistema |
| `estudio_unidadestudio` | `(publicada, orden)` compuesto | El itinerario publicado, en su secuencia |
| `evaluacion_ejecucionevaluacion` | `ejecutada_el` | La comparación con la línea base y el histórico |

### 4.4 Esquema

```python
# apps/cuentas/models.py — paso 4
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

    def __str__(self) -> str:
        return self.username
```

```python
# apps/analisis/models.py — pasos 6 y 22
import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q, UniqueConstraint


class CasoVivoManager(models.Manager):
    """Gestor por defecto: las filas borradas en suave no existen para nadie
    salvo para el panel de administración."""

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class Caso(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="casos", db_index=True,
    )
    titulo = models.CharField(max_length=160, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    engine_version = models.CharField(max_length=16)
    dataset_version = models.CharField(max_length=16)
    has_ai_explanation = models.BooleanField(default=False)
    payload = models.JSONField()

    objects = CasoVivoManager()
    todos = models.Manager()

    class Meta:
        db_table = "casos"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["usuario", "-created_at"])]
        constraints = [
            # Índice único PARCIAL: un usuario no puede tener dos casos vivos con
            # el mismo título, pero al borrar uno en suave el título vuelve a estar
            # libre. Sin la condición, una fila borrada bloquearía su identificador
            # para siempre.
            UniqueConstraint(
                fields=["usuario", "titulo"],
                condition=Q(deleted_at__isnull=True),
                name="titulo_unico_por_usuario_entre_casos_vivos",
            ),
        ]

    def __str__(self) -> str:
        return self.titulo


class CasoContrastado(models.Model):
    slug = models.SlugField(max_length=80, unique=True)
    titulo = models.CharField(max_length=160)
    caso_origen = models.ForeignKey(Caso, null=True, blank=True, on_delete=models.SET_NULL)
    payload = models.JSONField()
    comentario_curador = models.TextField()
    publicado = models.BooleanField(default=False)
    curado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    creado_el = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "casos_contrastados"
        ordering = ["-creado_el"]
```

```python
# apps/corpus/models.py — paso 19
from django.db import models


class Ficha(models.Model):
    """Índice RECONSTRUIBLE del corpus. El .md en disco es la fuente de verdad."""

    id = models.CharField(max_length=80, primary_key=True)
    titulo = models.CharField(max_length=200)
    jurisdiccion = models.CharField(max_length=8, db_index=True)
    clase = models.CharField(max_length=24)
    rango_normativo = models.CharField(max_length=80)
    cita = models.TextField()
    pinpoint = models.CharField(max_length=120, blank=True)
    tipo_localizador = models.CharField(max_length=16)
    localizador = models.CharField(max_length=300)
    url_oficial = models.URLField(max_length=400, blank=True)
    confianza_verificacion = models.CharField(max_length=32, null=True, blank=True)
    verificada_el = models.DateField()
    ruta_fichero = models.CharField(max_length=300, unique=True)
    hash_fichero = models.CharField(max_length=64)
    actualizada_el = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fichas"
        ordering = ["jurisdiccion", "id"]
```

```python
# apps/estudio/models.py — paso 21
from django.db import models


class UnidadEstudio(models.Model):
    """Material didáctico. NUNCA es fuente citable: no aparece en ningún informe."""

    slug = models.SlugField(max_length=80, unique=True)
    titulo = models.CharField(max_length=200)
    resumen = models.CharField(max_length=300)
    cuerpo = models.TextField()
    orden = models.PositiveIntegerField(default=0)
    publicada = models.BooleanField(default=False)
    fichas = models.ManyToManyField("corpus.Ficha", blank=True, related_name="unidades")
    creada_el = models.DateTimeField(auto_now_add=True)
    actualizada_el = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "unidades_estudio"
        ordering = ["orden", "titulo"]
        indexes = [models.Index(fields=["publicada", "orden"])]
```

```python
# apps/ia/models.py — paso 16
from django.conf import settings
from django.db import models


class LlamadaLLM(models.Model):
    """Uso REPORTADO POR EL PROVEEDOR. Nunca se estiman tokens contándolos aquí."""

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_index=True)
    caso = models.ForeignKey("analisis.Caso", null=True, blank=True, on_delete=models.SET_NULL)
    creada_el = models.DateTimeField(auto_now_add=True, db_index=True)
    proposito = models.CharField(max_length=32, db_index=True)  # "explicacion" | "evaluacion"
    modelo = models.CharField(max_length=80)
    prompt_version = models.CharField(max_length=40)
    tokens_entrada = models.PositiveIntegerField(default=0)
    tokens_salida = models.PositiveIntegerField(default=0)
    tokens_cache_escritura = models.PositiveIntegerField(default=0)
    tokens_cache_lectura = models.PositiveIntegerField(default=0)
    coste_eur = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    latencia_ms = models.PositiveIntegerField()
    razon_finalizacion = models.CharField(max_length=32, blank=True)
    error = models.CharField(max_length=200, blank=True)
    intento = models.PositiveSmallIntegerField()

    class Meta:
        db_table = "llamadas_llm"
        ordering = ["-creada_el"]
        indexes = [models.Index(fields=["usuario", "creada_el"])]
```

```python
# apps/evaluacion/models.py — paso 23
from django.db import models


class CasoEvaluacion(models.Model):
    """Índice del conjunto dorado, que vive en evaluacion/casos/*.json."""

    id = models.CharField(max_length=60, primary_key=True)
    descripcion = models.CharField(max_length=200)
    entrada = models.JSONField()
    propiedades_esperadas = models.JSONField()
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "casos_evaluacion"
        ordering = ["id"]


class EjecucionEvaluacion(models.Model):
    ejecutada_el = models.DateTimeField(auto_now_add=True, db_index=True)
    sha_commit = models.CharField(max_length=40)
    modelo = models.CharField(max_length=80)
    prompt_version = models.CharField(max_length=40)
    casos_totales = models.PositiveIntegerField()
    casos_acertados = models.PositiveIntegerField()
    tasa_acierto = models.FloatField()
    coste_total_eur = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    latencia_p50_ms = models.PositiveIntegerField()
    latencia_p95_ms = models.PositiveIntegerField()
    es_linea_base = models.BooleanField(default=False)
    detalle = models.JSONField()

    class Meta:
        db_table = "ejecuciones_evaluacion"
        ordering = ["-ejecutada_el"]
```

### 4.5 Migraciones

Herramienta: las migraciones propias de Django. **Nunca se escribe una migración a mano y nunca se
inventa su nombre de fichero**: se generan con `uv run python manage.py makemigrations <app>` y se
aplican con `uv run python manage.py migrate`. Este documento se refiere siempre a *"la migración que
emite `makemigrations`"* y verifica por efecto:

- `uv run python manage.py makemigrations --check --dry-run` sale **0** si no queda ningún cambio de
  modelo sin migrar, y **1** si queda. El gate exige 0.
- `uv run python manage.py migrate --check` sale **0** si la base de datos está al día.

**Orden obligatorio y con una sola oportunidad:** `apps.cuentas` y su `AUTH_USER_MODEL` se migran
**los primeros**, en el paso 4, antes de que exista ninguna tabla con clave foránea al usuario. No es
una preferencia de estilo: Django no puede reescribir `AUTH_USER_MODEL` sobre un esquema ya migrado sin
una intervención manual de varios días.

Regla para toda migración futura: expandir y luego contraer. Nunca una migración destructiva en el
mismo commit que el cambio de código que la necesita.

### 4.6 Datos de arranque

Una base de datos recién creada necesita **exactamente una cosa**: una cuenta de administrador con la
que entrar al panel. Se crea sin interacción con
`uv run python manage.py createsuperuser --noinput`, que lee `DJANGO_SUPERUSER_USERNAME`,
`DJANGO_SUPERUSER_EMAIL` y `DJANGO_SUPERUSER_PASSWORD` del entorno (§10). No hay ningún otro dato de
arranque, y el resto de "datos de referencia" de este sistema **no viven en la base de datos**, viven en
el repositorio y se versionan con él:

| Dato de referencia | Dónde vive | Cómo entra en la base de datos |
|---|---|---|
| Dataset de comparables | `tp_domain/comparables.json` | No entra: el motor lo lee del fichero |
| Registro cerrado de fuentes citables | `tp_domain/sources.py` | No entra: el motor lo lee del módulo |
| Corpus de investigación | `documentation/tax-research/**.md` | `uv run python manage.py reindexar_corpus` reconstruye `Ficha` |
| Conjunto dorado de evaluación | `evaluacion/casos/*.json` | `uv run python manage.py reindexar_evaluacion` reconstruye `CasoEvaluacion` |

Los dos comandos de reindexado son **idempotentes y destructivos hacia su propia tabla**: vacían y
reconstruyen. Es lo que permite decir sin ambigüedad cuál es la fuente de verdad.

---

## 5. Diseño de la superficie HTTP

Esta aplicación no expone una API JSON —eso es un No-Goal de §1—. Su superficie HTTP son páginas
renderizadas en el servidor, y esta sección es su contrato.

### Convenciones

- **Ruta base:** `/`. No hay prefijo de versión: no hay cliente externo al que versionar nada.
- **Forma de la respuesta:** HTML renderizado en el servidor. Toda página extiende `templates/base.html`.
- **Sesión exigida por omisión.** El middleware `apps.comun.middleware.ExigirAutenticacion` (§8, paso 5)
  cierra **todo** salvo una lista blanca explícita: `/entrar/`, los ficheros estáticos y las páginas de
  error. La orientación del valor por defecto es deliberada: olvidar un decorador dejaría una vista
  abierta, olvidar añadir una ruta a la lista blanca la deja cerrada, que es el fallo seguro.
- **Códigos de estado**, enumerados y sin excepciones:

| Código | Cuándo | Cuerpo |
|---|---|---|
| `200` | La página se sirve | La plantilla correspondiente |
| `302` | Un POST válido ha creado algo, o una petición anónima llega a una ruta cerrada | `Location` al recurso creado, o a `/entrar/` con la ruta original en `next` |
| `400` | La ruta de una ficha se sale del corpus | `400.html` |
| `403` | Falta o no valida el token CSRF | `403.html` |
| `404` | El recurso no existe **o no es de quien lo pide** | `404.html` — ver la nota sobre 404 frente a 403, abajo |
| `405` | Método no permitido: un `GET` a `/salir/` o a una ruta de borrado | `405.html` |
| `422` | Un formulario se ha enviado y **no** valida (creación de caso, acceso, cambio de contraseña) | La misma plantilla con los errores. **Deliberadamente 422 y no el 200 habitual de Django**: un estado distinto hace que "el formulario ha rechazado la entrada" sea comprobable por una máquina, y §9 lo usa como criterio de aceptación |
| `500` | Error no controlado | `500.html`, sin traza |

- **404 y nunca 403 para un recurso ajeno.** Pedir el caso de otro usuario devuelve `404`, exactamente
  igual que pedir un identificador que no existe en ninguna tabla. Un `403` confirmaría que ese
  identificador existe, y con eso se enumera la base de datos de otro sin ver ni una fila. El `403`
  queda reservado a un único motivo: el token CSRF. La regla la impone la guarda única de §8, no cada
  vista por su cuenta.
- **Validación:** `django.forms` para la forma de la entrada; `tp_domain.models.Transaction` de pydantic
  para las invariantes del dominio. El formulario construye el `Transaction` dentro de su `clean()` y
  convierte el `ValidationError` de pydantic en errores de formulario, de modo que **el usuario ve un
  único conjunto de errores** y no dos validaciones en cascada con mensajes distintos.
- **Paginación:** solo en `/casos/`. Cursor no, desplazamiento sí (`?pagina=`), porque la tabla es
  pequeña y el usuario quiere saltar a la última página. **El tamaño de página lo decide el servidor**:
  `?por_pagina=` se acepta y se recorta a un máximo de **100**; el valor por defecto es **20**; un
  valor no numérico cae al valor por defecto sin error. Un cliente no puede pedir la tabla entera.
- **Idempotencia:** `GET` es puro. `POST /casos/` **no** es idempotente por diseño: dos envíos iguales
  crean dos casos, porque son dos análisis, cada uno con su marca de tiempo y su propia redacción de
  IA. La restricción única parcial de §4 impide que dos casos **vivos** del mismo usuario compartan
  título, así que el formulario desambigua antes de guardar.
- **Límites de petición:** ninguno por IP —un usuario, en local—. El único consumo que puede
  dispararse es el de tokens, y lo acota el tope mensual por cuenta de §17, comprobado **antes** de
  cada llamada al proveedor (paso 16).

### Rutas

| Método | Ruta | Qué hace | Sesión | Notas |
|---|---|---|---|---|
| `GET` | `/entrar/` | Formulario de acceso | **No** | Única ruta de la lista blanca junto a estáticos y errores |
| `POST` | `/entrar/` | Autentica y redirige | **No** | `422` con mensaje **genérico e idéntico** para usuario inexistente, contraseña incorrecta y cuenta inactiva |
| `POST` | `/salir/` | Cierra la sesión | Sí | **Solo POST.** Un `GET` responde `405`, para que nadie cierre la sesión de otro con un enlace o una imagen |
| `GET` | `/cuenta/contrasena/` | Formulario de cambio de contraseña | Sí | — |
| `POST` | `/cuenta/contrasena/` | Cambia la contraseña | Sí | Rota la clave de sesión: la cookie anterior deja de autenticar |
| `GET` | `/` | Formulario de operación vacío | Sí | Lleva el aviso de privacidad junto al formulario (§8, paso 25) |
| `POST` | `/casos/` | Valida, ejecuta el motor, comprueba cuota, persiste y redirige | Sí | `302` al detalle · `422` si no valida |
| `GET` | `/casos/` | Listado del usuario: búsqueda, filtro, orden, vacíos y paginación | Sí | Solo sus casos vivos. Tope de página en servidor |
| `GET` | `/casos/<uuid:pk>/` | El resultado completo | Sí | **Propietario**; si no, `404` |
| `GET` | `/casos/<uuid:pk>/informe.pdf` | Descarga el PDF regenerado desde el caso persistido | Sí | **Propietario**; si no, `404` |
| `POST` | `/casos/<uuid:pk>/borrar/` | Borrado **suave**: pone `deleted_at` | Sí | **Propietario**; si no, `404`. Un `GET` responde `405` |
| `GET` | `/contrastados/` | Biblioteca de precedentes publicados | Sí | Visible para **toda** cuenta autenticada, no solo para quien curó |
| `GET` | `/contrastados/<slug>/` | Un precedente | Sí | `404` si no está publicado y quien pide no es administrador |
| `GET` | `/fuentes/` | Índice del corpus, filtrable por jurisdicción | Sí | Se sirve desde la tabla `Ficha` (paso 19) |
| `GET` | `/fuentes/<path:ruta>/` | Una ficha renderizada desde su Markdown | Sí | `400` si la ruta se sale del corpus · `404` si no existe |
| `GET` | `/estudio/` | Índice de unidades de estudio publicadas, en su orden | Sí | **Nunca** aparece en un informe: es material didáctico, no fuente citable (§4) |
| `GET` | `/estudio/<slug>/` | Una unidad de estudio | Sí | `404` si `publicada=False` |
| `GET` | `/privacidad/` | El detalle del aviso: qué se guarda, dónde, cuánto y cómo se borra | Sí | Enlazada desde el pie de toda página (§8, paso 25) |
| — | `/admin/**` | Panel de administración de Django | Sí, **y `is_staff`** | Lo impone el propio panel. Alta y baja de cuentas, curación de precedentes, redacción de unidades de estudio, consulta de `LlamadaLLM` y de las ejecuciones del arnés |

### Puntos críticos — detalle completo

#### `POST /entrar/`

**Entrada:** `username`, `password`, `csrfmiddlewaretoken`, y opcionalmente `next`.

**Salida correcta:** `302`. El destino es `next` **si y solo si apunta a una ruta local**; en cualquier
otro caso, `/casos/`. Un `next` hacia un dominio externo se descarta en silencio: aceptarlo sería una
redirección abierta, que convierte esta pantalla en un trampolín de suplantación.

**Casos de error:** los tres —usuario inexistente, contraseña incorrecta, cuenta con `is_active=False`—
responden `422` con **el mismo texto**: *"Usuario o contraseña incorrectos"*. Distinguirlos revelaría
qué cuentas existen y cuáles están desactivadas. No hay bloqueo por intentos en la v1; el sistema
escucha en `127.0.0.1` (§14).

#### `POST /casos/`

**Entrada** (`application/x-www-form-urlencoded`, con `csrfmiddlewaretoken`):

| Campo | Tipo | Reglas |
|---|---|---|
| `titulo` | texto | Opcional. Si llega vacío se deriva de `description`, recortado a 160 caracteres |
| `description` | texto | Obligatorio, longitud mínima 1 |
| `payer_country` | texto | Exactamente 2 caracteres; se normaliza a mayúsculas |
| `recipient_country` | texto | Exactamente 2 caracteres; se normaliza a mayúsculas; **distinto de `payer_country`** |
| `transaction_type` | elección | Solo los valores de `SUPPORTED_TRANSACTION_TYPES`; hoy, solo `royalty` |
| `industry` | elección | `pharmaceutical` \| `software` \| `manufacturing` |
| `amount_eur` | decimal | `> 0` |
| `rate_percent` | decimal | `0 <= x <= 100` |
| `effective_date` | fecha | Obligatoria, sin valor por defecto. **No existe un análisis "de hoy"**: la ventana de comparables (2 años) se cuenta desde esta fecha |

**Salida correcta:** `302` a `/casos/<uuid>/`. Efectos secundarios: se crea exactamente una fila en
`casos`, con `usuario` puesto al solicitante; **se comprueba la cuota mensual antes de cualquier
llamada al proveedor** (§17, paso 16) y, si hay margen y hay clave y modelo configurados, se hace una
llamada —dos como mucho, si el primer borrador se rechaza— y se escribe una fila en `llamadas_llm` con
el uso reportado por el proveedor; se emiten eventos de `structlog` con el id del caso, el usuario, las
dos jurisdicciones y si la capa de IA produjo texto.

**Casos de error:**

| Situación | Código | Qué se ve |
|---|---|---|
| Cualquier campo inválido | `422` | El formulario reenviado **con todos los valores ya introducidos**, y los errores junto a cada campo |
| Las dos jurisdicciones coinciden | `422` | Error no asociado a campo: *"Una operación vinculada transfronteriza requiere dos jurisdicciones distintas."* (mensaje del dominio, no reescrito) |
| Tipo de operación no soportado | `422` | El mensaje del dominio, que ya nombra los tipos soportados |
| Falta el token CSRF | `403` | `403.html` |
| Petición anónima | `302` | A `/entrar/`, con `next=/` |
| El motor no encuentra ni un comparable | `302` — **no es un error** | El caso se crea igual, con `BenchmarkRange` vacío y un `RiskFactor` de código `no_comparables`. Un rango que no se puede calcular es un resultado, no un fallo |
| Cuota mensual agotada | `302` — **no es un error** | El caso se crea **sin** explicación de IA, sin ninguna llamada al proveedor y sin ninguna fila en `llamadas_llm`. El tope desactiva la sección de IA; nunca bloquea el producto |
| La capa de IA falla, no hay clave o el borrador no valida | `302` — **no es un error** | El caso se crea sin `ai_explanation`. La sección del informe declara su ausencia en vez de dejar un hueco |

#### `GET /casos/`

**Parámetros:** `?q=` (texto sobre el título, insensible a mayúsculas), `?jurisdiccion=`, `?orden=`
(`fecha` o `titulo`), `?pagina=`, `?por_pagina=`.

La consulta **siempre** filtra por `usuario` antes que por nada más —lo hace `apps/comun/consultas.py`,
donde el propietario no es un parámetro opcional— y excluye los casos con `deleted_at`. Dos estados
vacíos distintos, y la distinción importa: *"todavía no has analizado ninguna operación"* cuando el
usuario no tiene casos, frente a *"ningún caso coincide con esta búsqueda"* más un enlace que limpia el
filtro cuando sí los tiene pero el filtro no casa. `?por_pagina=100000` devuelve como mucho 100 filas;
`?por_pagina=abc` o una página más allá de la última responden `200`, nunca `500`.

#### `GET /casos/<uuid:pk>/informe.pdf`

Obtiene el caso **a través de la guarda de §8**, lo rehidrata con
`AnalysisResult.model_validate(obj.payload)`, llama a `infrastructure.report.render_report_bytes` y
responde `200` con `Content-Type: application/pdf` y
`Content-Disposition: attachment; filename="tpip-<uuid>.pdf"`. **No llama a ninguna API** —el informe se
genera sin red, propiedad que ya cubre
`tests/report/test_pdf_report.py::test_report_is_generated_without_any_api_call`—. Si el `pk` no existe
**o no es del solicitante**, `404`, sin distinguir los dos casos.

#### `GET /fuentes/<path:ruta>/`

`ruta` es la ruta relativa de la ficha dentro de `documentation/tax-research/`, sin extensión (por
ejemplo `jurisdictions/spain/art18-lis-operaciones-vinculadas`). `apps/corpus/indexador.py` **resuelve
la ruta absoluta y comprueba que sigue estando dentro del directorio del corpus**; cualquier `..`, ruta
absoluta o enlace que se salga responde `400` y no lee nada. Si la ficha no existe, `404`. Si existe,
`200` con la cabecera servida desde la fila de `Ficha` —título, rango normativo, cita, pinpoint,
localizador, confianza y fecha de verificación— y el cuerpo Markdown renderizado a HTML.

---

## 6. Arquitectura de la interfaz

### Rutas y su origen de datos

| Ruta | Página | Origen de datos | Sesión |
|---|---|---|---|
| `/entrar/` | Acceso | Ninguno: formulario vacío | **No** |
| `/` | Formulario de operación | Ninguno: formulario vacío | Sí |
| `/casos/` | Listado del usuario | `apps/comun/consultas.py::casos_de(usuario, …)`, paginado en el servidor | Sí |
| `/casos/<uuid>/` | Resultado | La guarda `caso_del_usuario()`, rehidratada a `AnalysisResult` | Sí |
| `/casos/<uuid>/informe.pdf` | Descarga | Lo mismo, pasado por `render_report_bytes` | Sí |
| `/contrastados/` | Precedentes publicados | `CasoContrastado.objects.filter(publicado=True)` | Sí |
| `/contrastados/<slug>/` | Un precedente | Su `payload` congelado, rehidratado igual que un caso | Sí |
| `/fuentes/` | Índice del corpus | La tabla `Ficha`, filtrable por jurisdicción | Sí |
| `/fuentes/<path:ruta>/` | Ficha | Cabecera desde `Ficha`; cuerpo leído y renderizado del `.md` | Sí |
| `/estudio/` | Itinerario de estudio | `UnidadEstudio.objects.filter(publicada=True)`, por `orden` | Sí |
| `/estudio/<slug>/` | Unidad de estudio | Su `cuerpo` Markdown, más los enlaces a las fichas que estudia | Sí |
| `/privacidad/` | Aviso de privacidad | Estática | Sí |
| `/cuenta/contrasena/` | Cambio de contraseña | Ninguno | Sí |
| `/admin/**` | Panel de administración | Todos los modelos de §4 | Sí, y `is_staff` |

### Estrategia de renderizado

**Todo se renderiza en el servidor, en la petición.** No hay generación estática, no hay revalidación,
no hay caché de página. El motivo es que casi nada se puede cachear: cada resultado es único por UUID y
cada listado depende de quién lo pide.

La única excepción es el cuerpo de las fichas y de las unidades de estudio, que sí es estable —y aun
así no se cachea en la v1: son diez ficheros y unas pocas filas, y la fila de `Ficha` ya evita releer
el disco para la cabecera del índice. Introducir una caché aquí añadiría una vía de invalidación que
hoy no compensa.

No hay JavaScript propio. Ni un fichero `.js` en `static/`. La interacción del formulario es la nativa
del navegador; la búsqueda y el filtro del listado son un `<form method="get">`; el cierre de sesión y
el borrado son formularios `POST` con su token. El gráfico del rango es SVG generado en el servidor por
`infrastructure/charts.py` — el mismo módulo que ya alimentaba la interfaz anterior, y que comparte
geometría con el gráfico del PDF a través de `theme.range_geometry`.

### Jerarquía de plantillas

```
base.html                              (servidor)
├── enlace "Saltar al contenido"       -> #contenido
├── <header>                           marca · navegación (Casos · Precedentes · Fuentes ·
│                                      Estudio) · formulario POST de salida
├── <main id="contenido">  {% block contenido %}
└── <footer role="contentinfo">
    ├── aviso permanente de datos sintéticos
    └── AVISO DE PRIVACIDAD + enlace a /privacidad/        (§8, paso 25)

cuentas/entrar.html                    (extiende base.html, sin la navegación de sesión)
├── <h1>
├── <form method="post"> con {% csrf_token %} y el next oculto
├── errores en un contenedor role="alert" — texto ÚNICO y genérico para los tres casos
└── nota: "si has olvidado la contraseña, pídesela al administrador" — no hay enlace muerto

analisis/form.html                     (extiende base.html)
├── <h1>
├── el aviso de privacidad, ANTES del formulario: el usuario está a punto de escribir el dato
├── <form method="post"> con {% csrf_token %}
├── errores no asociados a campo, en role="alert"
└── un <label for> por campo, y el error del campo junto a él

analisis/lista.html                    (extiende base.html)
├── <h1>
├── <form method="get">                búsqueda por título · filtro por jurisdicción · orden
├── tabla de casos: título, fecha, jurisdicciones, posición en el rango, acciones
├── DOS estados vacíos distintos       "aún no has analizado nada" / "ningún caso coincide"
└── paginación                         tope de página impuesto por el servidor

analisis/detalle.html                  (extiende base.html)
├── <h1> la operación analizada
├── partials/_benchmark.html           EL PROTAGONISTA: el SVG del rango a ancho completo,
│                                      con role="img" y un <title> que dice lo mismo en texto
├── resumen: posición, nivel de defendibilidad, puntuación
├── partials/_jurisdictions.html       una tarjeta por JurisdictionAssessment
├── partials/_risk_factors.html        una fila por RiskFactor, con su severidad
├── fuentes citadas                    cada una enlaza a su ficha en /fuentes/…
├── sección de IA                      o la declaración explícita de su ausencia
├── botón de descarga del informe
└── formulario POST de borrado suave

analisis/contrastado.html              reutiliza los tres parciales de arriba: un precedente
                                       se lee igual que un caso, más el comentario del curador
corpus/ficha.html                      cabecera desde Ficha + cuerpo Markdown
estudio/unidad.html                    cuerpo Markdown + enlaces a las fichas que estudia
privacidad.html                        qué se guarda, dónde, cuánto y cómo se pide el borrado
```

### Gestión de estado

No hay estado de cliente: ni un fichero `.js`, ni nada guardado en el navegador. **El único estado del
lado del cliente es la cookie de sesión**, que el navegador envía sola y que el script de la página no
puede leer porque es `HttpOnly` (§8). Todo lo demás es estado del servidor: las ocho tablas de §4, a
las que se llega por URL y, cuando tienen propietario, siempre a través de la guarda de §8.

El estado de la búsqueda del listado vive **en la URL**, no en una sesión ni en una cookie: `?q=`,
`?jurisdiccion=`, `?orden=` y `?pagina=`. Así un listado filtrado se puede guardar en marcadores y
compartir con uno mismo, y recargar no pierde el filtro. Guardarlo en la sesión habría hecho que la
misma URL enseñara cosas distintas según lo último que se hubiera pulsado.

Lo que **deliberadamente no** se guarda en ningún estado global: el `AnalysisResult` rehidratado. Se
reconstruye en cada petición desde `payload`. Es una validación de pydantic sobre un diccionario, y
tenerlo en caché ahorraría microsegundos a cambio de una fuente de incoherencia.

### Estados de carga, vacío y error

| Superficie | Cargando | Vacío | Error |
|---|---|---|---|
| Acceso `/entrar/` | No aplica | Es su estado inicial | Un solo mensaje genérico en `role="alert"`, idéntico para usuario inexistente, contraseña incorrecta y cuenta inactiva |
| Formulario `/` | No aplica: renderizado en el servidor, sin peticiones asíncronas | Es su estado inicial | Errores junto a cada campo, más un bloque `role="alert"` para los que no pertenecen a ningún campo. **El formulario se reenvía con todos los valores ya introducidos** |
| Listado `/casos/` | No aplica | **Dos estados distintos**: *"todavía no has analizado ninguna operación"*, con un enlace al formulario; y *"ningún caso coincide con esta búsqueda"*, con un enlace que limpia el filtro. Confundirlos haría que un filtro mal escrito pareciera una base de datos vacía | Una página más allá de la última o un `?por_pagina=` no numérico caen al valor por defecto y responden `200`, nunca `500` |
| Detalle — gráfico del rango | No aplica | **Sin comparables aceptados**: no se dibuja el SVG (`range_geometry` devuelve `None`); en su lugar, un bloque que dice que no se ha podido calcular un rango y remite al factor de riesgo `no_comparables`. Dibujar un rango vacío sería peor que no dibujar nada | Si el SVG no se puede generar, la página se sirve igual sin él |
| Detalle — factores de riesgo | No aplica | Lista vacía: *"Sin factores de riesgo registrados"*, no un hueco | — |
| Detalle — comparables rechazados | No aplica | Lista vacía: *"Ningún comparable ha sido descartado"* | — |
| Detalle — sección de IA | La llamada es síncrona y ocurre antes del redirect: cuando la página se pinta, ya está resuelta | **Sin explicación**: se declara la ausencia, nunca se deja un hueco. Vale igual si faltó la clave, faltó el modelo, se agotó la cuota, falló la API o el borrador no pasó el validador | Idéntico al vacío: la capa de IA no propaga errores hacia arriba |
| Precedentes `/contrastados/` | No aplica | *"Todavía no hay precedentes publicados"* | Slug no publicado: `404` |
| Corpus `/fuentes/` | No aplica | Corpus sin ficheros: *"No hay fichas publicadas"* — señal de que falta ejecutar `reindexar_corpus` | Ficha inexistente: `404`; ruta fuera del corpus: `400` |
| Estudio `/estudio/` | No aplica | *"Todavía no hay unidades publicadas"* | Unidad en borrador: `404` |

---

## 7. Sistema de diseño

Todos los valores son literales. La paleta sale de `infrastructure/theme.py`, que ya existe y ya
alimenta el PDF; **el paso 9 la amplía con las superficies que hoy le faltan, sin renombrar ni
eliminar ninguna clave existente** —añadir es seguro, renombrar rompería las 38 pruebas de informe—.
`static/css/tokens.css` se genera desde ese diccionario, de modo que pantalla e informe no pueden
divergir sin que un gate lo diga.

### Colores

| Token | Pantalla (oscuro) | Informe (claro) | Uso |
|---|---|---|---|
| `--tpip-ink` | `#E8EDF4` | `#1A1A1A` | Texto principal |
| `--tpip-muted` | `#94A3B8` | `#5A5A5A` | Texto secundario, pies de tabla, metadatos |
| `--tpip-rule` | `#253044` | `#C8C8C8` | Separadores y filetes |
| `--tpip-background` | `#0F172A` | `#FFFFFF` | Fondo de página |
| `--tpip-surface` | `#161F33` | `#F7F8FA` | Tarjetas y paneles |
| `--tpip-surface-sunken` | `#1B2438` | `#EBEEF3` | Cabeceras de tabla y zonas hundidas |
| `--tpip-border-strong` | `#65758F` | `#767676` | Borde de controles interactivos |
| `--tpip-focus` | `#7EB3E0` | `#1F4E79` | Anillo de foco y enlaces |
| `--tpip-accent` | `#F59E0B` | `#B45309` | **Atención aquí**: ajuste obligatorio, tipo fuera de rango, conclusión |
| `--tpip-band-outer` | `#2C3E52` | `#DCE3EC` | Relleno decorativo de la banda P10–P90 |
| `--tpip-band-inner` | `#4A7CA8` | `#9FB3C8` | Relleno decorativo de la banda intercuartílica |
| `--tpip-median` | `#7EB3E0` | `#334E68` | Marca de la mediana y del tipo analizado |
| `--tpip-ok` | `#3DD68C` | `#2E6B4F` | Defendible |
| `--tpip-warn` | `#A8B4C4` | `#8A6D1F` | Moderado |
| `--tpip-risk` | `#F26D6D` | `#8C2F2F` | Riesgo alto, errores, destructivo |

**Dos superficies, un mismo vocabulario.** Los nombres significan lo mismo en ambas y solo cambian los
hexadecimales: la coherencia entre pantalla e informe vive en los **significados**, no en los valores.
El motivo es que el papel es blanco — un informe fiscal con fondo negro no se imprime ni se presenta
ante nadie —, mientras que la pantalla se pidió oscura de forma explícita.

**El ámbar sale de la escala de veredicto.** Con verde-ámbar-rojo, el ámbar significaría dos cosas a
la vez —"moderado" y "mira aquí"— y dejaría de comunicar. `--tpip-warn` pasa a gris neutro, que además
es más honesto: moderado quiere decir que no hay señal fuerte en ninguna dirección. El ámbar queda
reservado en exclusiva a `--tpip-accent`, y por eso funciona: es el único color vivo de la interfaz.

**Contrastes de la pantalla, medidos** sobre el fondo `#0F172A` y sobre la tarjeta `#161F33`:
`ink` 15,18 · `muted` 6,96 / 6,41 · `accent` 8,31 / 7,65 · `ok` 9,52 · `warn` 8,49 · `risk` 6,11 ·
`median` y `focus` 8,00 · `border_strong` **3,82 / 3,52** (umbral 3:1 para límites de componente; era
el único par que no pasaba con el valor inicial y por eso se aclaró).

**Contraste — WCAG 2.2 AA.** Los tres pares con menos margen, medidos:

| Par | Ratio | Umbral | Veredicto |
|---|---|---|---|
| `--tpip-muted` `#5A5A5A` sobre `--tpip-surface` `#F7F8FA` | **6,49:1** | 4,5:1 (texto normal) | Pasa |
| `--tpip-warn` `#8A6D1F` sobre `--tpip-background` `#FFFFFF` | **4,90:1** | 4,5:1 | Pasa, con poco margen. Cualquier aclarado de este token lo rompe |
| `--tpip-border-strong` `#767676` sobre `--tpip-background` `#FFFFFF` | **4,54:1** | 3:1 (límites de componentes) | Pasa |

Para referencia: `--tpip-ink` sobre blanco da 17,4:1 y sobre `--tpip-surface` 16,4:1; `--tpip-focus`
sobre blanco, 8,66:1; `--tpip-ok`, 6,30:1; `--tpip-risk`, 8,19:1; `--tpip-median`, 8,64:1.

**`--tpip-band-inner` y `--tpip-band-outer` son rellenos decorativos, nunca límites de componente ni
fondo de texto.** `#9FB3C8` sobre blanco da 2,15:1 y no alcanzaría el 3:1 que exige un límite. El
límite del gráfico lo dan `--tpip-median` y `--tpip-rule`, y ningún texto se imprime sobre las bandas.

### Tipografía

Sin fuentes web: ni CDN ni auto-hospedadas. Una descarga de fuente es una dependencia de red en una
aplicación que funciona sin red, y el PDF usa las fuentes base de PDF de todos modos.

| Papel | Familia | Tamaño / interlineado | Peso | Espaciado |
|---|---|---|---|---|
| Display | `-apple-system, "Segoe UI", Roboto, system-ui, sans-serif` | `2rem` / `1.2` | 600 | `-0.01em` |
| Encabezado | igual | `1.375rem` / `1.3` | 600 | `0` |
| Subencabezado | igual | `1.0625rem` / `1.4` | 600 | `0` |
| Cuerpo | igual | `1rem` / `1.6` | 400 | `0` |
| Secundario | igual | `0.875rem` / `1.5` | 400 | `0` |
| Monoespaciado | `"Cascadia Mono", Consolas, "SF Mono", monospace` | `0.875rem` / `1.5` | 400 | `0` |

`font-display` no aplica —no hay `@font-face`—. La pila arranca por la fuente del sistema, que en
Windows 10 es Segoe UI.

### Espaciado, radio y elevación

- Escala de espaciado, base `4px`: `4 · 8 · 12 · 16 · 24 · 32 · 48 · 64`. Expuesta como
  `--tpip-space-1` … `--tpip-space-8`.
- Radio: `4px` en controles de formulario y botones; `8px` en tarjetas; `0` en tablas.
- Sombras: **ninguna**. Las superficies se separan por color de fondo y por `1px solid var(--tpip-rule)`.
  Es coherente con un documento impreso, que es lo que este producto acaba siendo.
- Ancho máximo de contenido: `72rem`. Puntos de ruptura: `40rem` (de una columna a dos) y `64rem`
  (tarjetas de jurisdicción en fila).

### Movimiento

| Interacción | Duración | Curva |
|---|---|---|
| Foco y `hover` en controles | `120ms` | `ease-out` |
| Aparición de los errores de formulario | Ninguna: llegan con la respuesta del servidor | — |

No hay más movimiento en el producto. Todo lo anterior va dentro de
`@media (prefers-reduced-motion: no-preference)`, de modo que la ausencia de movimiento es el estado
por defecto y la animación es la excepción que se activa.

### Estilo de componente

Sobrio a propósito: gris tinta sobre blanco, superficies apenas tintadas, filetes finos y tres
acentos desaturados reservados al veredicto. **El color solo aparece donde comunica algo** —el nivel de
defendibilidad, la severidad de un riesgo, la banda del rango—; nunca decora. Si un componente nuevo
necesita un color que no esté en la tabla de arriba, la respuesta correcta casi siempre es que no
necesita color. La referencia es el informe PDF que ya existe: si el componente no cabría en ese
documento sin desentonar, no pertenece a esta interfaz.

---

## 8. Autenticación y autorización

### Proveedor y razón

**`django.contrib.auth`, con un modelo de usuario propio (`cuentas.Usuario`) declarado en
`AUTH_USER_MODEL` desde la primera migración.** Sin proveedor externo, sin OAuth, sin servicio de
identidad de terceros: la aplicación tiene un puñado de cuentas que da de alta y de baja una persona
concreta, y añadir un proveedor de identidad sería introducir una dependencia de red, una cuenta más y
un flujo de recuperación para resolver un problema que aquí es una fila en una tabla.

`django.contrib.auth`, `django.contrib.admin`, `django.contrib.sessions`, `django.contrib.contenttypes`
y `django.contrib.messages` **entran en `INSTALLED_APPS`** desde el paso 1.

**Por qué el modelo propio va en el primer commit aunque la v1 empiece con un solo usuario.** Es la
decisión de este blueprint que menos se puede aplazar. Cambiar `AUTH_USER_MODEL` después de la
migración inicial no es una migración normal: toda tabla con una clave foránea al usuario apunta a una
tabla que deja de existir, y rehacerlo sobre un esquema vivo es trabajo de varios días con riesgo de
pérdida. **Una columna hoy cuesta una línea; la migración de mañana cuesta el proyecto.** El requisito
de partida —*"cuentas que yo puedo dar de alta o baja cuando quiera"*— no admite un esquema sin
propietario de fila.

**Y una aclaración que evita confundir dos argumentos distintos.** Es cierto que en un despliegue
local monousuario el marco de sesiones y roles no protege de nadie: nadie más llega a esa máquina. Pero
eso es un argumento sobre **la superficie de red**, no sobre **el modelo de datos**. `usuario_id` no
está en las tablas por seguridad perimetral; está porque *"de quién es esta fila"* tiene que tener
respuesta desde la primera fila que se escribe. Las dos cosas conviven en la v1: el esquema es
multiusuario desde el día uno y **el despliegue sigue siendo local, escuchando en `127.0.0.1`**
(§12, §14). Esa segunda parte se mantiene como decisión razonada, no se pierde.

### Flujos

- **Alta de una cuenta.** La hace un administrador desde el panel: `/admin/cuentas/usuario/add/`. No
  hay auto-registro, y no lo habrá mientras las cuentas las decida una persona. El administrador fija
  usuario, correo, contraseña y `tope_gasto_mensual_eur`.
- **Baja de una cuenta.** `is_active = False` desde el panel. **Nunca un `DELETE`**: las claves
  foráneas son `PROTECT` (§4) y un borrado real fallaría ruidosamente, que es justo lo que se quiere.
  Una cuenta inactiva no puede iniciar sesión, sus casos siguen existiendo y su gasto sigue imputado.
- **Inicio de sesión.** `GET /entrar/` muestra el formulario; `POST /entrar/` autentica. Credenciales
  incorrectas: se vuelve a mostrar el formulario con un error genérico —*"Usuario o contraseña
  incorrectos"*—, **el mismo mensaje para un usuario que no existe y para una contraseña equivocada**,
  porque distinguirlos revela qué cuentas existen.
- **Cuenta inactiva.** El mismo mensaje genérico. Que una cuenta esté desactivada tampoco es
  información que deba salir por el formulario de acceso.
- **Redirección tras entrar.** Al parámetro `next` si lo hay **y apunta a una ruta local**, y si no, al
  listado de casos. Un `next` hacia un dominio externo se descarta: es una redirección abierta.
- **Cierre de sesión.** `POST /salir/` — **POST y no GET**, para que no se pueda cerrar la sesión de
  alguien con un enlace o una imagen.
- **Cambio de contraseña.** `GET`/`POST /cuenta/contrasena/`, con la contraseña actual. Al cambiarla se
  renueva la sesión.
- **Recuperación de contraseña por correo: NO se implementa en la v1.** Exigiría un servidor de correo
  saliente, que es un No-Goal de §1. La ruta de recuperación es que el administrador la restablezca
  desde el panel, y así se dice en la propia pantalla de acceso en vez de dejar un enlace muerto.
- **Caducidad de la sesión.** A las 12 horas, y con `SESSION_EXPIRE_AT_BROWSER_CLOSE = True`. Al
  caducar, cualquier navegación lleva a `/entrar/` con `next` puesto.

### Protección de rutas

| Superficie | Regla | Dónde se aplica |
|---|---|---|
| `/entrar/` | pública | `apps/cuentas/views.py` |
| `/` (formulario de operación) | autenticada | `apps/analisis/views.py` |
| `/casos/`, `/casos/<uuid>/`, `/casos/<uuid>/informe.pdf` | autenticada **y propietaria** | `apps/analisis/views.py`, a través de la guarda |
| `/contrastados/`, `/contrastados/<slug>/` | autenticada — visible para todas las cuentas | `apps/analisis/views.py` |
| `/fuentes/`, `/fuentes/<path:ruta>/` | autenticada | `apps/corpus/views.py` |
| `/estudio/`, `/estudio/<slug>/` | autenticada | `apps/estudio/views.py` |
| `/cuenta/contrasena/` | autenticada | `apps/cuentas/views.py` |
| `/admin/**` | `is_staff` — lo impone el propio panel de Django | `django.contrib.admin` |

**Regla de aplicación:** la autorización se comprueba **en el servidor, en cada petición**. Las guardas
de plantilla son cosméticas y jamás la única comprobación. Un botón oculto no es un permiso.

La comprobación de sesión no se escribe vista a vista: `config/settings/base.py` instala un middleware
propio, `apps.comun.middleware.ExigirAutenticacion`, que exige sesión en **todo** salvo una lista
explícita de rutas públicas (`/entrar/`, los estáticos, y las páginas de error). Es la orientación
correcta del valor por defecto: olvidar un decorador deja una vista abierta, olvidar añadir una ruta a
la lista blanca deja una vista cerrada. El fallo por omisión tiene que ser el seguro.

### La guarda de autorización, única y con nombre

Todo lector y todo escritor de una fila con propietario pasa por **una sola función**, en
`apps/comun/guardas.py`:

```python
def caso_del_usuario(usuario, pk):
    """Devuelve el Caso vivo de ESE usuario, o levanta Http404.

    404 y no 403, deliberadamente: un 403 confirmaría que el id existe y que
    pertenece a otro. El 404 no distingue "no existe" de "no es tuyo", que es
    exactamente la propiedad que se quiere."""
    return get_object_or_404(Caso, pk=pk, usuario=usuario)
```

**Una sola guarda, y no una condición repetida en cada vista.** Una comprobación duplicada en siete
sitios es una comprobación que tarde o temprano falta en el octavo, y ese octavo no da error: **devuelve
los datos de otro**. Al ser una función con nombre, se puede buscar quién la llama y quién no, y esa
búsqueda es un criterio de aceptación del paso 7.

**404 y no 403** es la decisión que hay que sostener aunque parezca menos informativa: un 403 sobre un
identificador ajeno confirma que ese identificador existe, y con eso se enumera la base de datos de otro
usuario sin ver ni una fila. Vale para `Caso`, para el informe PDF y para cualquier entidad con
`usuario_id` que se añada después.

### Roles y permisos

| Rol | Puede | No puede |
|---|---|---|
| **Usuario** (`is_active`, sin `is_staff`) | Crear casos; ver, buscar, listar y borrar en suave **los suyos**; descargar el informe de los suyos; leer el corpus, las unidades de estudio publicadas y los casos contrastados publicados; cambiar su contraseña | Ver, listar o descargar el caso de otro (recibe **404**); entrar en `/admin/`; publicar un caso contrastado; cambiar su propio tope de gasto |
| **Administrador** (`is_staff` + `is_superuser`) | Todo lo anterior, más: alta y baja de cuentas; fijar el tope de gasto de cada cuenta; curar y publicar `CasoContrastado`; escribir y publicar `UnidadEstudio`; consultar `LlamadaLLM` y `EjecucionEvaluacion`; **y ver los casos de todos los usuarios desde el panel** | Editar `Ficha` de forma persistente: el panel la muestra en solo lectura porque el siguiente reindexado la sobrescribiría |

No hay más roles. Un tercer rol —"revisor", "solo lectura"— es una función que hoy no tiene quien la
pida, y el sistema de permisos de Django ya está ahí el día que la tenga.

### Aviso de privacidad — obligatorio y visible

**El administrador ve los casos de todos los usuarios.** Eso es una consecuencia inevitable de tener un
panel de administración y de que alguien tenga que poder curar precedentes y auditar el gasto, pero
**no puede quedar implícito**: quien escribe una operación vinculada en este sistema tiene derecho a
saber, antes de escribirla, quién más la va a poder leer.

Por eso el aviso es un requisito con criterio de aceptación propio (paso 25), no una nota en un
`README`:

- Aparece en `templates/base.html`, dentro de un `<footer>` con `role="contentinfo"`, en **todas** las
  páginas autenticadas.
- Aparece **también** junto al formulario de creación de un caso, que es el momento en el que el
  usuario está a punto de escribir el dato.
- El texto es explícito y sin eufemismos: dice que las cuentas con permiso de administración pueden
  acceder a los casos de cualquier usuario, para qué (soporte, curación de precedentes y control de
  gasto), y qué queda registrado de cada llamada al modelo.
- Enlaza a `/privacidad/`, una página estática con el detalle: qué se guarda, dónde, durante cuánto
  tiempo, y cómo se pide el borrado.

### Sesiones

**La sesión viaja en una cookie, y nunca en un token guardado por el navegador.** Ni
`localStorage`, ni `sessionStorage`, ni un JWT en una cabecera puesta por JavaScript: cualquier cosa
que el JavaScript de la página pueda leer, la puede leer también un XSS. La cookie de sesión es
`HttpOnly`, de modo que el script de la página no la ve, y el navegador la envía sola sin que haya
código que la gestione. Este proyecto, además, **no tiene ni un fichero `.js`** (§6), así que un token
en el navegador exigiría escribir JavaScript solo para empeorar la seguridad.

| Aspecto | Valor |
|---|---|
| Tipo | Cookie de sesión de Django, con el estado respaldado en base de datos (`django.contrib.sessions.backends.db`) |
| Por qué no un token en el navegador | Un token en `localStorage` es legible por cualquier script inyectado y hay que gestionarlo a mano. La cookie `HttpOnly` no es legible por el script y la envía el propio navegador |
| Por qué no cookie firmada sin estado | Una sesión enteramente en cookie no se puede invalidar desde el servidor. Al dar de baja una cuenta, su sesión tiene que dejar de valer **inmediatamente**, y con la cookie firmada seguiría siendo válida hasta caducar |
| Duración | `SESSION_COOKIE_AGE = 43200` (12 horas) · `SESSION_EXPIRE_AT_BROWSER_CLOSE = True` |
| Renovación | `SESSION_SAVE_EVERY_REQUEST = False`: la sesión caduca 12 horas después de entrar, no de la última acción |
| Marcas de la cookie | `SESSION_COOKIE_HTTPONLY = True` · `SESSION_COOKIE_SAMESITE = "Lax"` · `SESSION_COOKIE_SECURE = True` **solo en producción** (en local no hay TLS y activarlo dejaría la aplicación inutilizable) |
| CSRF | `CsrfViewMiddleware` activo; `{% csrf_token %}` en todo formulario, incluidos `/entrar/` y `/salir/`. `CSRF_COOKIE_SECURE = True` en producción |
| Rotación | `django.contrib.auth` rota el identificador de sesión al iniciar sesión y al cambiar la contraseña. No se desactiva |
| Contraseñas | Los `AUTH_PASSWORD_VALIDATORS` por defecto de Django, los cuatro. El hasher por defecto de Django 5.2, sin tocar |

### Aislamiento por propietario

El mecanismo **no** es "acordarse de filtrar por `usuario_id`". Son tres piezas, y las tres se
comprueban:

1. **La columna existe y es `not null`** desde la primera migración de cada tabla con propietario (§4).
   Una fila sin dueño no se puede escribir.
2. **La guarda con nombre es el único camino de lectura.** El paso 7 la introduce con sus pruebas de
   aislamiento, y el criterio de aceptación es negativo además de positivo: **ninguna vista de
   `apps/analisis/` construye una consulta sobre `Caso` sin pasar por la guarda o sin filtrar por
   `request.user`**, y eso se comprueba buscándolo en el código.
3. **Las pruebas de aislamiento son parte del gate**, no de un plan de pruebas aparte: dos usuarios,
   un caso cada uno, y cada intento cruzado —ver, listar, descargar el informe, borrar— responde
   **404**. Están en `tests/web/test_aislamiento.py` y las ejecuta §20.1.

El panel de administración es la excepción explícita y consciente: usa `Caso.todos`, ve todas las filas,
y por eso existe el aviso de privacidad de arriba.

---

## 9. ORDEN DE CONSTRUCCIÓN

**Esta es la sección para la que existe el blueprint entero.** Todo lo anterior es contexto; esto es
el conjunto de instrucciones. Un constructor que siga §9 al pie de la letra y pare cuando cada gate se
ponga en verde entrega el proyecto.

### El entorno de ejecución de esta sección

**Windows 10, PowerShell, y todo a través de `uv run`.** Ningún comando de este documento asume bash,
`make`, ni un entorno virtual activado a mano: `uv run` resuelve el intérprete y el entorno en cada
invocación. Los bloques `Verify` se escriben en PowerShell y **cada bloque sale con 0 cuando el paso
es correcto**. La forma que se usa en todo el documento es siempre la misma, y es deliberada:

```powershell
<comando>
if ($LASTEXITCODE -ne 0) { throw '<qué se esperaba>' }    # expect: exit 0
```

Cuando lo correcto es que un comando falle con un código concreto, se afirma **ese código** y nunca
"distinto de cero" —un error de uso (argumento de más, opción desconocida, fichero ilegible) también
sale distinto de cero, y una comprobación escrita así pasaría en vacío y seguiría pasando después de
romperse lo que vigila:

```powershell
<comando>
if ($LASTEXITCODE -ne 1) { throw "se esperaba código 1, obtenido $LASTEXITCODE" }   # 1 = la propiedad; 2 = uso
```

No hay ningún fichero auxiliar de aserciones: cada bloque se basta solo y se puede pegar tal cual en
una consola abierta en la raíz del proyecto.

### Las reglas de un paso

1. **Un paso, una sentada.** Más de **5 ficheros** o más de **6 criterios de aceptación** significa
   que son dos pasos.
2. **Todo paso lleva los cuatro campos:** `Do`, `Done when`, `Verify`, `Checkpoint`. El `Checkpoint`
   es un bloque literal que hace commit y etiqueta: `git tag step-NN-<slug>`. Esa etiqueta es el punto
   de retorno del paso siguiente.
3. **Los criterios son observables y comprobables por máquina**, en forma EARS:
   **WHEN** `<disparador>` **THE SYSTEM SHALL** `<respuesta observable>`.
4. **"Se ve bien" está prohibido.** También *funciona*, *está implementado*, *renderiza
   correctamente*, *queda cableado*.
5. **`Verify` es PowerShell literal**, con el resultado esperado en un comentario.
6. **Un paso no está hecho hasta que pasan sus comprobaciones *y* siguen pasando las de los pasos
   anteriores.**
7. **Nunca se salta un paso.** Si el 7 está bloqueado, se para y se reporta.
8. **Un `Verify` no puede afirmar nada que produzca su propio `Checkpoint`.** El orden es
   Do → Done when → Verify → Checkpoint, siempre: cuando el `Verify` corre, los ficheros del paso
   están escritos pero **sin añadir al índice**, el árbol está sucio por el propio trabajo del paso y
   su etiqueta no existe. Por eso ningún `Verify` de este documento comprueba `git status --porcelain`,
   ni `git ls-files --error-unmatch` sobre un fichero que ese paso crea, ni su propia etiqueta. Lo que
   sí se comprueba es el **sistema de ficheros** (`Test-Path`), y las afirmaciones sobre estado de git
   viven en el bloque `Checkpoint`, después del commit que las hace ciertas, o en el gate de §20.1.
9. **Ningún paso introduce un requisito que rompa retroactivamente el gate de un paso anterior.** El
   caso canónico es la validación de variables de entorno: la columna *"Requerida a partir del paso"*
   de §10 es un contrato, y la configuración de este proyecto trata **todas** las variables como
   opcionales en desarrollo precisamente para que ningún paso obligue a inventar credenciales de un
   servicio que aún no se ha integrado.
10. **Ningún número derivado se escribe sin haberlo contado.** El único recuento que este documento
    afirma es **180**, contado el 2026-08-15 sobre el repositorio real
    (`tests/domain` 89 + `tests/ai` 53 + `tests/report` 38), y es una invariante de la migración, no
    una estimación: la suite rescatada tiene que salir del último paso con las mismas 180 pruebas con
    las que entró en el paso 3. Los pasos 8 y 9 son los únicos que la tocan, y lo hacen sustituyendo
    prueba por prueba. Todo lo demás se afirma como **propiedad** (`exit 0`, `0 failed`, `0 skipped`),
    no como recuento.

### Un paso, una unidad — la regla de recuento

> **Un paso de §9 = una tarea de `tasks.json` = un bloque de tarea en un fichero de epic.**

Este blueprint tiene **27 pasos**, luego tendrá 27 tareas en `tasks.json` y 27 bloques de tarea
repartidos entre sus epics. Con 27 pasos, el número legal de epics está entre `ceil(27/9) = 3` y
`floor(27/5) = 5`: **se emiten 4 epics** (7 + 7 + 7 + 6), partidos por frontera de capa —cimientos y
cuentas · rebanada vertical del análisis · contenido, gasto y evidencia · acabado y cierre—.

**Sobre el tamaño.** 27 pasos está por encima del rango orientativo de 10-18, y es consciente: este no
es un proyecto nuevo, es una migración de interfaz **más** siete funcionalidades de producto
confirmadas (cuentas, corpus indexado, casos buscables, biblioteca de precedentes, módulo de estudio,
control de gasto y arnés de evaluación). Ninguna se ha partido en pasos artificialmente pequeños: cada
uno respeta el tope de ~5 ficheros y ~6 criterios, y ese tope es el que fija el número. Comprimirlos
para caber en 18 produciría pasos que no caben en una sentada, que es exactamente donde fallan las
construcciones autónomas.

### Mapa de pasos

| # | Paso | Depende de | Toca | Gate |
|---|---|---|---|---|
| 1 | Esqueleto de Django ejecutable | — | `manage.py`, `config/` | `uv run python manage.py check` sale 0 |
| 2 | Configuración tipada y registro estructurado | 1 | `config/settings/`, `config/logging.py` | `pytest tests/web/test_settings.py` |
| 3 | Retirada de Streamlit y red de seguridad en verde | 2 | borra `ui/`, `requirements.txt` | `pytest tests/domain tests/ai tests/report` → 180 passed |
| 4 | Modelo de usuario propio, `AUTH_USER_MODEL` y panel de administración | 3 | `apps/cuentas/` | `migrate` sale 0 y `AUTH_USER_MODEL` es `cuentas.Usuario` |
| 5 | Acceso: entrar, salir, cambiar contraseña y cierre por omisión | 4 | `apps/cuentas/views.py`, `apps/comun/middleware.py` | `pytest tests/web/test_acceso.py` |
| 6 | Entidad `Caso`: propietario, título y borrado suave | 4 | `apps/analisis/models.py` | `makemigrations --check` sale 0 |
| 7 | Guarda de autorización única y aislamiento con 404 | 5, 6 | `apps/comun/guardas.py` | `pytest tests/web/test_aislamiento.py` |
| 8 | Defecto 1: el modelo de IA deja de resolverse solo | 3 | `ai/claude_client.py` | `pytest tests/ai` en verde, sin `models.list` |
| 9 | Defecto 2: paleta con superficies diferenciadas | 3 | `infrastructure/theme.py` | `pytest tests/report tests/domain` sigue en verde |
| 10 | Formulario de operación | 6 | `apps/analisis/forms.py` | `pytest tests/web/test_forms.py` |
| 11 | Vista de análisis: POST → motor → persistencia con propietario | 7, 10 | `apps/analisis/{services,views,urls}.py` | `pytest tests/web/test_analisis_view.py` |
| 12 | Plantilla base y plantilla de resultado | 11 | `templates/` | `pytest tests/web/test_result_template.py` |
| 13 | Tokens de diseño: `theme.py` → CSS | 9, 12 | `scripts/build_tokens.py`, `static/css/` | `python -m scripts.build_tokens --check` sale 0 |
| 14 | Descarga del informe PDF | 11, 13 | vista de informe | `pypdf` extrae `DATOS SINTÉTICOS` del PDF servido |
| 15 | Listado de casos: búsqueda, filtro, orden, vacío y paginación | 12, 14 | `apps/analisis/views.py`, `templates/analisis/lista.html` | `pytest tests/web/test_listado.py` |
| 16 | `LlamadaLLM` y tope de gasto comprobado **antes** de llamar | 6, 8 | `apps/ia/` | `pytest tests/web/test_cuota.py` |
| 17 | Capa de IA en la vista: degradación silenciosa y llamada registrada | 14, 16 | `apps/analisis/services.py` | `pytest tests/web/test_ia_degradacion.py` |
| 18 | Completar el frontmatter de las 9 fichas del corpus | 4 | `documentation/tax-research/**.md` | Las 9 fichas cumplen el contrato del índice |
| 19 | `Ficha`: índice citable del corpus, reconstruible desde los `.md` | 4, 18 | `apps/corpus/` | `reindexar_corpus` indexa las 9 fichas |
| 20 | Publicación del corpus y enlace desde las fuentes citadas | 12, 19 | `apps/corpus/views.py`, `templates/corpus/` | `pytest tests/web/test_corpus.py` |
| 21 | `UnidadEstudio`: módulo de estudio, separado de las fichas | 19, 20 | `apps/estudio/` | `pytest tests/web/test_estudio.py` |
| 22 | `CasoContrastado`: biblioteca curada de precedentes | 15 | `apps/analisis/models.py`, `admin.py` | `pytest tests/web/test_contrastados.py` |
| 23 | Arnés de evaluación: conjunto dorado, puntuadores y puerta de CI | 17 | `apps/evaluacion/`, `evaluacion/casos/` | `evaluar --contra-linea-base` sale 0, y 1 al bajar |
| 24 | Copia de seguridad y restauración verificada por recuento de filas | 6, 16, 19 | `apps/comun/management/commands/` | Restaurar en limpio y comparar recuentos |
| 25 | Accesibilidad de las plantillas y aviso de privacidad | 12, 20, 21 | `templates/`, `static/css/app.css` | `pytest tests/web/test_accesibilidad.py` |
| 26 | Seguridad, cabeceras y ajustes de producción | 25 | `config/settings/production.py` | `manage.py check --deploy` sale 0 |
| 27 | Integración continua, estáticos y cierre | 1–26 | `.github/workflows/ci.yml`, `README.md` | El gate completo de §20.1 |

**Por qué este orden.** Los tres primeros pasos ponen el gate más caro lo antes posible: el paso 1
produce un ejecutable y **lo ejecuta**, el paso 2 fija la configuración de la que todo depende y el
paso 3 pone la red de seguridad en verde bajo la cadena de herramientas nueva —que es donde se
descubre si `reportlab` fijado en §11 rompe el informe rescatado (§20.2, riesgo 2)—.

Los pasos 4 a 7 son cuentas y propiedad de fila, y van **antes que cualquier tabla de negocio** por una
razón que no admite reordenación: `AUTH_USER_MODEL` no se puede cambiar después de la migración
inicial, y `usuario_id` no se puede retrofitar sobre un esquema vivo sin reescribir la capa de datos
(§4, §8). Los dos defectos conocidos se corrigen en los pasos 8 y 9, antes de que nada nuevo dependa
de ellos: arreglar la paleta después de escribir el CSS obligaría a reescribir el CSS.

Del 10 al 15 se construye la rebanada vertical completa —formulario, motor, persistencia, pantalla,
PDF, listado— antes de ensanchar. **La capa de IA llega tarde a propósito** (16 y 17): es la única
parte del sistema que depende de un tercero, y todo lo que hay debajo tiene que estar verde antes de
introducir esa variable. El tope de gasto va **antes** que la llamada, no después, porque un freno que
se instala después de rodar no es un freno.

---

#### Paso 1 — Esqueleto de Django ejecutable

**Do**

Crear el proyecto de Django a mano, sin `django-admin startproject`, para controlar exactamente qué
entra. `INSTALLED_APPS` en este paso contiene, en este orden:
`django.contrib.admin`, `django.contrib.auth`, `django.contrib.contenttypes`,
`django.contrib.sessions`, `django.contrib.messages`, `django.contrib.staticfiles`. Las cinco primeras
entran porque este producto tiene cuentas y panel de administración (§8), y el panel es la razón por la
que se eligió Django: le da a un jurista no-ingeniero el alta y baja de cuentas y la curación de
contenido sin escribir código.

**No se ejecuta `migrate` en este paso.** La primera migración que se aplica al proyecto tiene que ser
la de `apps.cuentas` con `AUTH_USER_MODEL` ya declarado (paso 4); aplicar antes las tablas de `auth`
con el usuario por defecto es precisamente el estado del que Django no sabe salir.

Ficheros:

- `manage.py` — con la línea literal `os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")`.
  Ese literal es el mismo que ya declara `pyproject.toml` para pytest (§19.6); es un valor compartido
  entre dos artefactos y este paso es el primero en el que existen los dos.
- `config/__init__.py`, `config/settings/__init__.py`
- `config/settings/base.py` — `BASE_DIR`, `INSTALLED_APPS` como arriba, `MIDDLEWARE` con seguridad,
  común, sesiones, CSRF, autenticación y mensajes, `ROOT_URLCONF`, `TEMPLATES` con `templates/` y los
  procesadores de contexto de `auth` y `messages`, `DATABASES` con SQLite en `BASE_DIR / "db.sqlite3"`,
  `STATIC_URL`, `STATIC_ROOT = BASE_DIR / "staticfiles"`, `LANGUAGE_CODE = "es-es"`,
  `TIME_ZONE = "Europe/Madrid"`, `USE_TZ = True`, `DEFAULT_AUTO_FIELD`.
- `config/settings/local.py` — importa todo de `base`, `DEBUG = True`,
  `ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver"]`, y `SECRET_KEY` con un valor de desarrollo
  explícito y comentado como tal.
- `config/urls.py` — solo `path("admin/", admin.site.urls)`.
- `config/wsgi.py`, `config/asgi.py`.

**Done when**

- [ ] WHEN `uv run python manage.py check` runs THE SYSTEM SHALL exit 0 and report zero issues.
- [ ] WHEN `manage.py` is read THE SYSTEM SHALL contain the literal `config.settings.local` as the default value of `DJANGO_SETTINGS_MODULE`, identical to the value `pyproject.toml` declares for pytest.
- [ ] WHEN `config.settings.local` is imported THE SYSTEM SHALL expose `INSTALLED_APPS` containing `django.contrib.admin`, `django.contrib.auth`, `django.contrib.sessions`, `django.contrib.contenttypes` and `django.contrib.messages`.
- [ ] WHEN the project is inspected THE SYSTEM SHALL have applied **zero** migrations — `manage.py showmigrations` lists none as applied, because the first migration must be `cuentas` (paso 4).
- [ ] WHEN `uv run ruff check config manage.py` runs THE SYSTEM SHALL exit 0.
- [ ] WHEN `uv run python manage.py check --list-tags` runs THE SYSTEM SHALL exit 0, proving the entry point is executable and not merely syntactically valid.

**Verify**

```powershell
uv run python manage.py check
if ($LASTEXITCODE -ne 0) { throw 'manage.py check no sale 0' }          # expect: exit 0

# El punto de entrada se EJECUTA, no solo se compila (§9 regla 13).
uv run python manage.py check --list-tags
if ($LASTEXITCODE -ne 0) { throw 'manage.py no es ejecutable' }         # expect: exit 0

# Contrato entre dos artefactos: manage.py y pyproject.toml nombran el MISMO módulo.
if (-not ((Get-Content -Raw 'manage.py') -match '"DJANGO_SETTINGS_MODULE",\s*"config\.settings\.local"')) { throw 'manage.py no fija config.settings.local' }
if (-not ((Get-Content -Raw 'pyproject.toml') -match 'DJANGO_SETTINGS_MODULE\s*=\s*"config\.settings\.local"')) { throw 'pyproject.toml no fija config.settings.local' }

uv run python -c "import os; os.environ['DJANGO_SETTINGS_MODULE']='config.settings.local'; import django; django.setup(); from django.conf import settings; faltan=[a for a in ('django.contrib.admin','django.contrib.auth','django.contrib.sessions','django.contrib.contenttypes','django.contrib.messages') if a not in settings.INSTALLED_APPS]; assert not faltan, faltan; print('INSTALLED_APPS OK')"
if ($LASTEXITCODE -ne 0) { throw 'faltan aplicaciones de contrib que §8 exige' }   # expect: exit 0

# Ninguna migracion aplicada todavia: la primera tiene que ser la de cuentas (paso 4).
$aplicadas = (uv run python manage.py showmigrations --plan 2>&1 | Select-String -Pattern '^\[X\]').Count
if ($aplicadas -ne 0) { throw "hay $aplicadas migraciones aplicadas; no debe haber ninguna antes del paso 4" }

uv run ruff check config manage.py
if ($LASTEXITCODE -ne 0) { throw 'ruff falla sobre el codigo nuevo' }   # expect: exit 0
```

**Checkpoint**

```powershell
git add -A
git commit -m "paso 1: esqueleto de Django ejecutable"
git tag step-01-esqueleto
git ls-files --error-unmatch manage.py config/settings/local.py
if ($LASTEXITCODE -ne 0) { throw 'el commit no ha recogido el esqueleto' }   # expect: exit 0
# punto de retorno si el paso 2 sale mal: git reset --hard step-01-esqueleto
```

---

#### Paso 2 — Configuración tipada y registro estructurado

**Do**

Sustituir las constantes provisionales del paso 1 por configuración tipada, y dejar el registro de
eventos montado antes de que haya nada que registrar.

- `config/settings/base.py` — se reescribe la parte de configuración: una clase `Settings` de
  `pydantic_settings.BaseSettings` con `model_config = SettingsConfigDict(env_file=".env", extra="ignore")`
  y los campos `django_secret_key: str`, `django_debug: bool = True`,
  `django_allowed_hosts: str = "127.0.0.1,localhost"`, `anthropic_api_key: str | None = None`,
  `anthropic_model: str | None = None`, `precio_entrada_eur_por_mtok: Decimal = 0`,
  `precio_salida_eur_por_mtok: Decimal = 0`.
  **Todos con valor por defecto salvo la clave, que lo recibe en `local.py`**: ninguna variable es
  obligatoria en desarrollo, y por eso ningún paso posterior puede romper el gate de un paso anterior
  exigiendo un secreto (§9 regla 9, §10).
  **Una variable declarada y vacía en `.env` cuenta como NO definida**, y esto no es un adorno:
  `.env.example` se versiona con todas las claves presentes y los valores vacíos, y §10 lo copia a
  `.env` tal cual. Sin un validador `mode="before"` que descarte los valores vacíos, un
  `ANTHROPIC_API_KEY=` llega como cadena vacía en vez de `None` —y el segundo criterio de aceptación
  de este paso falla— y un `PRECIO_ENTRADA_EUR_POR_MTOK=` revienta la validación del decimal antes
  de que Django arranque. Verificado ejecutándolo.
  **Este es el único punto del proyecto que lee `.env`**, y por eso es el mecanismo de carga de
  variables de entorno de todo el sistema (§19.6).
- `config/settings/local.py` — pasa a leer de esa clase; mantiene el valor de desarrollo de la clave.
- `config/logging.py` — configuración de `structlog` sobre `logging`: procesadores de nivel, marca de
  tiempo ISO y renderizador de consola. Una función `configure_logging()` que `base.py` invoca.
- `tests/web/__init__.py` — **obligatorio**: sin él, pytest no inserta la raíz del proyecto en
  `sys.path` para esta carpeta y ningún test de `tests/web/` podría importar `config` ni `apps`
  (§19.6, matriz de resolución).
- `tests/web/test_settings.py` — comprueba que la configuración se carga, que ninguna variable es
  obligatoria y que `configure_logging()` deja un logger de `structlog` utilizable.

**Done when**

- [ ] WHEN `config.settings.local` is imported with an empty environment and no `.env` file THE SYSTEM SHALL load successfully and SHALL NOT raise a missing-variable error.
- [ ] WHEN `ANTHROPIC_API_KEY` is absent THE SYSTEM SHALL expose `settings.ANTHROPIC_API_KEY` as `None` rather than an empty string, so the AI layer can tell "unset" from "set to nothing".
- [ ] WHEN `DJANGO_ALLOWED_HOSTS` contains `a.example,b.example` THE SYSTEM SHALL expose `ALLOWED_HOSTS` as a list of two entries, not a single comma-joined string.
- [ ] WHEN `configure_logging()` runs and a bound logger emits an event THE SYSTEM SHALL produce a record carrying the bound keys.
- [ ] WHEN `uv run pytest tests/web/test_settings.py` runs THE SYSTEM SHALL exit 0 with 0 failed and 0 skipped.
- [ ] WHEN `uv run python manage.py check` runs THE SYSTEM SHALL still exit 0 — the step-1 gate does not regress.

**Verify**

```powershell
uv run pytest tests/web/test_settings.py -q
if ($LASTEXITCODE -ne 0) { throw 'las pruebas de configuracion fallan' }   # expect: exit 0, 0 failed, 0 skipped

# Ninguna variable es obligatoria: la configuracion carga con el entorno vacio.
uv run python -c "import os; [os.environ.pop(k, None) for k in ('DJANGO_SECRET_KEY','DJANGO_DEBUG','DJANGO_ALLOWED_HOSTS','ANTHROPIC_API_KEY','ANTHROPIC_MODEL')]; os.environ['DJANGO_SETTINGS_MODULE']='config.settings.local'; import django; django.setup(); from django.conf import settings; assert isinstance(settings.ALLOWED_HOSTS, list); print('config OK')"
if ($LASTEXITCODE -ne 0) { throw 'la configuracion exige alguna variable' }   # expect: exit 0

uv run python manage.py check
if ($LASTEXITCODE -ne 0) { throw 'el gate del paso 1 ha dejado de pasar' }    # expect: exit 0

uv run ruff check config tests/web
if ($LASTEXITCODE -ne 0) { throw 'ruff falla' }                              # expect: exit 0
uv run mypy config
if ($LASTEXITCODE -ne 0) { throw 'mypy falla sobre config/' }                # expect: exit 0
```

**Checkpoint**

```powershell
git add -A
git commit -m "paso 2: configuracion tipada con pydantic-settings y structlog"
git tag step-02-configuracion
git ls-files --error-unmatch config/logging.py tests/web/__init__.py
if ($LASTEXITCODE -ne 0) { throw 'el commit no ha recogido la configuracion' }   # expect: exit 0
```

---

#### Paso 3 — Retirada de Streamlit y red de seguridad en verde

**Do**

Este es el paso que convierte "el 92% del código sobrevive" en un hecho comprobado en lugar de una
afirmación. No se escribe lógica nueva: se retira la capa que se sustituye y se ejecuta la suite
rescatada entera contra la cadena de herramientas y las versiones fijadas en §11 —que es donde se
descubriría un cambio de comportamiento de `reportlab` (§20.2, riesgo 2)—.

- Borrar `ui/app.py` y `ui/__init__.py`. `streamlit` no está en el `pyproject.toml` emitido.
- **Retirar el eslabón de Streamlit de `resolve_api_key()` en `ai/claude_client.py`.** No basta con
  borrar `ui/`: esa función encadena tres orígenes para la clave —secretos de Streamlit Cloud,
  entorno, `.env`— y el primero hace `import streamlit` dentro de un `try`. Es la única dependencia
  de la capa de IA con un framework, y **el gate de este paso no puede pasar mientras siga ahí**:
  el criterio exige cero apariciones de `import streamlit` fuera de `blueprints/`. Se quedan los dos
  eslabones restantes, que no dependen de nada; la aplicación web no llama a esta función, le pasa la
  clave que ya leyó su configuración tipada (paso 2). Verificado ejecutándolo: sin esta retirada el
  paso 3 falla en su cuarta comprobación.
- Borrar `requirements.txt` (lo sustituye `pyproject.toml` + `uv.lock`) y el directorio `tpip.egg-info/`
  (residuo de `pip install -e .`, que ya no se usa: `[tool.uv] package = false`).
- Borrar `pyproject.toml.pre-django`, que §10 dejó archivado, **solo si** `git log` ya lo recoge en el
  commit de bootstrap; si no, dejarlo y anotarlo.
- Añadir `tests/web/test_rescate.py`: comprueba que los tres paquetes rescatados se importan sin
  Django y sin Streamlit, y que el registro de fuentes sigue teniendo sus 5 entradas.

**Done when**

- [ ] WHEN `uv run pytest tests/domain tests/ai tests/report` runs THE SYSTEM SHALL report exactly 180 passed, 0 failed and 0 skipped — the rescued safety net, counted on 2026-08-15, unchanged.
- [ ] WHEN the repository is searched for `import streamlit` THE SYSTEM SHALL find zero occurrences outside `blueprints/`.
- [ ] WHEN `ui/` is looked for on disk THE SYSTEM SHALL NOT find it.
- [ ] WHEN `tp_domain.sources.SOURCE_REGISTRY` is imported THE SYSTEM SHALL contain exactly the 5 source ids the engine can cite.
- [ ] WHEN `uv run ruff check .` runs from the project root with the bundle present THE SYSTEM SHALL exit 0, proving the `blueprints` exclusion in `pyproject.toml` holds.

**Verify**

```powershell
uv run pytest tests/domain tests/ai tests/report -q
if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad rescatada NO esta en verde' }
# expect: exit 0 — "180 passed" exactamente; 0 failed, 0 skipped

$n = (uv run pytest tests/domain tests/ai tests/report --collect-only -q 2>&1 | Select-String -Pattern '^(\d+) tests collected').Matches[0].Groups[1].Value
if ([int]$n -ne 180) { throw "la suite rescatada tiene $n pruebas, se esperaban 180" }   # expect: 180

if (Test-Path 'ui') { throw 'ui/ sigue existiendo' }
if (Test-Path 'requirements.txt') { throw 'requirements.txt sigue existiendo' }

# Ni una referencia a streamlit fuera del bundle.
$hits = Select-String -Path (Get-ChildItem -Recurse -Filter '*.py' -File | Where-Object { $_.FullName -notmatch '\\(\.venv|blueprints)\\' }).FullName -Pattern 'import streamlit' -SimpleMatch -ErrorAction SilentlyContinue
if ($hits) { throw 'queda alguna importacion de streamlit' }

uv run python -c "from tp_domain.sources import SOURCE_REGISTRY; assert len(SOURCE_REGISTRY) == 5, len(SOURCE_REGISTRY); print('registro OK')"
if ($LASTEXITCODE -ne 0) { throw 'el registro cerrado de fuentes ha cambiado' }   # expect: exit 0

# ruff desde la raiz CON el bundle presente: prueba la exclusion de blueprints/.
uv run ruff check .
if ($LASTEXITCODE -ne 0) { throw 'ruff falla desde la raiz con el bundle presente' }   # expect: exit 0
```

**Checkpoint**

```powershell
git add -A
git commit -m "paso 3: retirada de Streamlit; la suite rescatada de 180 pruebas queda en verde"
git tag step-03-rescate
git ls-files ui | Measure-Object -Line | ForEach-Object { if ($_.Lines -ne 0) { throw 'ui/ sigue versionado' } }
```

---

#### Paso 4 — Modelo de usuario propio, `AUTH_USER_MODEL` y panel de administración

**Do**

**Es el paso con una sola oportunidad de todo el proyecto.** `AUTH_USER_MODEL` no se puede cambiar
después de la migración inicial sin reescribir la capa de datos entera (§4.5, §8), así que la primera
migración que este proyecto aplica es la de `apps.cuentas`, y ninguna otra antes.

- `apps/__init__.py`, `apps/cuentas/__init__.py` — marcadores de paquete.
- `apps/cuentas/apps.py` — `CuentasConfig` con `name = "apps.cuentas"` y `label = "cuentas"`.
- `apps/cuentas/models.py` — el modelo `Usuario` **tal cual está en §4.4**, heredando de `AbstractUser`.
- `apps/cuentas/admin.py` — registra `Usuario` sobre `UserAdmin`, añadiendo `tope_gasto_mensual_eur` y
  `notas_admin` a los formularios. **Un modelo sin registrar es apalancamiento desperdiciado**: el
  panel es la razón por la que se eligió Django (§2), y esta es la primera vez que se cobra.
- `config/settings/base.py` — `AUTH_USER_MODEL = "cuentas.Usuario"` y `"apps.cuentas"` en
  `INSTALLED_APPS`, **antes** de `django.contrib.admin` en el orden no importa, pero el ajuste sí tiene
  que existir antes del primer `migrate`.
- `tests/web/conftest.py` — **los *fixtures* compartidos de toda la suite web**: `usuario`,
  `otro_usuario` y `administrador`. Se crean aquí porque este es el primer paso en el que existe la
  tabla de usuarios, y desde el paso 5 **todas** las pruebas de `tests/web/` los piden. Sin este
  fichero la suite entera falla con `fixture 'usuario' not found`, que se lee como una instalación
  rota y no lo es.
- `tests/web/test_cuentas.py` — el modelo se crea, el correo es único, la baja es `is_active=False` y
  un `delete()` de un usuario con casos fallará (se comprueba en el paso 6, cuando `Caso` exista).

La migración se genera con `uv run python manage.py makemigrations cuentas` y se aplica con
`uv run python manage.py migrate`. **No se escribe a mano y no se le pone nombre.**

**Done when**

- [ ] WHEN `settings.AUTH_USER_MODEL` is read THE SYSTEM SHALL be exactly `cuentas.Usuario`.
- [ ] WHEN `uv run python manage.py migrate` runs against a fresh database THE SYSTEM SHALL exit 0 with `cuentas.0001_initial` applied before `admin.0001_initial` and before any table carrying a foreign key to the user — las migraciones de `auth` que crean grupos y permisos van necesariamente antes, porque `AbstractUser` depende de ellas, and `makemigrations --check --dry-run` SHALL then exit 0 — no model change left unmigrated.
- [ ] WHEN two users are created with the same `email` THE SYSTEM SHALL raise an integrity error — the field is unique.
- [ ] WHEN a `Usuario` is created without specifying `tope_gasto_mensual_eur` THE SYSTEM SHALL default it to `5.00`.
- [ ] WHEN any test in `tests/web/` requests the `usuario`, `otro_usuario` or `administrador` fixture THE SYSTEM SHALL resolve it from `tests/web/conftest.py`, so no later suite fails with a missing-fixture error.
- [ ] WHEN the admin registry is inspected THE SYSTEM SHALL have `cuentas.Usuario` registered — el panel es la razón por la que se eligió Django, y esta es la primera vez que se cobra.

**Verify**

```powershell
uv run python manage.py makemigrations cuentas
if ($LASTEXITCODE -ne 0) { throw 'makemigrations falla' }                # expect: exit 0
uv run python manage.py migrate
if ($LASTEXITCODE -ne 0) { throw 'migrate falla' }                       # expect: exit 0
uv run python manage.py makemigrations --check --dry-run
if ($LASTEXITCODE -ne 0) { throw "quedan cambios de modelo sin migrar (codigo $LASTEXITCODE)" }   # expect: exit 0
uv run python manage.py migrate --check
if ($LASTEXITCODE -ne 0) { throw 'la base de datos no esta al dia' }      # expect: exit 0

uv run python -c "import os; os.environ['DJANGO_SETTINGS_MODULE']='config.settings.local'; import django; django.setup(); from django.conf import settings; from django.contrib import admin; from apps.cuentas.models import Usuario; assert settings.AUTH_USER_MODEL=='cuentas.Usuario', settings.AUTH_USER_MODEL; assert Usuario in admin.site._registry, 'Usuario no esta registrado en el admin'; print('AUTH_USER_MODEL y admin OK')"
if ($LASTEXITCODE -ne 0) { throw 'AUTH_USER_MODEL o el registro en el admin no son los esperados' }   # expect: exit 0

uv run pytest tests/web -q
if ($LASTEXITCODE -ne 0) { throw 'las pruebas de cuentas fallan' }        # expect: exit 0, 0 failed, 0 skipped
uv run pytest tests/domain tests/ai tests/report -q
if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A
git commit -m "paso 4: modelo de usuario propio, AUTH_USER_MODEL y panel de administracion"
git tag step-04-cuentas
git ls-files --error-unmatch apps/cuentas/models.py apps/cuentas/admin.py
if ($LASTEXITCODE -ne 0) { throw 'el modelo de usuario no ha quedado versionado' }
if ((git ls-files 'apps/cuentas/migrations/*.py' | Measure-Object -Line).Lines -lt 2) { throw 'la migracion generada no ha quedado versionada' }
```

---

#### Paso 5 — Acceso: entrar, salir, cambiar contraseña y cierre por omisión

**Do**

- `apps/comun/__init__.py`, `apps/comun/middleware.py` — `ExigirAutenticacion`: exige sesión en **todo**
  salvo una lista explícita de rutas públicas (`/entrar/`, los estáticos y las páginas de error).
  **La orientación del valor por defecto es la decisión**: olvidar un decorador deja una vista abierta;
  olvidar añadir una ruta a la lista blanca deja una vista cerrada, que es el fallo seguro.
- `apps/cuentas/views.py` y `apps/cuentas/urls.py` — `/entrar/`, `/salir/` (**solo POST**) y
  `/cuenta/contrasena/`. Mensaje de error **genérico e idéntico** para usuario inexistente, contraseña
  incorrecta y cuenta inactiva.
- `config/settings/base.py` — el middleware, `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `SESSION_COOKIE_AGE`,
  `SESSION_EXPIRE_AT_BROWSER_CLOSE`, `SESSION_COOKIE_HTTPONLY`, `SESSION_COOKIE_SAMESITE` (§8).
- `templates/cuentas/entrar.html` y `templates/cuentas/contrasena.html`.
- `tests/web/test_acceso.py`.

`createsuperuser --noinput` se documenta en §10; no se ejecuta dentro de un paso.

**Done when**

- [ ] WHEN an anonymous request hits any URL other than `/entrar/`, the static files or an error page THE SYSTEM SHALL respond `302` to `/entrar/` carrying the original path in `next`.
- [ ] WHEN `/entrar/` receives wrong credentials, a username that does not exist, or an inactive account THE SYSTEM SHALL respond `422` with **the same** generic message in all three cases, revealing nothing about which accounts exist.
- [ ] WHEN `/entrar/` receives valid credentials with a `next` pointing at an external host THE SYSTEM SHALL ignore it and redirect to the case list instead.
- [ ] WHEN `/salir/` receives a `GET` THE SYSTEM SHALL respond `405` and SHALL NOT end the session.
- [ ] WHEN a password is changed successfully THE SYSTEM SHALL rotate the session key so the old session cookie no longer authenticates.
- [ ] WHEN `uv run pytest tests/web/test_acceso.py` runs THE SYSTEM SHALL exit 0 with 0 failed and 0 skipped.

**Verify**

```powershell
uv run pytest tests/web/test_acceso.py -q
if ($LASTEXITCODE -ne 0) { throw 'las pruebas de acceso fallan' }   # expect: exit 0, 0 failed, 0 skipped

# El cierre es por omision: el middleware esta instalado, no un decorador por vista.
uv run python -c "import os; os.environ['DJANGO_SETTINGS_MODULE']='config.settings.local'; import django; django.setup(); from django.conf import settings; assert any('ExigirAutenticacion' in m for m in settings.MIDDLEWARE), settings.MIDDLEWARE; print('middleware OK')"
if ($LASTEXITCODE -ne 0) { throw 'el middleware de cierre por omision no esta instalado' }   # expect: exit 0

uv run pytest tests/web -q
if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q
if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A
git commit -m "paso 5: acceso, cierre de sesion y cierre por omision via middleware"
git tag step-05-acceso
```

---

#### Paso 6 — Entidad `Caso`: propietario, título y borrado suave

**Do**

- `apps/analisis/__init__.py`, `apps/analisis/apps.py` — `AnalisisConfig`, `label = "analisis"`.
- `apps/analisis/models.py` — el modelo `Caso` y el `CasoVivoManager` **tal cual están en §4.4**:
  `usuario` como clave foránea **no nula, indexada y `PROTECT`**, `titulo`, `deleted_at` y el índice
  compuesto `(usuario, -created_at)`.
- `apps/analisis/admin.py` — registra `Caso` usando `Caso.todos` como consulta base, con
  `list_display` de título, usuario y fecha, y filtro por usuario. **Es lo que hace visible el aviso de
  privacidad de §8 como un hecho y no como una advertencia teórica.**
- `config/settings/base.py` — `"apps.analisis"` en `INSTALLED_APPS`.
- `tests/web/test_caso.py` — ida y vuelta del `payload`, el gestor por defecto oculta los borrados en
  suave, y **borrar un usuario con casos levanta `ProtectedError`**.

**Done when**

- [ ] WHEN a `Caso` is saved and read back THE SYSTEM SHALL rehydrate it through `AnalysisResult.model_validate` without raising.
- [ ] WHEN a `Caso` is created THE SYSTEM SHALL require a non-null `usuario`, and an attempt to save without one SHALL raise an integrity error.
- [ ] WHEN a `Caso` has `deleted_at` set THE SYSTEM SHALL exclude it from `Caso.objects` and SHALL include it in `Caso.todos`.
- [ ] WHEN `delete()` is called on a `Usuario` that owns at least one `Caso` THE SYSTEM SHALL raise `ProtectedError` and delete nothing.
- [ ] WHEN `uv run python manage.py makemigrations --check --dry-run` runs THE SYSTEM SHALL exit 0.
- [ ] WHEN `engine_version`, `dataset_version` and `has_ai_explanation` are read back THE SYSTEM SHALL find them equal to the values inside `payload`, derived at save time.

**Verify**

```powershell
uv run python manage.py makemigrations analisis
if ($LASTEXITCODE -ne 0) { throw 'makemigrations falla' }                # expect: exit 0
uv run python manage.py makemigrations --check --dry-run
if ($LASTEXITCODE -ne 0) { throw "quedan cambios de modelo sin migrar (codigo $LASTEXITCODE)" }   # expect: exit 0
uv run python manage.py migrate
if ($LASTEXITCODE -ne 0) { throw 'migrate falla' }                       # expect: exit 0
uv run python manage.py migrate --check
if ($LASTEXITCODE -ne 0) { throw 'la base de datos no esta al dia' }     # expect: exit 0

# usuario_id existe, es NOT NULL y esta indexado: es lo que hace decidible el aislamiento.
uv run python -c "import os; os.environ['DJANGO_SETTINGS_MODULE']='config.settings.local'; import django; django.setup(); from apps.analisis.models import Caso; f=Caso._meta.get_field('usuario'); assert not f.null, 'usuario admite null'; assert f.db_index, 'usuario no esta indexado'; from django.db.models import PROTECT; assert f.remote_field.on_delete is PROTECT, f.remote_field.on_delete; print('usuario_id OK')"
if ($LASTEXITCODE -ne 0) { throw 'la clave foranea al usuario no cumple lo que exige §4' }   # expect: exit 0

uv run pytest tests/web -q
if ($LASTEXITCODE -ne 0) { throw 'las pruebas de Caso fallan' }          # expect: exit 0, 0 failed, 0 skipped
uv run pytest tests/domain tests/ai tests/report -q
if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A
git commit -m "paso 6: entidad Caso con propietario, titulo y borrado suave"
git tag step-06-caso
git ls-files --error-unmatch apps/analisis/models.py apps/analisis/admin.py
if ($LASTEXITCODE -ne 0) { throw 'el modelo Caso no ha quedado versionado' }
```

---

#### Paso 7 — Guarda de autorización única y aislamiento con 404

**Do**

- `apps/comun/guardas.py` — la función `caso_del_usuario(usuario, pk)` **tal cual está en §8**, con su
  docstring explicando por qué **404 y no 403**. Es la única puerta de lectura de un `Caso` con
  propietario.
- `apps/comun/consultas.py` — `casos_de(usuario)`, que devuelve el `QuerySet` ya filtrado. Todo listado
  parte de aquí; ninguna vista escribe `Caso.objects.filter(...)` por su cuenta.
- `tests/web/test_aislamiento.py` — dos usuarios, un caso cada uno, y **cada intento cruzado responde
  404**: ver, listar, descargar el informe y borrar. Las rutas que aún no existen (informe, listado) se
  añaden a este mismo fichero en los pasos 14 y 15, que es donde nacen.
- `tests/web/test_guarda_unica.py` — la comprobación negativa: ninguna vista de `apps/analisis/`
  construye una consulta sobre `Caso` sin pasar por la guarda o sin filtrar por `request.user`. Se
  comprueba buscando en el código, que es el medio donde esa propiedad es observable (§9 regla 12).

**Done when**

- [ ] WHEN user A requests `/casos/<pk-de-B>/` THE SYSTEM SHALL respond **404**, not 403 — a 403 would confirm the id exists.
- [ ] WHEN user A requests a `pk` that exists in no table THE SYSTEM SHALL respond **404**, indistinguishable from the previous case.
- [ ] WHEN user A lists their cases and user B owns cases too THE SYSTEM SHALL return only A's rows.
- [ ] WHEN a case has `deleted_at` set and its owner requests it THE SYSTEM SHALL respond **404**.
- [ ] WHEN `apps/analisis/` source is searched THE SYSTEM SHALL find zero `Caso.objects` accesses outside `apps/comun/`, so the guard is the only path.
- [ ] WHEN `uv run pytest tests/web/test_aislamiento.py tests/web/test_guarda_unica.py` runs THE SYSTEM SHALL exit 0 with 0 failed and 0 skipped.

**Verify**

```powershell
uv run pytest tests/web/test_aislamiento.py tests/web/test_guarda_unica.py -q
if ($LASTEXITCODE -ne 0) { throw 'el aislamiento por propietario falla' }   # expect: exit 0, 0 failed, 0 skipped

# La guarda existe con nombre y documenta el 404.
if (-not (Test-Path 'apps/comun/guardas.py')) { throw 'falta apps/comun/guardas.py' }
if ((Get-Content -Raw 'apps/comun/guardas.py') -notmatch 'def caso_del_usuario') { throw 'la guarda no tiene el nombre acordado' }

# Ninguna vista consulta Caso por su cuenta: la guarda es el unico camino.
$sueltas = Select-String -Path (Get-ChildItem 'apps/analisis' -Recurse -Filter '*.py' -File).FullName -Pattern 'Caso\.objects' -ErrorAction SilentlyContinue
if ($sueltas) { throw "hay consultas directas a Caso.objects fuera de apps/comun: $($sueltas.Path -join ', ')" }

uv run pytest tests/web -q
if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q
if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A
git commit -m "paso 7: guarda de autorizacion unica y aislamiento con 404"
git tag step-07-guarda
```

---

#### Paso 8 — Defecto 1: el modelo de IA deja de resolverse solo

**Do**

`ai/claude_client.py:78` resuelve hoy el identificador del modelo **en ejecución**: si
`ANTHROPIC_MODEL` no está definida, pregunta a la API por el catálogo y elige "el Sonnet más
reciente". Es un defecto por tres razones distintas, y las tres importan en este producto concreto:

1. **Rompe la reproducibilidad, que es la premisa del sistema.** `ENGINE_VERSION` viaja dentro de cada
   `AnalysisResult` para que un análisis emitido hoy se pueda reproducir mañana. Un modelo que cambia
   solo hace que dos informes idénticos en todo lo demás se hayan redactado con modelos distintos, sin
   que nadie lo haya decidido.
2. **Convierte una llamada de red opcional en obligatoria.** La capa de IA está diseñada para poder
   fallar entera sin que se note; en cambio, `resolve_model` puede tumbarla por un motivo —el catálogo
   no responde— que no tiene nada que ver con la explicación.
3. **Es la capa de IA descubriendo su propia configuración.** Contradice la frontera de §3: `ai/` no
   decide nada, se le inyecta. Y hace imposible el paso 16: un modelo que no se conoce antes de llamar
   no se puede tarifar antes de llamar, y sin tarifa no hay tope de gasto comprobable **antes** del
   gasto.

La corrección:

- `ai/claude_client.py`:
  - **Borrar `resolve_model()` por completo**, junto con la llamada a `client.models.list`.
  - `request_explanation(result, client=None, model=None)` pasa a exigir `model`: si llega vacío,
    levanta `ClaudeUnavailable("No hay ANTHROPIC_MODEL configurado...")`. `explain_analysis` sigue sin
    lanzar nunca y devuelve `None`, tal como está hoy.
  - `resolve_api_key()` pierde la rama de `st.secrets` (Streamlit ya no existe, paso 3) y la rama de
    `dotenv_values(".env")`: quien carga `.env` es `config/settings/base.py` y nadie más (§19.6).
    Queda leyendo `ANTHROPIC_API_KEY` del entorno, y el llamante puede seguir inyectando la clave.
  - **Devolver el uso reportado por el proveedor.** `request_explanation` pasa a devolver, junto a la
    `AIExplanation`, el objeto `usage` de la respuesta y el `stop_reason`, sin interpretarlos: es lo
    que el paso 16 persiste en `LlamadaLLM`. `ai/` no calcula coste ni cuenta tokens; solo transporta
    lo que el proveedor dijo.
  - Actualizar el docstring del módulo, que hoy describe la precedencia antigua.
- `.env.example` — el comentario de `ANTHROPIC_MODEL` deja de decir que se resuelve solo y pasa a decir
  que sin ella la capa de IA queda desactivada.
- `tests/ai/test_explanation_flow.py` — **se sustituyen prueba por prueba** las que cubrían la
  resolución dinámica y la precedencia antigua de la clave, por otras que cubren el comportamiento
  nuevo. El recuento de la suite rescatada **sigue siendo 180**, y el gate del paso 3 lo comprueba.

`ai/` sigue sin importar Django: el modelo y la clave se los pasa el llamante, y ese llamante es
`apps/analisis/services.py`, que se escribe en el paso 17.

**Done when**

- [ ] WHEN `ai/claude_client.py` is read THE SYSTEM SHALL contain no reference to `models.list` and no function named `resolve_model`.
- [ ] WHEN `request_explanation` is called with `model=None` THE SYSTEM SHALL raise `ClaudeUnavailable` without making any network call.
- [ ] WHEN `explain_analysis` is called with `model=None` THE SYSTEM SHALL return `None` and SHALL NOT raise.
- [ ] WHEN a call succeeds THE SYSTEM SHALL return the provider's reported `usage` and `stop_reason` alongside the explanation, uninterpreted — no token is counted locally.
- [ ] WHEN `ai/claude_client.py` is imported THE SYSTEM SHALL NOT import `django` or `streamlit`.
- [ ] WHEN `uv run pytest tests/domain tests/ai tests/report` runs THE SYSTEM SHALL still report exactly 180 passed — every retired test has been replaced by one covering the new behaviour.

**Verify**

```powershell
if ((Get-Content -Raw 'ai/claude_client.py') -match 'models\.list') { throw 'sigue consultando el catalogo de modelos' }
if ((Get-Content -Raw 'ai/claude_client.py') -match 'def resolve_model') { throw 'resolve_model sigue existiendo' }
if ((Get-Content -Raw 'ai/claude_client.py') -match 'import streamlit') { throw 'sigue importando streamlit' }
if ((Get-Content -Raw 'ai/claude_client.py') -match '(?m)^\s*(from|import)\s+django') { throw 'ai/ ha empezado a importar Django' }

uv run python -c "import inspect; from ai.claude_client import request_explanation; assert 'model' in inspect.signature(request_explanation).parameters; print('firma OK')"
if ($LASTEXITCODE -ne 0) { throw 'la firma de request_explanation no es la esperada' }   # expect: exit 0

uv run pytest tests/ai -q
if ($LASTEXITCODE -ne 0) { throw 'las pruebas de la capa de IA fallan' }   # expect: exit 0, 0 failed, 0 skipped

# La invariante de la migracion: la suite rescatada sigue teniendo 180 pruebas.
uv run pytest tests/domain tests/ai tests/report -q
if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
$n = (uv run pytest tests/domain tests/ai tests/report --collect-only -q 2>&1 | Select-String -Pattern '^(\d+) tests collected').Matches[0].Groups[1].Value
if ([int]$n -ne 180) { throw "la suite rescatada tiene $n pruebas, se esperaban 180" }   # expect: 180
```

**Checkpoint**

```powershell
git add -A
git commit -m "paso 8: el modelo de IA se fija por configuracion; fuera la resolucion dinamica"
git tag step-08-modelo-fijado
```

---

#### Paso 9 — Defecto 2: paleta con superficies diferenciadas

**Do**

`infrastructure/theme.py` tiene hoy **una sola superficie**: `COLORS["surface"] = "#F7F8FA"`. Para un
generador de PDF sobre papel blanco eso bastaba. Para una pantalla no: hacen falta al menos un fondo
de página, una superficie de tarjeta, una superficie hundida para cabeceras de tabla, un borde con
contraste suficiente para los controles de formulario y un color de foco. Con un único token, la
interfaz de Django tendría dos salidas y las dos son malas: aplanar todo contra un mismo gris, o
inventar colores fuera del lenguaje compartido —que es exactamente la divergencia entre pantalla e
informe que este módulo existe para impedir—.

La corrección es **estrictamente aditiva**: se añaden claves, no se renombra ni se elimina ninguna.
Renombrar `surface` rompería `pdf_report.py` y las 38 pruebas de `tests/report`, y la red de seguridad
del paso 3 dejaría de estar en verde.

- `infrastructure/theme.py` — añadir a `COLORS` las cuatro claves nuevas con los valores literales de
  §7: `background` `#FFFFFF`, `surface_sunken` `#EBEEF3`, `border_strong` `#767676`, `focus` `#1F4E79`.
  Añadir bajo la paleta un comentario que diga qué papel tiene cada superficie y cuál es su ratio de
  contraste medido, para que el siguiente que toque un hex sepa qué está gastando.
- `tests/report/test_theme_and_charts.py` — **no se añaden pruebas aquí**: cualquier prueba nueva
  cambiaría el recuento de la suite rescatada. La cobertura de los tokens nuevos es una prueba de la
  capa web y va en `tests/web/test_theme_tokens.py` (paso 13), porque lo que hay que comprobar es el
  contrato entre `theme.py` y el CSS, no el módulo aislado.

**Done when**

- [ ] WHEN `infrastructure.theme.COLORS` is imported THE SYSTEM SHALL contain the keys `background`, `surface_sunken`, `border_strong` and `focus` with the literal values §7 states.
- [ ] WHEN `infrastructure.theme.COLORS` is imported THE SYSTEM SHALL still contain every key it had before this step, with the same value — `ink`, `muted`, `rule`, `surface`, `band_outer`, `band_inner`, `median`, `ok`, `warn`, `risk`.
- [ ] WHEN every value in `COLORS` is read THE SYSTEM SHALL find each one is a 7-character `#RRGGBB` string.
- [ ] WHEN `uv run pytest tests/report tests/domain` runs THE SYSTEM SHALL exit 0 with 0 failed and 0 skipped.
- [ ] WHEN `uv run pytest tests/domain tests/ai tests/report` runs THE SYSTEM SHALL still report exactly 180 passed.

**Verify**

```powershell
uv run python -c "from infrastructure.theme import COLORS; esperado={'background':'#FFFFFF','surface_sunken':'#EBEEF3','border_strong':'#767676','focus':'#1F4E79','ink':'#1A1A1A','muted':'#5A5A5A','rule':'#C8C8C8','surface':'#F7F8FA','band_outer':'#DCE3EC','band_inner':'#9FB3C8','median':'#334E68','ok':'#2E6B4F','warn':'#8A6D1F','risk':'#8C2F2F'}; faltan=[k for k,v in esperado.items() if COLORS.get(k)!=v]; assert not faltan, faltan; malos=[k for k,v in COLORS.items() if not (len(v)==7 and v.startswith('#'))]; assert not malos, malos; print('paleta OK', len(COLORS))"
if ($LASTEXITCODE -ne 0) { throw 'la paleta no tiene las superficies nuevas o ha perdido alguna vieja' }   # expect: exit 0

uv run pytest tests/report tests/domain -q
if ($LASTEXITCODE -ne 0) { throw 'la ampliacion de la paleta ha roto el informe' }   # expect: exit 0, 0 failed, 0 skipped

uv run pytest tests/domain tests/ai tests/report -q
if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
$n = (uv run pytest tests/domain tests/ai tests/report --collect-only -q 2>&1 | Select-String -Pattern '^(\d+) tests collected').Matches[0].Groups[1].Value
if ([int]$n -ne 180) { throw "la suite rescatada tiene $n pruebas, se esperaban 180" }   # expect: 180
```

**Checkpoint**

```powershell
git add -A
git commit -m "paso 9: la paleta gana fondo, superficie hundida, borde de control y foco"
git tag step-09-paleta
```

---

#### Paso 10 — Formulario de operación

**Do**

- `apps/analisis/forms.py` — `CasoForm`, un `forms.Form` (no un `ModelForm`: no se guarda un
  formulario, se guarda un `AnalysisResult`). Un campo por cada fila de la tabla de entrada de §5, más
  `titulo`. Las opciones de `transaction_type` se generan **desde `SUPPORTED_TRANSACTION_TYPES`**, no
  se escriben a mano: cuando la Fase 2 añada un tipo, el desplegable lo recoge solo. Las de `industry`,
  desde el enum `Industry`.
  Su `clean()` construye un `tp_domain.models.Transaction` y traduce el `ValidationError` de pydantic
  a errores de formulario —los de campo, al campo; los del modelo entero, a error no asociado—, de
  modo que el usuario vea un solo conjunto de errores (§5). El objeto construido queda en
  `cleaned_data["transaction"]`.
  Si `titulo` llega vacío, se deriva de `description` recortada a 160 caracteres: la restricción única
  parcial de §4 exige que dos casos vivos del mismo usuario no compartan título, así que el formulario
  desambigua añadiendo la fecha efectiva cuando el derivado ya existe.
- `tests/web/test_forms.py` — casos válido e inválidos: jurisdicciones iguales, tipo no soportado,
  importe cero, tipo por encima de 100, fecha ausente, y título derivado.

**Done when**

- [ ] WHEN the form receives a valid payload THE SYSTEM SHALL expose a `tp_domain.models.Transaction` in `cleaned_data["transaction"]`.
- [ ] WHEN `payer_country` and `recipient_country` are equal THE SYSTEM SHALL be invalid and SHALL surface the domain message about two distinct jurisdictions as a non-field error.
- [ ] WHEN `transaction_type` is a value outside `SUPPORTED_TRANSACTION_TYPES` THE SYSTEM SHALL be invalid and the rendered `<select>` SHALL NOT have offered that value.
- [ ] WHEN `amount_eur` is `0` or `rate_percent` is `101` THE SYSTEM SHALL be invalid with the error attached to that specific field.
- [ ] WHEN `effective_date` is missing THE SYSTEM SHALL be invalid — there is no "today" default.
- [ ] WHEN `titulo` is submitted empty THE SYSTEM SHALL derive a non-empty title of at most 160 characters from `description`.

**Verify**

```powershell
uv run pytest tests/web/test_forms.py -q
if ($LASTEXITCODE -ne 0) { throw 'las pruebas del formulario fallan' }   # expect: exit 0, 0 failed, 0 skipped

# El desplegable se deriva del dominio, no esta escrito a mano.
if ((Get-Content -Raw 'apps/analisis/forms.py') -notmatch 'SUPPORTED_TRANSACTION_TYPES') { throw 'las opciones de tipo no se derivan del dominio' }

uv run ruff check apps tests/web
if ($LASTEXITCODE -ne 0) { throw 'ruff falla' }
uv run mypy apps config
if ($LASTEXITCODE -ne 0) { throw 'mypy falla' }
uv run pytest tests/domain tests/ai tests/report -q
if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A
git commit -m "paso 10: formulario de operacion sobre el Transaction del dominio"
git tag step-10-formulario
```

---

#### Paso 11 — Vista de análisis: POST → motor → persistencia con propietario

**Do**

La rebanada vertical, sin plantillas definitivas todavía (el paso 12 las escribe; aquí las respuestas
se prueban con el cliente de pruebas de Django y plantillas mínimas provisionales que el paso 12
sustituye).

- `apps/analisis/services.py` — `crear_caso(usuario, transaction, titulo) -> Caso`: llama a
  `tp_domain.calculations.arm_length_range.calculate_arm_length_range`, vuelca el resultado y crea la
  fila **con `usuario` puesto, a través de `apps/comun/escrituras.py`**. No la crea aquí: el gate de
  este mismo paso prohíbe cualquier `Caso.objects` dentro de `apps/analisis/`, y las dos cosas no
  podían ser ciertas a la vez. La resolución coherente es que **todo** acceso a una fila con
  propietario —leer y escribir— pase por `apps/comun`, no solo la lectura. Verificado ejecutándolo. **Sin IA todavía**: el paso 17 la enchufa aquí. **Sin nada de HTTP
  dentro.** Emite un evento de `structlog` con el id, el usuario, las dos jurisdicciones y la posición
  en el rango.
- `apps/analisis/views.py` — `formulario` (GET `/`), `crear` (POST `/casos/`) y `detalle`
  (GET `/casos/<uuid:pk>/`). `crear` devuelve **422** con el formulario reenviado cuando no valida, y
  **302** al detalle cuando sí. `detalle` **usa la guarda del paso 7** y no consulta `Caso` por su
  cuenta.
- `apps/analisis/urls.py` y `config/urls.py` — las rutas de §5, con `app_name = "analisis"` y nombres
  de ruta (`analisis:formulario`, `analisis:crear`, `analisis:detalle`) para que ninguna plantilla
  escriba una URL a mano.
- `tests/web/test_analisis_view.py` — el ciclo completo con el cliente de pruebas, autenticado.

**Done when**

- [ ] WHEN `GET /` is requested by an authenticated user THE SYSTEM SHALL respond `200` with an empty form.
- [ ] WHEN `POST /casos/` receives a valid payload THE SYSTEM SHALL respond `302` to `/casos/<uuid>/` and SHALL create exactly one `Caso` row whose `usuario` is the requesting user.
- [ ] WHEN `POST /casos/` receives an invalid payload THE SYSTEM SHALL respond `422` and SHALL create zero `Caso` rows.
- [ ] WHEN `GET /casos/<uuid>/` is requested for a case owned by another user THE SYSTEM SHALL respond `404` — the guard of paso 7 is the only reader.
- [ ] WHEN the persisted row is read back THE SYSTEM SHALL have `engine_version`, `dataset_version` and `has_ai_explanation` equal to the values derived from `payload` at save time.
- [ ] WHEN a transaction is submitted whose industry matches no comparable THE SYSTEM SHALL still respond `302` and persist a case carrying a `no_comparables` risk factor — an uncomputable range is a result, not a failure.

**Verify**

```powershell
uv run pytest tests/web/test_analisis_view.py tests/web/test_aislamiento.py -q
if ($LASTEXITCODE -ne 0) { throw 'el ciclo de analisis o el aislamiento fallan' }   # expect: exit 0, 0 failed, 0 skipped

# Fronteras de §3: la vista no importa el motor ni consulta Caso por su cuenta.
if ((Get-Content -Raw 'apps/analisis/views.py') -match 'tp_domain\.calculations') { throw 'la vista importa el motor; debe pasar por services.py' }
$sueltas = Select-String -Path (Get-ChildItem 'apps/analisis' -Recurse -Filter '*.py' -File).FullName -Pattern 'Caso\.objects' -ErrorAction SilentlyContinue
if ($sueltas) { throw 'hay consultas directas a Caso.objects fuera de apps/comun' }

uv run python manage.py check
if ($LASTEXITCODE -ne 0) { throw 'el gate del paso 1 ha dejado de pasar' }
uv run pytest tests/web -q
if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q
if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A
git commit -m "paso 11: POST valida, ejecuta el motor, persiste con propietario y redirige"
git tag step-11-vista-analisis
```

---

#### Paso 12 — Plantilla base y plantilla de resultado

**Do**

- `templates/base.html` — `<html lang="es">`, enlace "Saltar al contenido" como primer elemento
  enfocable, `<header>` con la navegación de la sesión iniciada y el formulario de salida por `POST`,
  `<main id="contenido">`, `<footer role="contentinfo">` con el aviso permanente de datos sintéticos
  **y el hueco del aviso de privacidad que rellena el paso 25**, y el enlace a `static/css/tokens.css`
  y `static/css/app.css` (los ficheros los escribe el paso 13; aquí basta con que las etiquetas
  apunten donde toca).
- `templates/analisis/form.html` — el formulario con un `<label for>` por campo y un contenedor
  `role="alert"` para los errores no asociados a campo.
- `templates/analisis/detalle.html` y los tres parciales de §6 — con **el rango como protagonista**: el
  SVG que devuelve `infrastructure.charts.benchmark_range_svg` a ancho completo y por encima de todo lo
  demás. Debajo, en este orden: posición y defendibilidad, tarjetas de jurisdicción, factores de
  riesgo, fuentes citadas, sección de IA (o su ausencia declarada) y el botón de descarga del informe.
- `templates/{400,403,404,405,500}.html`.
- `tests/web/test_result_template.py` — comprueba el contenido renderizado, no su aspecto.

Las plantillas **no calculan nada** y **no escriben ninguna URL a mano**: todo con `{% url %}`.

**Done when**

- [ ] WHEN a detail page is rendered for a case with comparables THE SYSTEM SHALL include an `<svg` element for the benchmark range inside `<main>`.
- [ ] WHEN a detail page is rendered for a case with **no** accepted comparables THE SYSTEM SHALL NOT include an `<svg` element and SHALL include the text stating no range could be calculated.
- [ ] WHEN a detail page is rendered THE SYSTEM SHALL contain one jurisdiction card per `JurisdictionAssessment`, each naming its country and its rule label from `infrastructure.theme`.
- [ ] WHEN a case has zero risk factors THE SYSTEM SHALL render the literal empty-state text, never an empty container.
- [ ] WHEN any page is rendered THE SYSTEM SHALL contain `<html lang="es"`, exactly one `<h1`, one `<main id="contenido"`, and a skip link whose `href` is `#contenido`.
- [ ] WHEN any authenticated page is rendered THE SYSTEM SHALL contain the permanent synthetic-data notice in the footer.

**Verify**

```powershell
uv run pytest tests/web/test_result_template.py -q
if ($LASTEXITCODE -ne 0) { throw 'las pruebas de plantilla fallan' }   # expect: exit 0, 0 failed, 0 skipped

# Ninguna plantilla escribe una URL a mano.
$rutasAMano = Select-String -Path (Get-ChildItem 'templates' -Recurse -Filter '*.html' -File).FullName -Pattern 'href="/casos|action="/casos|href="/fuentes|action="/entrar' -ErrorAction SilentlyContinue
if ($rutasAMano) { throw 'hay URLs escritas a mano en las plantillas; usa {% url %}' }

uv run pytest tests/web -q
if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q
if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A
git commit -m "paso 12: plantilla base y detalle con el rango como protagonista"
git tag step-12-plantillas
```

---

#### Paso 13 — Tokens de diseño: `theme.py` → CSS

**Do**

Este paso cierra el contrato entre pantalla e informe: el CSS deja de tener colores literales y pasa a
consumir variables generadas desde el mismo diccionario que usa el PDF.

- `scripts/__init__.py` — marcador de paquete. **Es lo que hace que `python -m scripts.build_tokens`
  encuentre `infrastructure`**; ejecutar `python scripts/build_tokens.py` no lo encontraría, porque el
  intérprete pondría `scripts/` en `sys.path` en vez de la raíz del proyecto (§19.6, matriz de
  resolución). Todo el proyecto invoca sus scripts con `-m`, sin excepción.
- `scripts/build_tokens.py` — lee `infrastructure.theme.COLORS` y la escala de espaciado de §7 y
  escribe `static/css/tokens.css` con un bloque `:root` de variables `--tpip-<clave-en-kebab>`. Acepta
  `--check`: **no escribe nada y sale 0 si el fichero en disco coincide con lo que generaría, y 1 si
  no.** Un código 2 significa error de uso; el gate afirma el 0 y el paso 27 afirma el 1 sobre un
  fichero manipulado a propósito.
- `static/css/tokens.css` — generado por el script y **versionado**, para que el CSS funcione sin
  ejecutar nada.
- `static/css/app.css` — escrito a mano; **ni un color literal**, solo `var(--tpip-*)`. Implementa la
  tipografía, el espaciado, el radio y el ancho máximo de §7.
- `tests/web/test_theme_tokens.py` — comprueba que cada clave de `COLORS` tiene su variable en
  `tokens.css` con el mismo valor, y que `app.css` no contiene ningún literal hexadecimal.

**Done when**

- [ ] WHEN `uv run python -m scripts.build_tokens --check` runs against a synchronised tree THE SYSTEM SHALL exit 0 and write nothing.
- [ ] WHEN `static/css/tokens.css` is read THE SYSTEM SHALL declare one `--tpip-*` custom property for every key of `infrastructure.theme.COLORS`, with the identical hex value.
- [ ] WHEN `static/css/app.css` is searched for a `#` followed by three or six hex digits THE SYSTEM SHALL find zero matches.
- [ ] WHEN `uv run python scripts/build_tokens.py` is run as a plain file path THE SYSTEM SHALL fail to import `infrastructure` — the documented reason the project invokes scripts with `-m`, stated here so nobody "fixes" the `-m` away.
- [ ] WHEN `uv run pytest tests/web/test_theme_tokens.py` runs THE SYSTEM SHALL exit 0 with 0 failed and 0 skipped.

**Verify**

```powershell
uv run python -m scripts.build_tokens --check
if ($LASTEXITCODE -ne 0) { throw "tokens.css esta desincronizado con theme.py (codigo $LASTEXITCODE)" }
# expect: exit 0 — 1 significaria "hay que regenerar"; 2, error de uso

uv run pytest tests/web/test_theme_tokens.py -q
if ($LASTEXITCODE -ne 0) { throw 'las pruebas de tokens fallan' }   # expect: exit 0, 0 failed, 0 skipped

$literales = Select-String -Path 'static/css/app.css' -Pattern '#[0-9A-Fa-f]{3,6}\b' -ErrorAction SilentlyContinue
if ($literales) { throw 'app.css contiene colores literales; deben venir de tokens.css' }

uv run ruff check scripts
if ($LASTEXITCODE -ne 0) { throw 'ruff falla sobre scripts/' }
uv run pytest tests/web -q
if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q
if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A
git commit -m "paso 13: tokens de diseno generados desde theme.py"
git tag step-13-tokens
git ls-files --error-unmatch static/css/tokens.css
if ($LASTEXITCODE -ne 0) { throw 'tokens.css no ha quedado versionado' }   # expect: exit 0
```

---

#### Paso 14 — Descarga del informe PDF

**Do**

- `apps/analisis/views.py` — añadir `informe`: obtiene el caso **a través de la guarda del paso 7**, lo
  rehidrata con `AnalysisResult.model_validate(obj.payload)`, llama a
  `infrastructure.report.render_report_bytes(result)` y responde con
  `Content-Type: application/pdf` y `Content-Disposition: attachment; filename="tpip-<uuid>.pdf"`.
- `apps/analisis/urls.py` — la ruta `analisis:informe`.
- `templates/analisis/detalle.html` — el botón de descarga apunta a `{% url 'analisis:informe' %}`.
- `tests/web/test_informe_view.py` — descarga el PDF por HTTP y extrae su texto con `pypdf`.
- `tests/web/test_aislamiento.py` — se amplía con el caso cruzado del informe, que nace aquí.

**El literal que se comprueba no es una predicción.** `DATOS SINTÉTICOS` es la primera palabra del
`disclaimer` de `TPIP_DATASET_V1` en `tp_domain/sources.py` (código rescatado, leído en disco el
2026-08-15), y `tests/report/test_pdf_report.py::test_cover_discloses_the_synthetic_dataset` ya lo
comprueba hoy sobre el PDF generado en memoria. Este paso comprueba lo mismo **sobre el PDF que sirve
la web**, que es lo que el usuario se lleva. Ver §19.6, *Conciliación de artefactos byte a byte*.

**Done when**

- [ ] WHEN `GET /casos/<uuid>/informe.pdf` is requested by the owner THE SYSTEM SHALL respond `200` with `Content-Type: application/pdf`.
- [ ] WHEN the served PDF is parsed with `pypdf` THE SYSTEM SHALL contain the literal `DATOS SINTÉTICOS` — the immovable notice of §20.2 risk 1, present in the document the user actually downloads.
- [ ] WHEN the response headers are read THE SYSTEM SHALL carry `Content-Disposition` with `attachment` and a filename containing the case UUID.
- [ ] WHEN the report of a case owned by another user is requested THE SYSTEM SHALL respond `404` and SHALL NOT generate a PDF.
- [ ] WHEN the report view runs THE SYSTEM SHALL make no network call — the PDF is produced from the persisted payload alone.
- [ ] WHEN the same case is downloaded twice THE SYSTEM SHALL produce a document with the same synthetic-data notice both times and SHALL NOT create any new `Caso` row.

**Verify**

```powershell
uv run pytest tests/web/test_informe_view.py tests/web/test_aislamiento.py -q
if ($LASTEXITCODE -ne 0) { throw 'la descarga del informe o su aislamiento fallan' }   # expect: exit 0, 0 failed, 0 skipped

uv run pytest tests/web -q
if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/report -q
if ($LASTEXITCODE -ne 0) { throw 'las pruebas de informe rescatadas fallan' }
uv run pytest tests/domain tests/ai tests/report -q
if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A
git commit -m "paso 14: descarga del informe PDF desde el caso persistido"
git tag step-14-informe
```

---

#### Paso 15 — Listado de casos: búsqueda, filtro, orden, vacío y paginación

**Do**

Un caso que se guarda pero no se encuentra es un caso perdido. Este paso convierte la tabla en una
biblioteca.

- `apps/comun/consultas.py` — se amplía `casos_de(usuario, *, texto, jurisdiccion, orden)`: filtra
  **siempre** por `usuario` primero, luego por texto sobre `titulo` (insensible a mayúsculas), luego por
  jurisdicción, y ordena por fecha o por título. **El filtro por propietario no es un parámetro
  opcional**: es el primer `filter` de la consulta y no hay forma de llamarla sin él.
- `apps/analisis/views.py` — `lista` (GET `/casos/`) con paginación por `Paginator` de Django.
  **El tamaño de página lo decide el servidor**: `?por_pagina=` se acepta pero se recorta a un máximo
  de 100 en el servidor, y un valor no numérico cae al valor por defecto de 20. Un cliente no puede
  pedir la tabla entera.
- `apps/analisis/views.py` — `borrar` (POST `/casos/<uuid>/borrar/`): borrado **suave**, poniendo
  `deleted_at`. Nunca un `DELETE`.
- `templates/analisis/lista.html` — la tabla, el formulario de búsqueda y filtro, los controles de
  orden, la paginación y **el estado vacío**, que distingue dos situaciones distintas: *"todavía no has
  analizado ninguna operación"* frente a *"ningún caso coincide con esta búsqueda"*, con un enlace para
  limpiar el filtro en el segundo.
- `tests/web/test_listado.py`.

**Done when**

- [ ] WHEN a user with zero cases opens `/casos/` THE SYSTEM SHALL respond `200` with the first-run empty state, and SHALL NOT show the "no matches" text.
- [ ] WHEN a search matches no case THE SYSTEM SHALL respond `200` with the "no matches" empty state and a link that clears the filter.
- [ ] WHEN user A lists cases and user B owns cases too THE SYSTEM SHALL return only A's rows, in every combination of search, filter and ordering.
- [ ] WHEN `?por_pagina=100000` is requested THE SYSTEM SHALL return at most 100 rows — the server caps the page size regardless of what the client asks for.
- [ ] WHEN `?por_pagina=abc` or a page number beyond the last is requested THE SYSTEM SHALL respond `200` with the default page size and the last valid page, never `500`.
- [ ] WHEN `POST /casos/<uuid>/borrar/` is sent by the owner THE SYSTEM SHALL set `deleted_at`, keep the row in the database, and make the case return `404` afterwards.

**Verify**

```powershell
uv run pytest tests/web/test_listado.py tests/web/test_aislamiento.py -q
if ($LASTEXITCODE -ne 0) { throw 'el listado o su aislamiento fallan' }   # expect: exit 0, 0 failed, 0 skipped

# El borrado es suave en todas partes: ninguna vista llama a delete() sobre un Caso.
$borradosDuros = Select-String -Path (Get-ChildItem 'apps/analisis' -Recurse -Filter '*.py' -File).FullName -Pattern '\.delete\(\)' -ErrorAction SilentlyContinue
if ($borradosDuros) { throw "hay un borrado duro en apps/analisis: $($borradosDuros.Line -join ' | ')" }

uv run pytest tests/web -q
if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q
if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A
git commit -m "paso 15: listado de casos con busqueda, filtro, orden, vacio y paginacion con tope"
git tag step-15-listado
```

---

#### Paso 16 — `LlamadaLLM` y tope de gasto comprobado **antes** de llamar

**Do**

**Este paso va antes que el paso 17 y el orden no es negociable.** Un tope que se añade después de que
la capa de IA funcione es un tope que nunca se ha probado en el único camino que importa: el de la
petición que sí iba a gastar. Aquí se construye el freno, con su prueba, y solo después se conecta el
motor que hay que frenar.

- `apps/ia/__init__.py`, `apps/ia/apps.py` — `IaConfig`, `label = "ia"`.
- `apps/ia/models.py` — el modelo `LlamadaLLM` **tal cual está en §4.4**, con `proposito`, los cuatro
  contadores de tokens y `coste_eur`.
- `apps/ia/cuota.py` — dos funciones y una excepción:
  - `gasto_del_mes(usuario) -> Decimal` — suma `coste_eur` de las `LlamadaLLM` del usuario en el mes
    natural en curso, apoyándose en el índice compuesto `(usuario, creada_el)` de §4.3.
  - `comprobar_cuota(usuario)` — levanta `CuotaSuperada` si `gasto_del_mes(usuario)` alcanza o supera
    `usuario.tope_gasto_mensual_eur`. **Se llama antes de construir el cliente**, no dentro de él.
  - `coste_de(usage, modelo) -> Decimal` — calcula el coste **a partir del uso reportado por el
    proveedor** y las tarifas de la configuración (§10). No cuenta tokens: los recibe.
- `apps/ia/registro.py` — `registrar_llamada(...)`, el único escritor de `LlamadaLLM`.
- `apps/ia/admin.py` — registra `LlamadaLLM` en solo lectura: es un registro contable, no un formulario.
- `config/settings/base.py` — `"apps.ia"` en `INSTALLED_APPS`.
- `tests/web/test_cuota.py` — **la prueba central de este paso usa un doble de cliente que lanza
  `AssertionError` si alguien lo llama.** Si la cuota funciona, ese doble no se toca nunca, y esa es la
  forma de comprobar "antes de cualquier llamada al proveedor" en el medio donde es observable.

**Done when**

- [ ] WHEN a user whose spend for the current month has reached `tope_gasto_mensual_eur` triggers a request that would call the model THE SYSTEM SHALL reject it **before any call to the provider**, with **zero** new `LlamadaLLM` rows and zero recorded spend.
- [ ] WHEN that rejection happens THE SYSTEM SHALL still complete the analysis and persist the case — the cap disables the AI section, it never blocks the product.
- [ ] WHEN a call completes THE SYSTEM SHALL persist one `LlamadaLLM` row whose four token counters come from the provider's reported `usage`, never from a local count.
- [ ] WHEN `coste_de` is given a usage object THE SYSTEM SHALL compute the cost from the configured rates, and with rates unset SHALL yield `0` rather than raising.
- [ ] WHEN a user is exactly `0.01 €` below the cap THE SYSTEM SHALL allow the call, and when exactly at the cap THE SYSTEM SHALL reject it — the boundary is inclusive on the rejection side.
- [ ] WHEN spend is summed THE SYSTEM SHALL count only rows of the current calendar month and only those belonging to that user.

**Verify**

```powershell
uv run python manage.py makemigrations ia
if ($LASTEXITCODE -ne 0) { throw 'makemigrations falla' }                # expect: exit 0
uv run python manage.py makemigrations --check --dry-run
if ($LASTEXITCODE -ne 0) { throw "quedan cambios de modelo sin migrar (codigo $LASTEXITCODE)" }   # expect: exit 0
uv run python manage.py migrate
if ($LASTEXITCODE -ne 0) { throw 'migrate falla' }                       # expect: exit 0

uv run pytest tests/web/test_cuota.py -q
if ($LASTEXITCODE -ne 0) { throw 'el tope de gasto falla' }              # expect: exit 0, 0 failed, 0 skipped

# El coste se calcula sobre el uso REPORTADO: nadie cuenta tokens por su cuenta.
$conteoPropio = Select-String -Path (Get-ChildItem 'apps/ia' -Recurse -Filter '*.py' -File).FullName -Pattern 'count_tokens|len\(.*split\(\)\)|tiktoken' -ErrorAction SilentlyContinue
if ($conteoPropio) { throw 'apps/ia estima tokens por su cuenta; deben venir del proveedor' }

uv run pytest tests/web -q
if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q
if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A
git commit -m "paso 16: LlamadaLLM y tope de gasto comprobado antes de llamar al proveedor"
git tag step-16-gasto
git ls-files --error-unmatch apps/ia/models.py apps/ia/cuota.py
if ($LASTEXITCODE -ne 0) { throw 'el freno de gasto no ha quedado versionado' }
```

---

#### Paso 17 — Capa de IA en la vista: degradación silenciosa y llamada registrada

**Do**

Aquí se enchufa la capa de IA, y es donde el principio rector deja de ser una frase y pasa a ser
código: **el motor calcula; el modelo explica, fundamenta y puede sugerir, pero nunca decide y nunca
escribe un número.** Cuando `services.py` llama al modelo, el `AnalysisResult` ya está calculado
entero. La explicación se añade encima y no puede modificar nada de lo anterior.

- `apps/analisis/services.py` — `crear_caso` pasa a: (1) **comprobar la cuota del paso 16**;
  (2) si hay margen, leer `settings.ANTHROPIC_API_KEY` y `settings.ANTHROPIC_MODEL` y llamar a
  `ai.claude_client.explain_analysis(result, model=...)`; (3) registrar la `LlamadaLLM` con el uso
  reportado y `proposito="explicacion"`. Este es **el único punto del proyecto que conoce a la vez
  Django y la capa de IA**: `ai/` sigue sin importar Django (paso 8, frontera de §3). Si
  `explain_analysis` devuelve `None`, el caso se persiste sin explicación y `has_ai_explanation` queda
  en `False`. Se emite un evento de `structlog` diciendo si hubo explicación, y cuando no la hubo, de
  qué categoría fue el fallo.
- `templates/analisis/detalle.html` — la sección de IA declara su ausencia con un texto explícito
  cuando no hay explicación, nunca deja un hueco. Cuando la hay, muestra también el modelo y la
  versión de prompt con que se redactó.
- `tests/web/test_ia_degradacion.py` — cubre las **cinco** rutas de degradación con dobles, **sin
  tocar la red**: sin clave, sin modelo, cuota superada, cliente que lanza, y borrador que no pasa el
  validador.

**Done when**

- [ ] WHEN `ANTHROPIC_API_KEY` is unset THE SYSTEM SHALL complete the analysis, respond `302`, persist `has_ai_explanation=False` and make no network call.
- [ ] WHEN `ANTHROPIC_API_KEY` is set but `ANTHROPIC_MODEL` is unset THE SYSTEM SHALL behave identically and SHALL make no network call — the model is never discovered at runtime (paso 8).
- [ ] WHEN the user's monthly cap is already reached THE SYSTEM SHALL behave identically, SHALL make no network call and SHALL write no `LlamadaLLM` row (paso 16).
- [ ] WHEN the injected client raises THE SYSTEM SHALL still respond `302`, persist the case without an explanation, and record one `LlamadaLLM` row whose `error` names the failure category and whose cost is `0`.
- [ ] WHEN the model returns a draft citing a source id the engine did not emit THE SYSTEM SHALL persist the case **without** that explanation, because `AnalysisResult` cannot be constructed with it.
- [ ] WHEN a valid draft is returned THE SYSTEM SHALL persist `has_ai_explanation=True`, record one `LlamadaLLM` with `proposito="explicacion"` and the provider's reported token counts, and render the explanation with its model id and prompt version.

**Verify**

```powershell
uv run pytest tests/web/test_ia_degradacion.py -q
if ($LASTEXITCODE -ne 0) { throw 'la degradacion de la capa de IA falla' }   # expect: exit 0, 0 failed, 0 skipped

# services.py es el UNICO punto que junta Django y la capa de IA.
$puentes = Select-String -Path (Get-ChildItem 'ai' -Recurse -Filter '*.py' -File).FullName -Pattern '(?m)^\s*(from|import)\s+django' -ErrorAction SilentlyContinue
if ($puentes) { throw 'ai/ ha empezado a importar Django' }
if ((Get-Content -Raw 'apps/analisis/views.py') -match 'claude_client') { throw 'la vista llama a la capa de IA; debe pasar por services.py' }

# La cuota se comprueba ANTES: services.py invoca comprobar_cuota antes que explain_analysis.
$src = Get-Content -Raw 'apps/analisis/services.py'
if ($src.IndexOf('comprobar_cuota') -lt 0) { throw 'services.py no comprueba la cuota' }
if ($src.IndexOf('comprobar_cuota') -gt $src.IndexOf('explain_analysis')) { throw 'la cuota se comprueba DESPUES de llamar al modelo' }

uv run pytest tests/web -q
if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q
if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A
git commit -m "paso 17: explicacion de IA aditiva, con degradacion silenciosa y llamada registrada"
git tag step-17-ia
```

---

#### Paso 18 — Completar el frontmatter de las 9 fichas del corpus

**Do**

**Este paso es contenido, no código, y va antes del indexador por un motivo concreto:** el corpus real
no cumple todavía el contrato que el paso 19 va a exigir. Sus fichas llevan hoy
`titulo`, `fecha_creacion`, `origen`, `fuente_primaria`, `tipo`, `usar_en` y `enlaces` —y ni siquiera
las siete en todas—, mientras que `Ficha` (§4) necesita además rango normativo, clase, localizador
tipado y fecha de verificación. Indexar antes de completarlas haría fallar el paso 19 contra el
repositorio del propio usuario.

**Los siete campos actuales se conservan.** Son suyos, sirven a su forma de trabajar en Obsidian y no
se tocan; dos de ellos ya alimentan el índice directamente: `titulo` → `Ficha.titulo` y
`fuente_primaria` → `Ficha.cita`.

**La jurisdicción no se escribe: se deduce de la ruta**, porque el corpus ya está organizado por
jurisdicción. Un campo explícito en el frontmatter la sobrescribe cuando hace falta.

| Directorio | `jurisdiccion` |
|---|---|
| `jurisdictions/spain/` | `ES` |
| `jurisdictions/germany/` | `DE` |
| `jurisdictions/eu/` | `EU` |
| `frameworks/` | `OECD` |
| `processes/` | sin valor por defecto — **la ficha debe declararlo en su frontmatter** |

**`documentation/tax-research/README.md` queda fuera del barrido.** Es el índice del corpus, no una
ficha, y no tiene frontmatter. **El criterio de exclusión es la ausencia de frontmatter**, no el
nombre: un fichero sin bloque YAML de cabecera no es una ficha y se omite en silencio. Se elige así
para que añadir un segundo índice o un borrador no obligue a tocar el indexador.

Añadir a cada una de las **9 fichas** los campos que faltan, con estos valores. El vocabulario de
`clase`, `tipo_localizador` y `confianza_verificacion` es el que ya existe en `tp_domain/sources.py`
(`SourceKind`, `LocatorType`, `VerificationConfidence`); no se inventa ninguno.

| # | Ficha (bajo `documentation/tax-research/`) | `clase` | `rango_normativo` | `tipo_localizador` |
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

Reglas para los dos campos que quedan, y **ninguna admite inventar un identificador**:

- **`localizador`.** Las fichas 1, 3 y 6 ya tienen entrada en el registro cerrado de
  `tp_domain/sources.py` (`es-lis-art18-4`, `de-astg-1-3a`, `oecd-tpg-2022-cap3`): **se copia el
  `locator` de allí, literal**, para que ficha y fuente resuelvan al mismo sitio. Las otras seis toman
  el identificador que **su propio cuerpo ya cita**. Si una no tiene identificador público resoluble,
  su `tipo_localizador` es `offline` y el `localizador` es la referencia del documento tal como la
  ficha la nombra.
- **`confianza_verificacion`.** `primary_source_verified` solo si la ficha se leyó contra su texto
  oficial; `directed_reading` en cualquier otro caso. **Se marca lo que de verdad pasó**: una fecha de
  verificación sola no debe leerse como más certeza de la que hubo.
- **`verificada_el`.** La fecha en que se comprobó ese localizador. Para las tres que vienen del
  registro, la misma que ya lleva `tp_domain/sources.py`.

Cuatro fichas no tienen hoy `fuente_primaria` —`criterios-seleccion-comparables`,
`directiva-intereses-canones-2003-49`, `doctrina-teac-bilateralidad-y-servicios` y
`propuesta-directiva-tp-2023-retirada`, que lleva `COM(2023) 529` en el cuerpo y `estado` en el
frontmatter en lugar de `fuente_primaria`— y dos no tienen
`tipo` —`ocde-directrices-2022-...` y `safe-harbours-y-htvi`—. Se completan también, porque el índice
los necesita.

**Ficheros**
- Las 9 fichas `.md` bajo `documentation/tax-research/` — se edita **solo el frontmatter**; el cuerpo
  no se toca
- `documentation/tax-research/README.md` — **no se toca**: es el índice y se excluye por no tener
  frontmatter

**Done when**

- [ ] WHEN every markdown file under the research directory that carries YAML frontmatter is read THE SYSTEM SHALL find exactly 9 of them, each with `titulo`, `fuente_primaria`, `rango_normativo`, `clase`, `tipo_localizador`, `localizador`, `verificada_el` and `confianza_verificacion` present and non-empty.
- [ ] WHEN `documentation/tax-research/README.md` is read THE SYSTEM SHALL find no YAML frontmatter, so the exclusion criterion is a property of the file and not a hardcoded name.
- [ ] WHEN each ficha's `clase`, `tipo_localizador` and `confianza_verificacion` are read THE SYSTEM SHALL find every value inside the vocabulary `tp_domain/sources.py` already defines.
- [ ] WHEN the three fichas that already have an entry in the closed source registry are read THE SYSTEM SHALL find their `localizador` identical, character for character, to the `locator` of that entry.
- [ ] WHEN the seven pre-existing frontmatter keys are read THE SYSTEM SHALL find them unchanged — this step only adds keys, it removes and rewrites none.

**Verify**

```powershell
uv run python -c "import frontmatter, pathlib; req={'titulo','fuente_primaria','rango_normativo','clase','tipo_localizador','localizador','verificada_el','confianza_verificacion'}; todos=sorted(pathlib.Path('documentation/tax-research').rglob('*.md')); fichas=[p for p in todos if frontmatter.load(p).metadata]; assert len(fichas)==9, [str(x) for x in fichas]; malas={str(p): sorted(req - set(frontmatter.load(p).metadata)) for p in fichas if req - set(frontmatter.load(p).metadata)}; assert not malas, malas; print('9 fichas completas')"; if ($LASTEXITCODE -ne 0) { throw 'alguna ficha no cumple el contrato del indice' }
uv run python -c "import frontmatter, pathlib; p=pathlib.Path('documentation/tax-research/README.md'); assert not frontmatter.load(p).metadata, 'README.md tiene frontmatter y dejaria de excluirse'; print('README excluido por ausencia de frontmatter')"; if ($LASTEXITCODE -ne 0) { throw 'el criterio de exclusion del README ya no se cumple' }
uv run python -c "import frontmatter, pathlib; from tp_domain.models import SourceKind, LocatorType, VerificationConfidence; ok_c={e.value for e in SourceKind}; ok_l={e.value for e in LocatorType}; ok_v={e.value for e in VerificationConfidence}; malas=[]; [malas.append(str(p)) for p in pathlib.Path('documentation/tax-research').rglob('*.md') if frontmatter.load(p).metadata and not (frontmatter.load(p)['clase'] in ok_c and frontmatter.load(p)['tipo_localizador'] in ok_l and frontmatter.load(p)['confianza_verificacion'] in ok_v)]; assert not malas, malas; print('vocabulario OK')"; if ($LASTEXITCODE -ne 0) { throw 'alguna ficha usa un valor fuera del vocabulario del dominio' }
uv run python -c "import frontmatter, pathlib; from tp_domain.sources import SOURCE_REGISTRY; pares={'jurisdictions/spain/art18-lis-operaciones-vinculadas.md':'es-lis-art18-4','jurisdictions/germany/astg-rango-intercuartilico-ajuste-mediana.md':'de-astg-1-3a','frameworks/ocde-directrices-2022-marcos-riesgo-dempe-servicios.md':'oecd-tpg-2022-cap3'}; malas={r: (frontmatter.load(pathlib.Path('documentation/tax-research')/r)['localizador'], SOURCE_REGISTRY[i].locator) for r, i in pares.items() if frontmatter.load(pathlib.Path('documentation/tax-research')/r)['localizador'] != SOURCE_REGISTRY[i].locator}; assert not malas, malas; print('localizadores alineados con el registro')"; if ($LASTEXITCODE -ne 0) { throw 'un localizador de ficha no coincide con el del registro cerrado' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A
git commit -m "paso 18: frontmatter completo en las 9 fichas del corpus"
git tag step-18-frontmatter
git ls-files --error-unmatch documentation/tax-research/jurisdictions/spain/art18-lis-operaciones-vinculadas.md
if ($LASTEXITCODE -ne 0) { throw 'las fichas no han quedado versionadas' }
```

---

#### Paso 19 — `Ficha`: índice citable del corpus, reconstruible desde los `.md`

**Do**

El corpus son **9 fichas** `.md` con frontmatter —más un `README.md` sin frontmatter, que se excluye—
que **el usuario escribe en Obsidian**, y que el paso 18 acaba de completar. Este paso los convierte en un índice consultable **sin dejar de ser ficheros**: el `.md` en
disco es la fuente de verdad y la tabla se reconstruye desde él.

- `apps/corpus/__init__.py`, `apps/corpus/apps.py` — `CorpusConfig`, `label = "corpus"`.
- `apps/corpus/models.py` — el modelo `Ficha` **tal cual está en §4.4**, con el vocabulario reutilizado
  de `tp_domain/sources.py` (`SourceKind`, `LocatorType`, `VerificationConfidence`).
- `apps/corpus/indexador.py` — recorre `documentation/tax-research/**/*.md`, lee el frontmatter con
  `frontmatter.load`, calcula el SHA-256 del fichero y construye las filas. **Omite todo fichero sin
  frontmatter** —así queda fuera `README.md`, que es el índice del corpus y no una ficha—, y deduce la
  jurisdicción de la ruta según la tabla del paso 18. **Resuelve la ruta absoluta y comprueba que sigue
  dentro del directorio del corpus**; cualquier `..`, ruta absoluta o enlace que se salga se rechaza
  sin leer nada.
- `apps/corpus/management/commands/reindexar_corpus.py` — vacía la tabla y la reconstruye.
  **Idempotente**: ejecutarlo dos veces deja exactamente el mismo estado.
- `apps/corpus/admin.py` — registra `Ficha` **en solo lectura**: una edición aquí se perdería en el
  siguiente reindexado, y una tabla que miente es peor que una tabla que no existe.
- `config/settings/base.py` — `"apps.corpus"` en `INSTALLED_APPS`.
- `tests/web/test_corpus_indice.py`.

**Done when**

- [ ] WHEN `uv run python manage.py reindexar_corpus` runs THE SYSTEM SHALL exit 0 and leave one `Ficha` row per markdown file under `documentation/tax-research/` that carries YAML frontmatter, which is 9 — `README.md` has none and is skipped.
- [ ] WHEN the command runs twice in a row THE SYSTEM SHALL leave the identical set of rows, with identical `hash_fichero` values — it is idempotent.
- [ ] WHEN a `.md` file changes on disk and the command is re-run THE SYSTEM SHALL update that row's `hash_fichero`, so drift between disk and index is detectable.
- [ ] WHEN a ficha's frontmatter is missing a required key THE SYSTEM SHALL fail loudly naming the file and the key, and SHALL NOT leave the table half-rebuilt.
- [ ] WHEN `Ficha` is opened in the admin THE SYSTEM SHALL present every field read-only — the file on disk is the source of truth.
- [ ] WHEN a source id emitted by the engine is looked up in `Ficha` THE SYSTEM SHALL resolve without a translation table, because both use the same identifier.

**Verify**

```powershell
uv run python manage.py makemigrations corpus
if ($LASTEXITCODE -ne 0) { throw 'makemigrations falla' }                # expect: exit 0
uv run python manage.py migrate
if ($LASTEXITCODE -ne 0) { throw 'migrate falla' }                       # expect: exit 0

uv run python manage.py reindexar_corpus
if ($LASTEXITCODE -ne 0) { throw 'el reindexado falla' }                 # expect: exit 0
uv run python manage.py reindexar_corpus
if ($LASTEXITCODE -ne 0) { throw 'el reindexado no es idempotente' }     # expect: exit 0 en la segunda pasada

# El indice coincide EXACTAMENTE con los ficheros que hay en disco.
uv run python -c "import os; os.environ['DJANGO_SETTINGS_MODULE']='config.settings.local'; import django; django.setup(); from pathlib import Path; from apps.corpus.models import Ficha; import frontmatter; n=len([q for q in Path('documentation/tax-research').rglob('*.md') if frontmatter.load(q).metadata]); m=Ficha.objects.count(); assert m==n, (m, n); print('corpus indexado OK', n)"
if ($LASTEXITCODE -ne 0) { throw 'el indice no coincide con los ficheros en disco' }   # expect: exit 0

uv run pytest tests/web/test_corpus_indice.py -q
if ($LASTEXITCODE -ne 0) { throw 'las pruebas del indice fallan' }       # expect: exit 0, 0 failed, 0 skipped
uv run pytest tests/web -q
if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q
if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A
git commit -m "paso 19: indice citable del corpus, reconstruible desde los ficheros .md"
git tag step-19-fichas
```

---

#### Paso 20 — Publicación del corpus y enlace desde las fuentes citadas

**Do**

- `apps/corpus/views.py` y `apps/corpus/urls.py` — `/fuentes/` (índice, filtrable por jurisdicción
  contra el índice del paso 19) y `/fuentes/<path:ruta>/` (la ficha renderizada). La vista lee la fila
  de `Ficha` para la cabecera —título, rango normativo, cita, pinpoint, localizador, confianza y fecha
  de verificación— y renderiza el cuerpo del `.md` con `Markdown`. La comprobación de que la ruta no
  se sale del corpus la hace `apps/corpus/indexador.py`, escrito en el paso 19; aquí se traduce su
  error a `400` y la ausencia a `404`.
- `templates/corpus/indice.html` y `templates/corpus/ficha.html`.
- `templates/analisis/detalle.html` — cada fuente citada por el motor enlaza a su ficha. El enlace se
  resuelve por identificador, sin tabla de traducción, porque `Ficha.id` es el mismo id que emite
  `tp_domain/sources.py` (§4).
- `tests/web/test_corpus.py`.

**Done when**

- [ ] WHEN `GET /fuentes/` is requested by an authenticated user THE SYSTEM SHALL respond `200` listing one entry per row of `Ficha`, each with its `titulo` and its `rango_normativo`.
- [ ] WHEN `GET /fuentes/jurisdictions/spain/art18-lis-operaciones-vinculadas/` is requested THE SYSTEM SHALL respond `200` containing that ficha's `titulo`, its `cita` and its `verificada_el`.
- [ ] WHEN the requested path does not exist in the corpus THE SYSTEM SHALL respond `404` and read no file.
- [ ] WHEN the requested path contains `..`, is absolute, or resolves outside `documentation/tax-research/` THE SYSTEM SHALL respond `400` and read no file.
- [ ] WHEN a case detail page cites a source THE SYSTEM SHALL render a link to that source's ficha, resolved by the shared identifier.
- [ ] WHEN an anonymous request hits `/fuentes/` THE SYSTEM SHALL respond `302` to `/entrar/` — the corpus is behind the session like everything else.

**Verify**

```powershell
uv run pytest tests/web/test_corpus.py -q
if ($LASTEXITCODE -ne 0) { throw 'la publicacion del corpus falla' }   # expect: exit 0, 0 failed, 0 skipped

uv run pytest tests/web -q
if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q
if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A
git commit -m "paso 20: publicacion del corpus y enlace desde las fuentes citadas"
git tag step-20-corpus-web
```

---

#### Paso 21 — `UnidadEstudio`: módulo de estudio, separado de las fichas

**Do**

Contenido didáctico propio, en una entidad **separada de `Ficha`**. La distinción es la que sostiene
todo lo demás: **una ficha es fuente citable con rango normativo; una unidad de estudio es material de
aprendizaje.** Fusionarlas con una bandera acabaría, tarde o temprano, con un informe citando material
de estudio como si fuera Derecho.

- `apps/estudio/__init__.py`, `apps/estudio/apps.py` — `EstudioConfig`, `label = "estudio"`.
- `apps/estudio/models.py` — el modelo `UnidadEstudio` **tal cual está en §4.4**, con su
  `ManyToManyField` hacia `Ficha`.
- `apps/estudio/admin.py` — registro **editable**: al contrario que `Ficha`, esto se escribe desde el
  panel. Es la segunda vez que el panel se cobra (§8): un jurista no-ingeniero escribe y publica su
  material sin tocar el repositorio.
- `apps/estudio/views.py`, `apps/estudio/urls.py` — `/estudio/` (índice de las publicadas, en su orden)
  y `/estudio/<slug>/` (la unidad, con su cuerpo Markdown renderizado y los enlaces a las fichas que
  estudia).
- `templates/estudio/indice.html`, `templates/estudio/unidad.html`.
- `config/settings/base.py` — `"apps.estudio"` en `INSTALLED_APPS`.
- `tests/web/test_estudio.py` — incluye **la prueba de la invariante**: ninguna `UnidadEstudio` es
  alcanzable desde el registro de fuentes citables ni aparece en un informe.

**Done when**

- [ ] WHEN `GET /estudio/` is requested THE SYSTEM SHALL list only units with `publicada=True`, ordered by `orden` and then `titulo`.
- [ ] WHEN a unit has `publicada=False` and its slug is requested directly THE SYSTEM SHALL respond `404`.
- [ ] WHEN a unit linked to two fichas is rendered THE SYSTEM SHALL show a link to each of them.
- [ ] WHEN `tp_domain.sources.SOURCE_REGISTRY` is inspected THE SYSTEM SHALL contain no identifier belonging to any `UnidadEstudio` — study material is never a citable source.
- [ ] WHEN a report is generated for any case THE SYSTEM SHALL contain no `UnidadEstudio` title or slug anywhere in its text.
- [ ] WHEN a unit is created from the admin THE SYSTEM SHALL persist it — unlike `Ficha`, this content is authored in the panel, not on disk.

**Verify**

```powershell
uv run python manage.py makemigrations estudio
if ($LASTEXITCODE -ne 0) { throw 'makemigrations falla' }                # expect: exit 0
uv run python manage.py migrate
if ($LASTEXITCODE -ne 0) { throw 'migrate falla' }                       # expect: exit 0

uv run pytest tests/web/test_estudio.py -q
if ($LASTEXITCODE -ne 0) { throw 'el modulo de estudio falla' }          # expect: exit 0, 0 failed, 0 skipped

# La invariante: el motor no puede citar material de estudio.
$fugas = Select-String -Path (Get-ChildItem 'tp_domain','infrastructure' -Recurse -Filter '*.py' -File).FullName -Pattern 'UnidadEstudio|apps\.estudio' -ErrorAction SilentlyContinue
if ($fugas) { throw 'el dominio o el informe conocen UnidadEstudio; el material de estudio no es citable' }

uv run pytest tests/web -q
if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q
if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A
git commit -m "paso 21: modulo de estudio, entidad separada de las fichas"
git tag step-21-estudio
```

---

#### Paso 22 — `CasoContrastado`: biblioteca curada de precedentes

**Do**

- `apps/analisis/models.py` — se añade el modelo `CasoContrastado` **tal cual está en §4.4**.
- `apps/analisis/admin.py` — registro con una acción de administración *"Curar como precedente"* sobre
  un `Caso`: **copia** su `payload` congelado a un `CasoContrastado` nuevo en borrador, con
  `caso_origen` apuntando al original y `curado_por` al administrador. **Curar no desprivatiza**: el
  caso original sigue siendo de su dueño y sigue filtrado por la guarda.
- `apps/analisis/views.py`, `apps/analisis/urls.py` — `/contrastados/` y `/contrastados/<slug>/`,
  visibles para **toda cuenta autenticada**, mostrando solo los publicados. Reutilizan las plantillas
  parciales del paso 12 para pintar el rango y las jurisdicciones, porque un precedente se lee igual
  que un caso.
- `templates/analisis/contrastados.html`, `templates/analisis/contrastado.html`.
- `tests/web/test_contrastados.py`.

**Done when**

- [ ] WHEN a `CasoContrastado` is published THE SYSTEM SHALL make it visible at `/contrastados/<slug>/` to **every** authenticated user, not only its curator.
- [ ] WHEN a `CasoContrastado` has `publicado=False` THE SYSTEM SHALL respond `404` at its slug for a non-staff user.
- [ ] WHEN a case is curated THE SYSTEM SHALL copy its `payload` and SHALL leave the original `Caso` unchanged and still private — requesting it as another user still returns `404`.
- [ ] WHEN the origin case is later soft-deleted THE SYSTEM SHALL keep the published precedent readable, with its frozen `payload` intact.
- [ ] WHEN a `CasoContrastado` is rendered THE SYSTEM SHALL show its `comentario_curador` — a precedent without the reason it is one is just another row.
- [ ] WHEN an anonymous request hits `/contrastados/` THE SYSTEM SHALL respond `302` to `/entrar/`.

**Verify**

```powershell
uv run python manage.py makemigrations analisis
if ($LASTEXITCODE -ne 0) { throw 'makemigrations falla' }                # expect: exit 0
uv run python manage.py makemigrations --check --dry-run
if ($LASTEXITCODE -ne 0) { throw "quedan cambios de modelo sin migrar (codigo $LASTEXITCODE)" }   # expect: exit 0
uv run python manage.py migrate
if ($LASTEXITCODE -ne 0) { throw 'migrate falla' }                       # expect: exit 0

uv run pytest tests/web/test_contrastados.py tests/web/test_aislamiento.py -q
if ($LASTEXITCODE -ne 0) { throw 'la biblioteca de precedentes o el aislamiento fallan' }   # expect: exit 0, 0 failed, 0 skipped

uv run pytest tests/web -q
if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q
if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A
git commit -m "paso 22: biblioteca curada de precedentes, copiada y congelada"
git tag step-22-contrastados
```

---

#### Paso 23 — Arnés de evaluación: conjunto dorado, puntuadores y puerta de CI

**Do**

Sin esto, los prompts se petrifican: nadie se atreve a tocarlos porque no hay forma de saber si el
cambio mejora o empeora, y la regresión la acaba descubriendo el usuario en un informe.

- `evaluacion/casos/*.json` — el **conjunto dorado, en control de versiones**. Cada fichero: un
  `AnalysisResult` de entrada congelado y las propiedades que la explicación debe cumplir. Vive en el
  repositorio para que un cambio del conjunto se revise en un *pull request*, igual que el código.
- `apps/evaluacion/models.py` — `CasoEvaluacion` y `EjecucionEvaluacion` **tal cual están en §4.4**,
  con `sha_commit`.
- `apps/evaluacion/management/commands/reindexar_evaluacion.py` — reconstruye `CasoEvaluacion` desde los
  `.json`, idempotente, igual que `reindexar_corpus`.
- `apps/evaluacion/puntuadores.py` — los puntuadores **de lo más barato a lo más caro**, y se paran en
  el primero que decide: (1) comprobaciones deterministas —fuentes citadas dentro del registro emitido,
  ninguna cifra nueva que no esté en el `AnalysisResult`, extensión dentro de `MIN_WORDS`/`MAX_WORDS`—;
  (2) coincidencias léxicas sobre las referencias legales; (3) y solo si las anteriores no deciden, un
  juicio del modelo. **El orden es la política de coste**: la mayoría de los casos se resuelven en la
  capa 1, que no cuesta nada.
- **La línea base se fija en este mismo paso**, con `evaluar --fijar-linea-base`, antes de la primera
  comparación: §4 declara que existe exactamente una fila con `es_linea_base = True`, y sin esta
  invocación esa invariante no la establece nada y `--contra-linea-base` saldría siempre con 2.
- `apps/evaluacion/management/commands/evaluar.py` — ejecuta el conjunto activo, registra una
  `EjecucionEvaluacion` con `sha_commit` (de `git rev-parse HEAD`), tasa de acierto, coste y latencias,
  y una `LlamadaLLM` por llamada con `proposito="evaluacion"` (§4). Acepta **tres** opciones:
  `--fijar-linea-base` marca la ejecución como línea base; `--contra-linea-base` **sale 1 si la tasa
  de acierto es menor que la de la línea base**, 0 si es igual o mayor, y 2 si no hay línea base; y
  `--autocomprobar-regresion` ejecuta el arnés con puntuadores dobles contra una línea base
  deliberadamente inalcanzable y **debe salir con 1**. Esta tercera existe para que «la puerta puede
  fallar» sea una comprobación y no una afirmación: sin ella, un gate que nunca ha fallado es
  indistinguible de uno que no puede fallar.
- `config/settings/base.py` — `"apps.evaluacion"` en `INSTALLED_APPS`.
- `tests/web/test_evaluacion.py` — con dobles, sin red.

**Done when**

- [ ] WHEN `uv run python manage.py reindexar_evaluacion` runs twice THE SYSTEM SHALL leave the identical set of `CasoEvaluacion` rows — idempotent, like the corpus reindex.
- [ ] WHEN `evaluar --contra-linea-base` runs and the hit rate equals or exceeds the baseline THE SYSTEM SHALL exit **0**.
- [ ] WHEN the hit rate falls below the baseline THE SYSTEM SHALL exit **1** specifically — not merely non-zero, so a usage error cannot pass for a regression.
- [ ] WHEN no baseline row exists THE SYSTEM SHALL exit **2** with a message saying so, distinguishable from both a pass and a regression.
- [ ] WHEN an `EjecucionEvaluacion` is written THE SYSTEM SHALL record `sha_commit`, `coste_total_eur`, `latencia_p50_ms` and `latencia_p95_ms` next to `tasa_acierto` — a precision gain that triples cost is a decision, not an improvement.
- [ ] WHEN a case is decided by the deterministic scorer THE SYSTEM SHALL NOT invoke any more expensive scorer for that case, and SHALL record zero provider calls for it.

**Verify**

```powershell
uv run python manage.py makemigrations evaluacion
if ($LASTEXITCODE -ne 0) { throw 'makemigrations falla' }                # expect: exit 0
uv run python manage.py migrate
if ($LASTEXITCODE -ne 0) { throw 'migrate falla' }                       # expect: exit 0

uv run python manage.py reindexar_evaluacion
if ($LASTEXITCODE -ne 0) { throw 'el reindexado del conjunto dorado falla' }      # expect: exit 0
uv run python manage.py reindexar_evaluacion
if ($LASTEXITCODE -ne 0) { throw 'el reindexado no es idempotente' }             # expect: exit 0

uv run pytest tests/web/test_evaluacion.py -q
if ($LASTEXITCODE -ne 0) { throw 'el arnes de evaluacion falla' }                # expect: exit 0, 0 failed, 0 skipped

# La puerta PUEDE fallar, y falla con el codigo 1 exacto. Se comprueba con dobles,
# sobre una linea base artificialmente alta, y se restaura despues.
uv run python manage.py evaluar --fijar-linea-base
if ($LASTEXITCODE -ne 0) { throw 'no se ha podido fijar la linea base' }   # expect: exit 0

uv run python manage.py evaluar --contra-linea-base
if ($LASTEXITCODE -ne 0) { throw 'la comparacion contra la linea base recien fijada deberia salir 0' }

uv run python manage.py evaluar --autocomprobar-regresion
$codigo = $LASTEXITCODE
if ($codigo -ne 1) { throw "con una tasa por debajo de la linea base se esperaba codigo 1, obtenido $codigo" }
# 1 = regresion (la propiedad) · 2 = no hay linea base · 0 = no detecta nada

uv run pytest tests/web -q
if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q
if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A
git commit -m "paso 23: arnes de evaluacion con conjunto dorado, puntuadores por coste y puerta de CI"
git tag step-23-evaluacion
git ls-files evaluacion/casos | Measure-Object -Line | ForEach-Object { if ($_.Lines -lt 1) { throw 'el conjunto dorado no ha quedado versionado' } }
```

---

#### Paso 24 — Copia de seguridad y restauración verificada por recuento de filas

**Do**

**Una copia sin restaurar no es una copia.** Un fichero SQLite en disco sin copia es un fichero que un
día no está, y con él se van todos los casos, todo el gasto registrado y toda la biblioteca de
precedentes. Esto está en la v1, no en el backlog: es la mitigación del riesgo 3 de §20.2.

- `apps/comun/management/commands/copia_seguridad.py` — usa la **API de copia en línea de SQLite**
  (`sqlite3.Connection.backup`), no una copia de fichero: copiar `db.sqlite3` con el proceso escribiendo
  produce un fichero corrupto sin avisar. Escribe
  `copias/tpip-<AAAAMMDD-HHMMSS>.sqlite3` y, junto a él, `copias/<mismo nombre>.recuentos.json` con el
  número de filas de **cada una de las ocho tablas** de §4. Ese fichero de recuentos es lo que convierte
  la restauración en verificable.
- `apps/comun/management/commands/restaurar_copia.py` — recibe la ruta de una copia y una ruta de
  destino, restaura, y **compara los recuentos de las ocho tablas contra el `.recuentos.json`**. Sale
  0 si todos coinciden, **1 si alguno difiere**, y 2 si la copia o su fichero de recuentos no existen.
- `.gitignore` — `copias/` ya está fuera del repositorio; se confirma que sigue así (las copias
  contienen datos, no código).
- `tests/web/test_copia.py` — crea filas en las ocho tablas, hace la copia, restaura en un directorio
  temporal y compara.

**Done when**

- [ ] WHEN `uv run python manage.py copia_seguridad` runs THE SYSTEM SHALL exit 0 and write both a `.sqlite3` file and its `.recuentos.json` sibling under `copias/`.
- [ ] WHEN the backup is taken THE SYSTEM SHALL use SQLite's online backup API, never a file copy — a file copy of a database being written is silently corrupt.
- [ ] WHEN `restaurar_copia` restores into a clean directory THE SYSTEM SHALL exit 0 and the row count of **each of the eight tables** SHALL equal the count recorded at backup time.
- [ ] WHEN a restored table's row count differs from the recorded one THE SYSTEM SHALL exit **1** specifically, naming the table and both numbers.
- [ ] WHEN the named backup or its counts file does not exist THE SYSTEM SHALL exit **2**, distinguishable from a count mismatch.
- [ ] WHEN `copias/` is checked against the ignore file THE SYSTEM SHALL find it excluded — backups carry data, not code.

**Verify**

```powershell
uv run python manage.py copia_seguridad
if ($LASTEXITCODE -ne 0) { throw 'la copia de seguridad falla' }         # expect: exit 0

$copia = Get-ChildItem 'copias' -Filter '*.sqlite3' | Sort-Object LastWriteTime | Select-Object -Last 1
if (-not $copia) { throw 'no se ha escrito ninguna copia' }
if (-not (Test-Path ($copia.FullName -replace '\.sqlite3$', '.recuentos.json'))) { throw 'falta el fichero de recuentos' }

# La prueba de verdad: restaurar en limpio y comparar recuentos de las ocho tablas.
$destino = Join-Path $env:TEMP ("tpip-restauracion-" + [guid]::NewGuid().ToString('N'))
uv run python manage.py restaurar_copia --copia $copia.FullName --destino $destino
if ($LASTEXITCODE -ne 0) { throw "la restauracion no coincide en recuentos (codigo $LASTEXITCODE)" }
# expect: exit 0 — 1 seria discrepancia de recuentos; 2, copia inexistente
Remove-Item -Recurse -Force $destino

# La copia esta fuera del repositorio.
git check-ignore -q 'copias'
if ($LASTEXITCODE -ne 0) { throw "copias/ no esta ignorado (codigo $LASTEXITCODE)" }
# expect: exit 0 — 0 = la ruta esta ignorada, que es lo que se quiere; 128 seria error de uso

uv run pytest tests/web/test_copia.py -q
if ($LASTEXITCODE -ne 0) { throw 'las pruebas de copia fallan' }         # expect: exit 0, 0 failed, 0 skipped
uv run pytest tests/domain tests/ai tests/report -q
if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A
git commit -m "paso 24: copia de seguridad en linea y restauracion verificada por recuento de filas"
git tag step-24-copia
```

---

#### Paso 25 — Accesibilidad de las plantillas y aviso de privacidad

**Do**

Los requisitos de §15 se aplican a las plantillas que ya existen, y se cierra el requisito de
transparencia de §8. Este paso no crea páginas nuevas salvo una: corrige y **fija con pruebas** lo que
dejaron los pasos 12, 19, 20 y 21.

- `templates/base.html` — enlace de salto visible al recibir el foco; landmarks completos; y **el aviso
  de privacidad** en el `<footer role="contentinfo">` de toda página autenticada: dice sin eufemismos
  que las cuentas con permiso de administración pueden acceder a los casos de cualquier usuario, para
  qué, y qué se registra de cada llamada al modelo. Enlaza a `/privacidad/`.
- `templates/analisis/form.html` — el mismo aviso, **también junto al formulario de creación**, que es
  el momento en el que el usuario está a punto de escribir el dato. Además: cada `<input>` y `<select>`
  con su `<label for>`; errores referenciados por `aria-describedby`; el bloque general con
  `role="alert"`; los errores como **texto**, nunca solo color.
- `templates/privacidad.html` y su ruta — qué se guarda, dónde, cuánto tiempo y cómo se pide el
  borrado. Es la única página nueva del paso.
- `static/css/app.css` — `:focus-visible` con anillo de `var(--tpip-focus)` de al menos 2px y
  `outline-offset`; objetivos de puntero de 24×24 px CSS como mínimo; el movimiento encapsulado en
  `@media (prefers-reduced-motion: no-preference)`; y las tablas anchas con `overflow-x: auto` en su
  propio contenedor.
- `templates/analisis/detalle.html` — el SVG del rango con `role="img"` y un `<title>` que diga en texto
  lo mismo que el gráfico muestra.
- `tests/web/test_accesibilidad.py`.

**Nota sobre el medio (§9 regla 12):** estas comprobaciones se hacen sobre el **HTML renderizado**, que
es donde son observables. Lo que un análisis estático no puede decidir —orden de tabulación real,
anuncios de un lector de pantalla, reflujo a 320 px— no se afirma aquí: está en los gates manuales de
§20.1.

**Done when**

- [ ] WHEN any authenticated page is rendered THE SYSTEM SHALL contain the privacy notice in a `<footer role="contentinfo">`, stating that administrators can access any user's cases.
- [ ] WHEN the case creation form is rendered THE SYSTEM SHALL show that same notice next to the form, before the user types anything.
- [ ] WHEN any page is rendered THE SYSTEM SHALL contain `<html lang="es"`, exactly one `<h1`, one `<main`, one `<header`, one `<footer`, and a skip link whose `href` is `#contenido` as the first focusable element.
- [ ] WHEN the form page is rendered THE SYSTEM SHALL emit a `<label for="…">` whose target matches the `id` of every `<input>` and `<select>` on the page — zero unlabelled controls.
- [ ] WHEN the form is rendered after an invalid submission THE SYSTEM SHALL express every error as text inside an element with `role="alert"` or referenced by `aria-describedby`.
- [ ] WHEN a detail page with a range is rendered THE SYSTEM SHALL emit the `<svg` with `role="img"` and a non-empty `<title>`.

**Verify**

```powershell
uv run pytest tests/web/test_accesibilidad.py -q
if ($LASTEXITCODE -ne 0) { throw 'las comprobaciones de accesibilidad fallan' }   # expect: exit 0, 0 failed, 0 skipped

if ((Get-Content -Raw 'static/css/app.css') -notmatch ':focus-visible') { throw 'falta el estilo de foco visible' }
if ((Get-Content -Raw 'static/css/app.css') -notmatch 'prefers-reduced-motion') { throw 'el movimiento no respeta prefers-reduced-motion' }
if ((Get-Content -Raw 'templates/base.html') -notmatch 'role="contentinfo"') { throw 'falta el pie con el aviso de privacidad' }
if (-not (Test-Path 'templates/privacidad.html')) { throw 'falta la pagina de privacidad' }

uv run pytest tests/web -q
if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q
if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A
git commit -m "paso 25: accesibilidad fijada con pruebas y aviso de privacidad visible"
git tag step-25-accesibilidad
```

---

#### Paso 26 — Seguridad, cabeceras y ajustes de producción

**Do**

- `config/settings/production.py` — nuevo: importa de `base`, `DEBUG = False`, exige
  `DJANGO_SECRET_KEY` de la configuración (aquí sí es obligatoria; en `local.py` sigue teniendo su
  valor de desarrollo, de modo que **ningún gate anterior se rompe**, §9 regla 9), lee `ALLOWED_HOSTS`
  de `DJANGO_ALLOWED_HOSTS`, y fija las cabeceras y opciones literales de §14 y §8:
  `SECURE_HSTS_SECONDS = 31536000`, `SECURE_HSTS_INCLUDE_SUBDOMAINS = True`,
  `SECURE_HSTS_PRELOAD = True`, `SECURE_SSL_REDIRECT = True`, `SECURE_CONTENT_TYPE_NOSNIFF = True`,
  `SECURE_REFERRER_POLICY = "same-origin"`, `SESSION_COOKIE_SECURE = True`, `CSRF_COOKIE_SECURE = True`,
  `X_FRAME_OPTIONS = "DENY"`.
- `config/settings/base.py` — WhiteNoise en `MIDDLEWARE`, detrás de `SecurityMiddleware`, y `STORAGES`
  con su backend de estáticos.
- `tests/web/test_seguridad.py` — cabeceras emitidas, CSRF activo (un POST sin token responde `403`), y
  que las marcas seguras de cookie **no** están activas en local, donde no hay TLS.
- `.env.example` — `DJANGO_SECRET_KEY`, `DJANGO_DEBUG` y `DJANGO_ALLOWED_HOSTS` con valores vacíos o
  evidentemente falsos, si el bootstrap no las dejó ya.

**Done when**

- [ ] WHEN `uv run python manage.py check --deploy --settings=config.settings.production` runs with `DJANGO_SECRET_KEY` set THE SYSTEM SHALL exit 0 with zero issues.
- [ ] WHEN `config.settings.production` is imported without `DJANGO_SECRET_KEY` THE SYSTEM SHALL fail at import with an error naming that variable, and SHALL NOT fall back to a default secret.
- [ ] WHEN `POST /casos/` is sent without a CSRF token THE SYSTEM SHALL respond `403` and create zero `Caso` rows.
- [ ] WHEN any response is inspected THE SYSTEM SHALL carry `X-Content-Type-Options: nosniff` and `Referrer-Policy: same-origin`.
- [ ] WHEN local settings are loaded THE SYSTEM SHALL leave `SESSION_COOKIE_SECURE` false — enabling it without TLS would make the application unusable locally.
- [ ] WHEN `uv run python manage.py check` runs with the local settings THE SYSTEM SHALL still exit 0 — the development gate does not regress.

**Verify**

```powershell
uv run pytest tests/web/test_seguridad.py -q
if ($LASTEXITCODE -ne 0) { throw 'las pruebas de seguridad fallan' }   # expect: exit 0, 0 failed, 0 skipped

$env:DJANGO_SECRET_KEY = 'clave-solo-para-esta-comprobacion-no-usar'
uv run python manage.py check --deploy --settings=config.settings.production
if ($LASTEXITCODE -ne 0) { throw 'check --deploy senala problemas' }   # expect: exit 0, cero avisos
Remove-Item Env:\DJANGO_SECRET_KEY

# Sin clave, produccion NO arranca. No basta con "sale distinto de cero" —un error de uso
# tambien lo haria—: se comprueba que el fallo NOMBRA la variable que falta.
$salida = uv run python -c "import os; os.environ.pop('DJANGO_SECRET_KEY', None); os.environ['DJANGO_SETTINGS_MODULE']='config.settings.production'; import django; django.setup(); print('ARRANCO SIN CLAVE')" 2>&1 | Out-String
if ($salida -match 'ARRANCO SIN CLAVE') { throw 'produccion arranca sin DJANGO_SECRET_KEY' }
if ($salida -notmatch 'DJANGO_SECRET_KEY') { throw "produccion fallo por otro motivo, no por la clave: $salida" }

uv run python manage.py check
if ($LASTEXITCODE -ne 0) { throw 'el gate local se ha roto' }
uv run pytest tests/web -q
if ($LASTEXITCODE -ne 0) { throw 'la suite web falla' }
uv run pytest tests/domain tests/ai tests/report -q
if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

**Checkpoint**

```powershell
git add -A
git commit -m "paso 26: ajustes de produccion, cabeceras de seguridad y WhiteNoise"
git tag step-26-seguridad
git ls-files --error-unmatch config/settings/production.py
if ($LASTEXITCODE -ne 0) { throw 'production.py no ha quedado versionado' }   # expect: exit 0
```

---

#### Paso 27 — Integración continua, estáticos y cierre

**Do**

- `.github/workflows/ci.yml` — un solo trabajo en `ubuntu-latest` con `astral-sh/setup-uv`, que ejecuta
  las mismas órdenes del gate de §20.1, en el mismo orden, **incluida la puerta de
  regresión del paso 23**. Si una comprobación está en el gate, está en CI. La única diferencia
  admitida son los flags `--cov` sobre `pytest`, que solo tienen sentido donde se publica el
  informe de cobertura y no cambian qué se comprueba ni si pasa. Sin secretos:
  `ANTHROPIC_API_KEY` no se define, de modo que CI ejercita permanentemente la ruta de degradación de
  la capa de IA y el arnés corre con sus puntuadores deterministas.
- `README.md` — se reescribe la puesta en marcha para `uv` y Django; desaparece `pip install -e .`,
  desaparece `streamlit run ui/app.py`. Se documentan el alta de la primera cuenta, los dos comandos de
  reindexado y el de copia de seguridad. Se conservan las secciones de trazabilidad jurídica y de capa
  de IA, actualizando la precedencia de la clave y el hecho de que el modelo ya no se resuelve solo.
- `uv run python manage.py collectstatic --noinput` — se ejecuta una vez para comprobar que WhiteNoise
  y `STATIC_ROOT` están bien puestos. `staticfiles/` **no** se versiona.
- Comprobación del modo `--check` en su rama de fallo: se altera `tokens.css`, se afirma que el script
  sale con **1**, y se restaura.

**Done when**

- [ ] WHEN the full §20.1 gate is run in order THE SYSTEM SHALL exit 0 at every line.
- [ ] WHEN `uv run python manage.py collectstatic --noinput` runs THE SYSTEM SHALL exit 0 and populate `staticfiles/`.
- [ ] WHEN `static/css/tokens.css` is deliberately corrupted THE SYSTEM SHALL make `uv run python -m scripts.build_tokens --check` exit **1** specifically — proving the sync gate can actually fail.
- [ ] WHEN `README.md` is read THE SYSTEM SHALL contain no reference to `streamlit` and no `pip install -e .`, and SHALL document creating the first account, both reindex commands and the backup command.
- [ ] WHEN `.github/workflows/ci.yml` is read THE SYSTEM SHALL contain every command of §20.1's automated block, including the evaluation regression gate.
- [ ] WHEN this step's `Checkpoint` has run THE SYSTEM SHALL list 27 tags matching `step-*`, one per step of §9.

**Verify**

```powershell
uv run python manage.py collectstatic --noinput
if ($LASTEXITCODE -ne 0) { throw 'collectstatic falla' }   # expect: exit 0

# El gate de sincronia PUEDE fallar: se afirma el codigo 1, no "distinto de cero".
Copy-Item 'static/css/tokens.css' 'static/css/tokens.css.bak'
Add-Content 'static/css/tokens.css' '/* alteracion deliberada */'
uv run python -m scripts.build_tokens --check
$codigo = $LASTEXITCODE
Move-Item 'static/css/tokens.css.bak' 'static/css/tokens.css' -Force
if ($codigo -ne 1) { throw "con tokens.css alterado se esperaba codigo 1, obtenido $codigo" }
# 1 = desincronizado (la propiedad) · 2 = error de uso · 0 = la comprobacion no detecta nada

uv run python -m scripts.build_tokens --check
if ($LASTEXITCODE -ne 0) { throw 'tokens.css no ha quedado restaurado' }   # expect: exit 0

if ((Get-Content -Raw 'README.md') -match 'streamlit') { throw 'el README sigue hablando de streamlit' }
if ((Get-Content -Raw 'README.md') -match 'pip install -e') { throw 'el README sigue mandando instalar el paquete' }

uv run ruff check .
if ($LASTEXITCODE -ne 0) { throw 'ruff falla' }
uv run ruff format --check .
if ($LASTEXITCODE -ne 0) { throw 'el formato no esta aplicado' }
uv run mypy .
if ($LASTEXITCODE -ne 0) { throw 'mypy falla' }
uv run pytest -q
if ($LASTEXITCODE -ne 0) { throw 'la suite completa falla' }   # expect: exit 0, 0 failed, 0 skipped

# El criterio "ci.yml contiene todas las ordenes del gate" necesita su propia comprobacion:
# sin ella es una afirmacion sin puerta. Se exige cada orden del bloque automatizado de 20.1.
$ci = Get-Content -Raw '.github/workflows/ci.yml'
$exigidas = @(
  'ruff check', 'ruff format --check', 'mypy .',
  'manage.py check', 'migrate --check', 'makemigrations --check --dry-run',
  'AUTH_USER_MODEL', 'reindexar_corpus', 'reindexar_evaluacion',
  'scripts.build_tokens --check', 'tests/domain tests/ai tests/report',
  'test_aislamiento.py', 'evaluar --contra-linea-base',
  'copia_seguridad', 'restaurar_copia', 'collectstatic', 'check --list-tags', 'check --deploy'
)
$faltan = $exigidas | Where-Object { -not $ci.Contains($_) }
if ($faltan) { throw "ci.yml no ejecuta el gate completo; faltan: $($faltan -join ', ')" }
# expect: ninguna falta — 20.1 y ci.yml ejecutan el mismo conjunto
```

**Checkpoint**

```powershell
git add -A
git commit -m "paso 27: integracion continua, estaticos y cierre de la migracion"
git tag step-27-cierre
$etiquetas = (git tag -l 'step-*' | Measure-Object -Line).Lines
if ($etiquetas -ne 27) { throw "hay $etiquetas etiquetas de paso, se esperaban 27" }   # expect: 27
git ls-files --error-unmatch .github/workflows/ci.yml
if ($LASTEXITCODE -ne 0) { throw 'el flujo de CI no ha quedado versionado' }           # expect: exit 0
```

---

### 9.1 Paridad y conmutación

Este blueprint **describe una migración**: sustituye una interfaz de Streamlit en funcionamiento por
una aplicación de Django. Un proyecto nuevo no tiene nada de lo que conmutar; este sí, y la forma en
que una migración falla es distinta: lo nuevo funciona, lo viejo hacía algo que nadie había escrito, y
la diferencia la descubre el usuario.

#### Conjunto de paridad

| # | Comportamiento que se mantiene | Cómo se demuestra la paridad | Tolerancia |
|---|---|---|---|
| 1 | El motor de cálculo produce exactamente los mismos resultados | `uv run pytest tests/domain` — 89 pruebas, sin modificar | Coincidencia exacta. Ni una prueba puede cambiar |
| 2 | El informe PDF tiene las mismas secciones y el mismo contenido | `uv run pytest tests/report` — 38 pruebas, sin modificar | Coincidencia exacta |
| 3 | La capa de IA sigue sin poder citar lo que el motor no emitió, y sigue degradando en silencio | `uv run pytest tests/ai` — 53 pruebas, de las que solo cambian las que cubrían la resolución dinámica del modelo | Sustitución prueba por prueba; el total de la suite rescatada sigue siendo **180** |
| 4 | La pantalla enseña lo mismo que enseñaba Streamlit: rango, posición, tratamiento por jurisdicción, factores de riesgo, fuentes y descarga | `tests/web/test_result_template.py` y `tests/web/test_informe_view.py` | Paridad de contenido, no de píxeles. La disposición cambia a propósito: el rango pasa a ser el protagonista |
| 5 | El aviso de datos sintéticos sigue en el documento que el usuario descarga | El literal `DATOS SINTÉTICOS` extraído con `pypdf` del PDF servido por la web (paso 14) | Coincidencia exacta. Es el riesgo 1 de §20.2, aceptado y bloqueante |

**Periodo en sombra: no lo hay, y es una decisión.** Las dos interfaces no pueden convivir: comparten
el mismo repositorio, el mismo `pyproject.toml` y el mismo intérprete, y Streamlit ya no está entre las
dependencias fijadas. Lo que sustituye al periodo en sombra es la suite rescatada: **180 pruebas que
pasaban antes de tocar nada y tienen que seguir pasando en cada uno de los 27 pasos.** Esa es la
evidencia de paridad de este proyecto, y es más fuerte que ejecutar las dos interfaces en paralelo,
porque cubre el motor entero y no solo los caminos que a alguien se le ocurra pulsar.

#### Conmutación

| Fase | Qué cambia | A quién afecta | Reversible con | Verify |
|---|---|---|---|---|
| Preparación | La rama de trabajo tiene Django y Streamlit todavía en disco | A nadie | `git reset --hard` a la etiqueta anterior | `uv run python manage.py check` |
| Corte (paso 3) | Se borra `ui/`; Streamlit deja de existir en el árbol | Al usuario, que a partir de aquí usa `manage.py runserver` | `git reset --hard step-02-configuracion` | `uv run pytest tests/domain tests/ai tests/report` → 180 passed |
| Completa (paso 27) | La aplicación de Django cubre todo lo que cubría la anterior, más las cuentas, el corpus indexado, la biblioteca de precedentes, el estudio, el control de gasto y el arnés | Al usuario | `git reset --hard step-02-configuracion`, que aún tiene `ui/app.py` | El gate completo de §20.1 |

**El interruptor de emergencia** es `git reset --hard step-02-configuracion`, seguido de `uv sync` con
el `pyproject.toml` archivado como `pyproject.toml.pre-django`. Tarda lo que tarde `uv` en reinstalar
Streamlit: del orden de un minuto, no instantáneo. Se dice aquí explícitamente porque una "vuelta atrás
inmediata" que tarda un minuto es un minuto de interrupción, y conviene saberlo antes y no durante.

#### Criterios de aborto

- [ ] WHEN `uv run pytest tests/domain tests/ai tests/report` reports fewer than 180 passed or any failure THE SYSTEM SHALL stop the migration at that step and SHALL NOT proceed to the next.
- [ ] WHEN the report suite fails against the pinned `reportlab` (§20.2, riesgo 2) THE SYSTEM SHALL stop at paso 3 and report it, rather than adapting the rescued code to a new behaviour without a decision.
- [ ] WHEN the literal `DATOS SINTÉTICOS` cannot be extracted from the served PDF THE SYSTEM SHALL treat it as a blocking defect and SHALL NOT continue past paso 14.
- [ ] WHEN `AUTH_USER_MODEL` is found to be anything other than `cuentas.Usuario` after paso 4 has been applied THE SYSTEM SHALL stop: recovering from that state costs days, and every later step compounds it.

#### Migración de datos

**NO APLICA — no se mueve ningún dato.** La aplicación de Streamlit no persistía nada: cada análisis
vivía en la memoria del proceso hasta que el usuario recargaba. Las ocho tablas de §4 nacen vacías y no
hay nada anterior que trasvasar. No existe, por tanto, ningún punto de no retorno de datos.

Sí hay un punto de no retorno **de esquema**, y está en el paso 4: una vez aplicada la migración
inicial con `AUTH_USER_MODEL`, cambiarlo deja de ser una migración y pasa a ser una reconstrucción. Es
la línea de mayor riesgo de toda la construcción, y por eso el paso 4 la comprueba explícitamente antes
de que exista ninguna tabla con clave foránea al usuario.

#### Retirada

Lo que se elimina —`ui/app.py`, `requirements.txt`, `tpip.egg-info/`, el `pyproject.toml` de
setuptools— se elimina en el paso 3, y su copia de seguridad es el historial de git: la etiqueta
`step-02-configuracion` contiene todo eso intacto. No hay credenciales, ni DNS, ni cuentas de
proveedor que limpiar, porque la etapa de Streamlit no desplegaba nada.

La retirada **no es un paso de §9** más allá del borrado del paso 3: quitar la etiqueta de retorno
`step-02-configuracion` o purgar el historial es una decisión posterior al periodo de reposo, y va en
la lista de gates manuales de §20.1.

---
## 10. Puesta en marcha del entorno

### Requisitos previos

| Herramienta | Versión | Comprobación |
|---|---|---|
| `uv` | 0.12.0 o superior | `uv --version` |
| Python 3.12 | 3.12.x — **lo instala `uv`, no hace falta tenerlo** | `uv python install 3.12` y después `uv run python --version` |
| Git | cualquiera con `git init -b` | `git --version` |
| PowerShell | 5.1 (el que trae Windows 10) o superior | `$PSVersionTable.PSVersion` |

El intérprete del sistema no importa: la máquina de referencia tiene Python 3.11.9 y el proyecto exige
3.12, y `uv` descarga y gestiona el 3.12 por su cuenta. Ese es justamente el motivo por el que `uv` es
la elección de §2.

### Cuentas que crear antes de empezar

Solo una, y es **opcional**: una cuenta de la API de Anthropic (`https://console.anthropic.com`) para
obtener `ANTHROPIC_API_KEY`. La necesita el paso 17, y **solo para ejercitar la ruta feliz de la capa
de IA**: sin clave, los 27 pasos se completan igual y el gate de §20.1 sale en verde, porque la capa de
IA está diseñada para degradar en silencio y las pruebas del paso 17 cubren la degradación con dobles,
sin tocar la red. No hay ninguna otra cuenta, ningún proveedor de alojamiento y ningún servicio de
pago.

### Variables de entorno

| Variable | Para qué | De dónde se saca | Requerida a partir del paso | ¿Secreta? |
|---|---|---|---|---|
| `DJANGO_SECRET_KEY` | Firma de tokens CSRF y de cualquier valor firmado | Generada localmente: `uv run python -c "import secrets; print(secrets.token_urlsafe(64))"` | **26**, y solo en `config.settings.production`. En desarrollo `config/settings/local.py` lleva un valor explícito marcado como tal | Sí |
| `DJANGO_DEBUG` | Modo de depuración | Valor local: `true` | Nunca obligatoria (por defecto `true` en local, `False` fijo en producción) | No |
| `DJANGO_ALLOWED_HOSTS` | Hosts admitidos, separados por comas | Valor local: `127.0.0.1,localhost` | **26** | No |
| `ANTHROPIC_API_KEY` | Autenticación de la capa de IA | Consola de Anthropic → API Keys | Nunca obligatoria. Sin ella la capa se desactiva y el informe se genera completo declarando su ausencia | Sí |
| `ANTHROPIC_MODEL` | Identificador exacto del modelo | Se elige a mano y se anota; **a partir del paso 8 no se resuelve solo** (§17) | Nunca obligatoria. Sin ella, la capa de IA queda desactivada aunque haya clave | No |
| `PRECIO_ENTRADA_EUR_POR_MTOK` | Tarifa de entrada, en euros por millón de tokens, con la que `apps/ia/cuota.py` imputa el gasto | Tarifa publicada del modelo fijado en `ANTHROPIC_MODEL`, convertida a euros por el administrador (§17) | Nunca obligatoria. Sin ella el coste imputado es `0`: se registra el uso pero no se imputa gasto | No |
| `PRECIO_SALIDA_EUR_POR_MTOK` | Ídem para los tokens de salida | Ídem | Nunca obligatoria, con el mismo efecto | No |
| `DJANGO_SUPERUSER_USERNAME` | Nombre de la cuenta de administrador inicial | Lo elige el desarrollador | **4**, y solo para el alta inicial | No |
| `DJANGO_SUPERUSER_EMAIL` | Correo de esa cuenta | Lo elige el desarrollador | **4**, y solo para el alta inicial | No |
| `DJANGO_SUPERUSER_PASSWORD` | Contraseña de esa cuenta | Generada localmente: `uv run python -c "import secrets; print(secrets.token_urlsafe(18))"` | **4**, y solo para el alta inicial | Sí |
| `DJANGO_SETTINGS_MODULE` | Qué módulo de configuración se carga | **No se pone en `.env`.** Lo fija `manage.py` para los comandos y `pyproject.toml` para pytest; en ambos, el literal `config.settings.local` | 1 | No |

**Las tres variables `DJANGO_SUPERUSER_*` se declaran aquí pero no las ejecuta Bootstrap, y el motivo
importa:** las lee `uv run python manage.py createsuperuser --noinput`, y `manage.py` no existe hasta
que lo escribe el paso 1, mientras que el bloque Bootstrap corre **antes** del paso 1. Meter ahí ese
comando lo haría fallar en la primera pasada, siempre. El alta se hace a mano una vez, después del
paso 4, que es cuando existe la tabla de usuarios; §4.6 lo describe como el único dato de arranque del
sistema. Son opcionales en todo momento: sin ellas no se crea la cuenta inicial, pero ningún gate de
§9 depende de que exista —las pruebas crean sus propios usuarios—.

`.env.example` se versiona con todas las claves presentes y todos los valores vacíos o evidentemente
falsos. `.env` está en el fichero de ignorados. **Ninguna variable es obligatoria en desarrollo**, y
eso no es un descuido: es lo que permite que ningún paso rompa retroactivamente el gate de un paso
anterior (§9 regla 9). La única que se vuelve obligatoria lo hace en el paso 26, dentro de
`config.settings.production`, que es exactamente el paso cuyo código la satisface.

**Listar una variable aquí no la carga.** El único mecanismo de carga de este proyecto es el
`SettingsConfigDict(env_file=".env")` de `config/settings/base.py`, y **todo** —`manage.py`, `pytest`
vía `DJANGO_SETTINGS_MODULE`, las vistas y `services.py`— pasa por ahí. Los scripts de `scripts/` no
leen ninguna variable de entorno. Está detallado en §19.6.

### Ficheros que deben quedar versionados

| Fichero | Por qué se versiona | Línea de excepción en el fichero de ignorados |
|---|---|---|
| `.env.example` | Es el contrato de configuración: quien clona sabe qué claves existen | `!.env.example`, escrita **después** del patrón `.env` |
| `pyproject.toml` | Dependencias, ruff, mypy y pytest. Sin él no hay nada que instalar | — no lo captura ningún patrón de ignorados |
| `uv.lock` | Fija el árbol resuelto; sin él, `uv sync` no es reproducible | — no lo captura ningún patrón |
| `static/css/tokens.css` | Generado, pero versionado: el CSS tiene que funcionar sin ejecutar nada | — no lo captura ningún patrón (`staticfiles/`, que sí se ignora, es otro directorio) |
| `.claude/settings.json`, `.claude/rules/`, `.claude/skills/` | La configuración del agente forma parte del proyecto | `!.claude/` si el fichero de ignorados trae `.claude/`; hoy no lo trae |
| `.github/workflows/ci.yml` | El gate de §20.1 ejecutándose solo | — no lo captura ningún patrón |
| Las migraciones de las seis aplicaciones con modelos (`cuentas`, `analisis`, `corpus`, `estudio`, `ia`, `evaluacion`) | Sin ellas, `migrate` no reconstruye el esquema, y la de `cuentas` es además la que fija `AUTH_USER_MODEL` (§4.5) | — `**/migrations/**` está excluido de **ruff**, que es otra cosa distinta de estar ignorado por git |

### Bootstrap

```powershell
# =====================================================================
# TPIP — bootstrap. PowerShell, Windows 10. Se ejecuta desde la raíz del
# proyecto, con el bundle ya presente en blueprints/tpip/.
#
# EL ORDEN IMPORTA, y es este:
#   archivar el pyproject antiguo -> copiar el workspace (que trae el
#   fichero de ignorados y la configuración) -> completar las líneas de
#   ignorados y las claves de .env.example -> identidad de git -> init ->
#   PRIMER COMMIT -> .env -> intérprete -> dependencias -> comprobación.
#
# La razón de que los ignorados vayan ANTES del primer commit: `git add -A`
# se lleva todo lo que haya en disco en ese momento, y una regla de
# ignorados no se aplica jamás a una ruta que git ya sigue.
#
# EL BLOQUE ENTERO ES SEGURO EJECUTÁNDOLO DOS VECES SEGUIDAS, y sale con 0
# en la segunda pasada. Cada guarda está escrita para no fallar sobre el
# camino contra el que guarda.
# =====================================================================
$ErrorActionPreference = 'Stop'

# --- 0. Sondas cuyo fallo es la respuesta esperada ---
# `git rev-parse` en un directorio sin repositorio escribe en stderr POR DISENO:
# no es un error, es la respuesta "todavia no hay repositorio". Pero con
# $ErrorActionPreference = 'Stop', PowerShell convierte el stderr de un comando
# NATIVO en error terminante, y `2>$null` silencia el texto sin evitarlo: el
# bloque abortaria en la sonda en vez de crear el repositorio. Verificado
# ejecutandolo: sin esto, Bootstrap muere en su paso 6 de 11 y `git init` nunca
# corre. Estas sondas se juzgan por su CODIGO DE SALIDA, que es lo unico que informa.
function Test-ComandoOk([scriptblock]$sonda) {
    $previo = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    & $sonda 2>&1 | Out-Null
    $ok = ($LASTEXITCODE -eq 0)
    $ErrorActionPreference = $previo
    return $ok
}

# --- 1. El pyproject.toml de la etapa Streamlit se aparta, una sola vez ---
# El emitido en §19.6 no puede aterrizar encima porque la copia de abajo
# nunca sobrescribe. Marca de reconocimiento: 'package = false', que solo
# tiene el nuevo. Segunda pasada: la condición ya no se cumple -> no hace nada.
if ((Test-Path -LiteralPath 'pyproject.toml') -and
    -not (Select-String -LiteralPath 'pyproject.toml' -Pattern 'package = false' -SimpleMatch -Quiet)) {
    Move-Item -LiteralPath 'pyproject.toml' -Destination 'pyproject.toml.pre-django' -Force
}

# --- 2. Copia NO destructiva del workspace del bundle a la raíz ---
# Copia únicamente lo que falta. Nunca sobrescribe: pyproject.toml y uv.lock
# cambian durante la construcción, y una segunda pasada NO debe revertirlos
# a su versión sin dependencias. Sale con 0 tanto si copia como si no.
$origen = (Resolve-Path 'blueprints/tpip/workspace').Path
$raiz = (Get-Location).Path
Get-ChildItem -LiteralPath $origen -Recurse -File -Force | ForEach-Object {
    $destino = Join-Path $raiz $_.FullName.Substring($origen.Length + 1)
    if (-not (Test-Path -LiteralPath $destino)) {
        $carpeta = Split-Path -Parent $destino
        if (-not (Test-Path -LiteralPath $carpeta)) { New-Item -ItemType Directory -Path $carpeta -Force | Out-Null }
        Copy-Item -LiteralPath $_.FullName -Destination $destino
    }
}
# Nunca se sobrescriben, una vez existen: pyproject.toml, uv.lock, .gitignore,
# .env.example, .claude/settings.json.

# --- 3. Fichero de ignorados: se añade lo que falte, en orden ---
# Idempotente por comparación línea a línea. '!.env.example' se añade DESPUÉS
# de '.env', que es lo único que hace que la excepción tenga efecto.
if (-not (Test-Path -LiteralPath '.gitignore')) { New-Item -ItemType File -Path '.gitignore' | Out-Null }
$actual = @(Get-Content -LiteralPath '.gitignore')
foreach ($linea in @('.env', '!.env.example', '.venv/', 'db.sqlite3', 'staticfiles/', 'copias/', 'blueprints/', 'pyproject.toml.pre-django')) {
    if ($actual -notcontains $linea) {
        Add-Content -LiteralPath '.gitignore' -Value $linea
        $actual += $linea
    }
}

# --- 4. .env.example: se añaden las claves que falten ---
foreach ($par in @('DJANGO_SECRET_KEY=', 'DJANGO_DEBUG=true', 'DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost', 'ANTHROPIC_API_KEY=', 'ANTHROPIC_MODEL=')) {
    $clave = $par.Split('=')[0]
    if (-not (Select-String -LiteralPath '.env.example' -Pattern "^$clave=" -Quiet)) {
        Add-Content -LiteralPath '.env.example' -Value $par
    }
}

# --- 5. Identidad de git, solo si falta (un repositorio recién creado no la tiene) ---
if (-not (Test-ComandoOk { git config user.email })) {
    git config user.email 'builder@localhost'
    git config user.name 'TPIP builder'
}

# --- 6. Repositorio: §9 usa etiquetas de checkpoint, así que tiene que existir ---
# No se da por hecho que ningún generador lo haya creado: aquí no hay generador.
if (-not (Test-ComandoOk { git rev-parse --git-dir })) {
    git init -b main
    if ($LASTEXITCODE -ne 0) { throw 'git init ha fallado' }
    git config user.email 'builder@localhost'
    git config user.name 'TPIP builder'
}

# --- 7. Primer commit: una etiqueta necesita un commit al que apuntar ---
# Solo si no hay HEAD todavía. Segunda pasada: HEAD existe -> no hace nada.
if (-not (Test-ComandoOk { git rev-parse --verify HEAD })) {
    git add -A
    git commit -m 'chore: bootstrap — workspace del blueprint, ignorados y configuracion' --allow-empty
    if ($LASTEXITCODE -ne 0) { throw 'el primer commit ha fallado' }
}

# --- 8. .env local, a partir del ejemplo. Ya está ignorado por el paso 3 ---
if (-not (Test-Path -LiteralPath '.env')) { Copy-Item -LiteralPath '.env.example' -Destination '.env' }

# --- 9. Entorno virtual con el intérprete correcto ---
# El .venv de la etapa Streamlit lleva Python 3.11 y no satisface
# requires-python >= 3.12. Se detecta por pyvenv.cfg y se rehace.
# La comprobacion es >= 3.12, NO "== 3.12". `uv` provisiona el interprete mas
# reciente que satisfaga requires-python —hoy 3.14—, asi que comparar contra el
# literal '3.12' borraria en CADA pasada un entorno perfectamente valido; y en
# Windows ese borrado ademas falla si un .pyd esta en uso, dejando el bloque en 1.
# Verificado ejecutando el bloque dos veces seguidas.
if (Test-Path -LiteralPath '.venv/pyvenv.cfg') {
    $cfg = Get-Content -Raw -LiteralPath '.venv/pyvenv.cfg'
    $v = [regex]::Match($cfg, 'version(?:_info)?\s*=\s*(\d+)\.(\d+)')
    $suficiente = $v.Success -and (
        ([int]$v.Groups[1].Value -gt 3) -or
        ([int]$v.Groups[1].Value -eq 3 -and [int]$v.Groups[2].Value -ge 12))
    if (-not $suficiente) { Remove-Item -Recurse -Force -LiteralPath '.venv' }
}
uv python install 3.12
if ($LASTEXITCODE -ne 0) { throw 'no se ha podido instalar Python 3.12' }

# --- 10. Dependencias. Idempotente por diseño ---
uv sync
if ($LASTEXITCODE -ne 0) { throw 'uv sync ha fallado' }

# --- 11. Comprobación final: la cadena de herramientas responde ---
uv run python -c "import django, pydantic, pydantic_settings, structlog, reportlab, numpy, frontmatter, markdown, anthropic; print('cadena de herramientas OK — Django', django.get_version())"
if ($LASTEXITCODE -ne 0) { throw 'la cadena de herramientas no esta lista' }

# NO hay migraciones ni datos de arranque aquí, y es a propósito: manage.py lo
# crea el paso 1 y la migración inicial la genera el paso 4. Ejecutar el
# servidor (`uv run python manage.py runserver`, puerto 8000) es posible a
# partir del paso 1, no antes.
```

**Ningún comando de este bloque es interactivo.** `uv sync` y `uv python install` no preguntan nada;
`git commit` tiene identidad garantizada por el paso 5; `Copy-Item` y `Add-Content` no abren ningún
diálogo. Un comando que abriera una consola de confirmación colgaría una construcción desatendida para
siempre, lo cual es indistinguible de una construcción lenta.

---

## 11. Dependencias

Esta sección es la tabla de procedencia de versiones. **Es el único sitio de la prosa del blueprint
donde aparece un número de versión**; la única excepción son los ficheros ejecutables emitidos en §19,
que llevan el valor real porque se ejecutan —en este proyecto, `pyproject.toml`—.

Todas las filas proceden del informe de `stack-researcher` producido en esta sesión y fechado el
**2026-08-15**, y están ya materializadas en `blueprints/tpip/workspace/pyproject.toml`, que es el
fichero que las instala. **`Instalado por` apunta en todas ellas a §10 Bootstrap**, porque `uv sync`
lee ese `pyproject.toml` y no hay ningún otro comando de instalación en todo el documento: no hay ni
un solo paso de §9 que ejecute `uv add`. Un paquete que no aparezca en ese fichero no está instalado
por nada, y por eso no hay ninguno aquí que no esté.

### Ejecución

| Paquete | Versión | Fuente | Comprobado | Instalado por | Para qué |
|---|---|---|---|---|---|
| `django` | `>=5.2,<5.3` | `https://pypi.org/project/Django/` | 2026-08-15 | §10 Bootstrap — `uv sync` | El marco web. La serie 5.2 es LTS; el acotado superior impide que un `uv sync` futuro salte de rama mayor sin decisión |
| `pydantic` | `>=2.13.4,<3` | `https://pypi.org/project/pydantic/` | 2026-08-15 | §10 Bootstrap — `uv sync` | El lenguaje del dominio rescatado. Todo `tp_domain/` está escrito contra pydantic 2 |
| `pydantic-settings` | `>=2.15.0,<3` | `https://pypi.org/project/pydantic-settings/` | 2026-08-15 | §10 Bootstrap — `uv sync` | Configuración tipada en `config/settings/base.py` (paso 2). **Es el único mecanismo de carga de `.env` del proyecto** |
| `python-dotenv` | `>=1.0.0` | `https://pypi.org/project/python-dotenv/` | 2026-08-15 | §10 Bootstrap — `uv sync` | Dependencia de `pydantic-settings` para el soporte de `env_file`, declarada de forma explícita porque este proyecto depende de esa función concreta y no quiere que desaparezca en una resolución futura |
| `whitenoise` | `>=6.12.0,<7` | `https://pypi.org/project/whitenoise/` | 2026-08-15 | §10 Bootstrap — `uv sync` | Sirve los estáticos desde el propio proceso (paso 26), que es lo que hace que `check --deploy` compruebe algo real |
| `anthropic` | `>=0.122.0,<1` | `https://pypi.org/project/anthropic/` | 2026-08-15 | §10 Bootstrap — `uv sync` | Cliente de la API para `ai/claude_client.py`. Acotado por debajo de 1.0: la serie 0.x todavía puede romper compatibilidad entre menores |
| `structlog` | `>=26.1.0,<27` | `https://pypi.org/project/structlog/` | 2026-08-15 | §10 Bootstrap — `uv sync` | Registro estructurado (paso 2, paso 12) |
| `python-frontmatter` | `>=1.3.0,<2` | `https://pypi.org/project/python-frontmatter/` | 2026-08-15 | §10 Bootstrap — `uv sync` | Lee el frontmatter YAML de las 9 fichas de `documentation/tax-research/` en el indexador (paso 19) |
| `Markdown` | `>=3.10.3,<4` | `https://pypi.org/project/Markdown/` | 2026-08-15 | §10 Bootstrap — `uv sync` | Renderiza el cuerpo de esas fichas a HTML al publicarlas (paso 20) |
| `reportlab` | `>=5.0.0,<6` | `https://pypi.org/project/reportlab/` | 2026-08-15 | §10 Bootstrap — `uv sync` | Genera el informe PDF. **AVISO ARRASTRADO DEL INFORME DE VERSIONES: la serie 5.0 es un salto de rama mayor sobre la 4.x contra la que se escribió `infrastructure/report/pdf_report.py`, con cambio de comportamiento señalado.** Este blueprint no adapta el código a ciegas: el paso 3 ejecuta las 38 pruebas de informe rescatadas contra esta versión fijada, y si fallan, el paso 3 se detiene y se reporta (§9.1, criterios de aborto; §20.2, riesgo 2) |
| `numpy` | `>=1.26` | `https://pypi.org/project/numpy/` | 2026-08-15 | §10 Bootstrap — `uv sync` | Los percentiles del rango. La convención de cálculo (interpolación lineal, el valor por defecto de numpy) viaja dentro de cada `BenchmarkRange` |

### Desarrollo

| Paquete | Versión | Fuente | Comprobado | Instalado por | Para qué |
|---|---|---|---|---|---|
| `ruff` | `>=0.16.3,<0.17` | `https://pypi.org/project/ruff/` | 2026-08-15 | §10 Bootstrap — `uv sync` | Lint, orden de imports y formato. Su `extend-exclude` es lo que mantiene el bundle y el código rescatado fuera del lint |
| `mypy` | `>=2.3.1,<3` | `https://pypi.org/project/mypy/` | 2026-08-15 | §10 Bootstrap — `uv sync` | Tipos, solo sobre el código nuevo |
| `pytest` | `>=9.1.1,<10` | `https://pypi.org/project/pytest/` | 2026-08-15 | §10 Bootstrap — `uv sync` | Las 180 pruebas rescatadas ya están escritas contra pytest |
| `pytest-django` | `>=4.14.0,<5` | `https://pypi.org/project/pytest-django/` | 2026-08-15 | §10 Bootstrap — `uv sync` | Base de datos de prueba y `DJANGO_SETTINGS_MODULE` desde `pyproject.toml` |
| `pytest-cov` | `>=7.1.0,<8` | `https://pypi.org/project/pytest-cov/` | 2026-08-15 | §10 Bootstrap — `uv sync` | Informe de cobertura en el flujo de CI del paso 27 |
| `pypdf` | `>=5.0` | `https://pypi.org/project/pypdf/` | 2026-08-15 | §10 Bootstrap — `uv sync` | Extrae el texto del PDF para las pruebas de informe (rescatadas) y para el paso 14 |

### Herramientas fuera del gestor de paquetes

| Herramienta | Versión | Fuente | Comprobado | Instalado por | Para qué |
|---|---|---|---|---|---|
| `uv` | `0.12.0` o superior | `https://pypi.org/project/uv/` — versión observada en la máquina de referencia el 2026-08-15 | 2026-08-15 | El desarrollador, §10 *Requisitos previos* | Gestor de paquetes e intérpretes |
| CPython | `3.12.x` | Lo descarga `uv python install 3.12` | 2026-08-15 | §10 Bootstrap | El intérprete. La máquina de referencia tiene 3.11.9; `uv` aporta el 3.12 |

### Deliberadamente no usados

| Rechazado | En su lugar | Por qué |
|---|---|---|
| `factory-boy` | Los *fixtures* de `tests/domain/conftest.py`, que ya existen (`make_transaction`) | **El informe de versiones lo marca OBSOLESCENTE.** Y aunque no lo estuviera: introducir un constructor de objetos de prueba en un proyecto cuyas 180 pruebas ya construyen los suyos a mano obligaría a reescribirlas, que es exactamente lo que la red de seguridad impide |
| `streamlit` | Django | Es lo que esta migración sustituye (§1). No aparece en `pyproject.toml` y el paso 3 comprueba que no queda ninguna importación |
| `django-environ` | `pydantic-settings` | El dominio ya es pydantic. Dos librerías de configuración con dos sistemas de tipos distintos en el mismo proyecto es una de más |
| `django-stubs` | `ignore_missing_imports = true` en la configuración de mypy | Los stubs de Django exigen configurar un plugin de mypy y anclar la versión de Django y la de los stubs entre sí. El código nuevo con tipos es `apps/`, `config/` y `scripts/`, y ahí el valor que aportan no cubre ese coste |
| `playwright`, `selenium` | El cliente de pruebas de Django | No-Goal de §1: exigirían un runtime de Node y binarios de navegador |
| `celery`, `redis` | Llamada síncrona dentro de la petición | No hay trabajo diferido: el análisis tarda menos de lo que el usuario espera mirando la pantalla |
| `gunicorn`, `uvicorn` | `manage.py runserver` en local | No hay despliegue en la v1 (§12). Añadir un servidor de producción sin sitio donde ponerlo es configuración que nadie ejecuta |

---

## 12. Estrategia de despliegue

### Alojamiento

**No hay alojamiento contratado, y es una decisión, no una omisión.** El sistema tiene un usuario y se
ejecuta en su equipo con `uv run python manage.py runserver`, escuchando en `127.0.0.1:8000`. Publicar
en internet una herramienta sin autenticación (§8) que emite documentos con la advertencia de que sus
datos son sintéticos sería, además de innecesario, una mala idea.

Lo que sí existe es `config/settings/production.py` (paso 26), con `DEBUG = False`, las cabeceras de
§14 y WhiteNoise sirviendo los estáticos. Existe **para que la comprobación de seguridad pruebe algo
real**: `manage.py check --deploy` sobre un módulo de configuración que nadie usa no comprobaría nada.
El día que haya dónde desplegar, el comando de construcción es
`uv sync --no-dev && uv run python manage.py migrate && uv run python manage.py collectstatic --noinput`,
el directorio de salida de estáticos es `staticfiles/` y el punto de entrada WSGI es
`config.wsgi:application`.

### Entornos

| Entorno | Rama | URL | Base de datos | Modo de terceros |
|---|---|---|---|---|
| Local | la de trabajo | `http://127.0.0.1:8000` | `db.sqlite3` en la raíz | `ANTHROPIC_API_KEY` real si el usuario quiere la sección de IA; si no, capa desactivada |
| Integración continua | cualquier `push` y cualquier PR | — | SQLite temporal que crea `pytest-django` | **Sin clave**: CI ejercita permanentemente la ruta de degradación |
| Producción | — | — | — | NO APLICA en la v1 — no hay entorno de producción desplegado |

### Integración continua

Un solo trabajo, en `ubuntu-latest`, con `astral-sh/setup-uv`, que ejecuta **las mismas órdenes del
bloque automatizado de §20.1, en el mismo orden**. Si una comprobación está en el gate, está en CI.
Traducidas a shell POSIX, que es el intérprete del ejecutor:

```yaml
# .github/workflows/ci.yml — lo escribe el paso 27.
# Es el bloque automatizado de §20.1 completo, en el mismo orden, traducido a shell POSIX.
- uv sync --frozen
- uv run ruff check .
- uv run ruff format --check .
- uv run mypy .
- uv run python manage.py check
- uv run python manage.py migrate --check
- uv run python manage.py makemigrations --check --dry-run
# AUTH_USER_MODEL es el punto sin retorno del paso 4: se comprueba en cada pasada.
- uv run python -c "import os; os.environ['DJANGO_SETTINGS_MODULE']='config.settings.local'; import django; django.setup(); from django.conf import settings; assert settings.AUTH_USER_MODEL == 'cuentas.Usuario', settings.AUTH_USER_MODEL"
# Los dos indices reconstruibles: el .md y el .json en disco son la fuente de verdad.
- uv run python manage.py reindexar_corpus
- uv run python manage.py reindexar_evaluacion
- uv run python -m scripts.build_tokens --check
- uv run pytest --cov=apps --cov=config --cov=scripts
# La red de seguridad de la migracion, explicita y con su recuento.
- uv run pytest tests/domain tests/ai tests/report -q
- |
  n=$(uv run pytest tests/domain tests/ai tests/report --collect-only -q 2>&1 | awk '/tests collected/ {print $1; exit}')
  test "$n" = 180 || { echo "la suite rescatada ya no tiene 180 pruebas, sino $n"; exit 1; }
# El aislamiento por propietario: si esto no pasa, el producto no es publicable.
- uv run pytest tests/web/test_aislamiento.py tests/web/test_guarda_unica.py -q
# La puerta de regresion del arnes (paso 23). 1 = regresion · 2 = no hay linea base.
- uv run python manage.py evaluar --contra-linea-base
# La copia, RESTAURADA y comparada por recuento de filas (paso 24).
- |
  uv run python manage.py copia_seguridad
  copia=$(ls -t copias/*.sqlite3 | head -1)
  destino=$(mktemp -d)
  uv run python manage.py restaurar_copia --copia "$copia" --destino "$destino"
# Se EJECUTA lo que se construye, no solo se construye.
- uv run python manage.py collectstatic --noinput
- uv run python manage.py check --list-tags
- uv run python manage.py check --deploy --settings=config.settings.production
# El gate de sincronia de tokens PUEDE fallar: se afirma el codigo 1 concreto.
- |
  cp static/css/tokens.css /tmp/tokens.bak
  printf '
/* alteracion deliberada */
' >> static/css/tokens.css
  set +e; uv run python -m scripts.build_tokens --check; codigo=$?; set -e
  cp /tmp/tokens.bak static/css/tokens.css
  test "$codigo" -eq 1 || { echo "con tokens.css alterado se esperaba 1, obtenido $codigo"; exit 1; }
```

CI **no** ejecuta `check --deploy` con una clave inventada: la comprobación de producción vive en el
`Verify` del paso 26, donde la clave se genera en el momento y se descarta.

### Publicación y vuelta atrás

La unidad de publicación de este proyecto es una etiqueta de git. Cada paso de §9 deja la suya
(`step-NN-<slug>`), y la vuelta atrás es `git reset --hard step-<N-1>-<slug>` seguido de `uv sync`.
Tarda lo que tarde `uv` en reconciliar el entorno: del orden de un minuto. **Nunca se depura hacia
delante a través de un checkpoint roto.**

Regla de migraciones respecto del despliegue: primero `migrate`, después el código, y nunca una
migración destructiva en el mismo commit que el cambio que la necesita (§4).

### Dominio, DNS y TLS

**NO APLICA — no hay dominio, no hay DNS y no hay certificado, porque no hay nada publicado.**
`SECURE_SSL_REDIRECT` y HSTS están configurados en `config/settings/production.py` (paso 26) para que
`check --deploy` los audite, no porque haya un certificado que los respalde hoy.

---

## 13. Estrategia de pruebas

Las pruebas existen para que las condiciones "Done when" de §9 sean comprobables. En este proyecto
tienen además un segundo trabajo, más importante: **las 180 pruebas rescatadas son la evidencia de
paridad de la migración** (§9.1).

### La invariante que ordena todo lo demás

> **La suite rescatada mantiene exactamente 180 pruebas de principio a fin, y las pruebas nuevas viven
> aparte, en `tests/web/`.**

No es una preferencia de organización: es lo que impide que un paso rompa retroactivamente el gate de
un paso anterior (§9 regla 9). El paso 3 deja `tests/domain tests/ai tests/report` en **180 passed**, y
esa misma orden se vuelve a ejecutar al final de **cada uno de los 27 pasos**. Si el recuento cambia,
alguien ha retirado cobertura del motor y el gate lo dice en el acto en vez de dejarlo pasar.

Solo dos pasos tocan la suite rescatada, y los dos lo hacen **sustituyendo prueba por prueba**: el
paso 8 en `tests/ai/test_explanation_flow.py`, al retirar la resolución dinámica del modelo, y el
paso 9 en `infrastructure/theme.py`, que es aditivo y por eso no necesita tocar `tests/report`. La
cobertura de los tokens nuevos no se añade a `tests/report` —lo cual cambiaría el recuento— sino a
`tests/web/test_theme_tokens.py`, porque lo que se comprueba ahí es el contrato entre `theme.py` y el
CSS, no el módulo aislado.

### Capas

| Capa | Marco | Qué cubre | Dónde | Cuándo corre |
|---|---|---|---|---|
| Dominio (rescatada) | pytest | Motor de cálculo, reglas por jurisdicción, registro de fuentes, invariantes de los modelos | `tests/domain/` — **89** pruebas | Cada paso, desde el 3 |
| Capa de IA (rescatada) | pytest | Validación de borradores, referencias legales, reintento único, degradación | `tests/ai/` — **53** pruebas | Cada paso, desde el 3 |
| Informe (rescatada) | pytest + pypdf | Secciones del PDF, portada, anexo, aviso de datos sintéticos, texto hostil a XML | `tests/report/` — **38** pruebas | Cada paso, desde el 3 |
| Web (nueva) | pytest + pytest-django + cliente de pruebas de Django | Todo lo que añade esta migración — el detalle, abajo | `tests/web/` | Desde el paso 2 |

### Las suites nuevas, una por paso que las crea

| Fichero | Paso | Qué fija |
|---|---|---|
| `tests/web/test_settings.py` | 2 | La configuración carga con el entorno vacío; ninguna variable es obligatoria en desarrollo |
| `tests/web/test_rescate.py` | 3 | Los tres paquetes rescatados importan sin Django y sin Streamlit; el registro cerrado sigue teniendo 5 fuentes |
| `tests/web/conftest.py` | 4 | Los *fixtures* `usuario`, `otro_usuario` y `administrador` que usa **toda** la suite web desde el paso 5 |
| `tests/web/test_cuentas.py` | 4 | `AUTH_USER_MODEL`, unicidad del correo, tope de gasto por defecto, registro en el panel |
| `tests/web/test_acceso.py` | 5 | Redirección con `next`, mensaje genérico único, `405` en un `GET` a `/salir/`, rotación de sesión al cambiar la contraseña |
| `tests/web/test_caso.py` | 6 | Ida y vuelta del `payload`; el gestor por defecto oculta los borrados en suave; borrar un usuario con casos levanta `ProtectedError` |
| **`tests/web/test_aislamiento.py`** | 7, ampliado en 11, 14 y 21 | **La prueba que más importa de todo el proyecto** — abajo |
| `tests/web/test_guarda_unica.py` | 7 | Ninguna vista consulta `Caso` por su cuenta: la guarda es el único camino |
| `tests/web/test_forms.py` | 10 | Validación del formulario y título derivado |
| `tests/web/test_analisis_view.py` | 11 | El ciclo POST → motor → persistencia → redirect, con propietario |
| `tests/web/test_result_template.py` | 12 | Contenido renderizado: rango, tarjetas, estados vacíos, landmarks |
| `tests/web/test_theme_tokens.py` | 13 | Cada clave de `COLORS` tiene su variable en `tokens.css`; `app.css` no lleva ni un hexadecimal |
| `tests/web/test_informe_view.py` | 14 | El PDF servido por la web lleva el literal `DATOS SINTÉTICOS` |
| `tests/web/test_listado.py` | 15 | Búsqueda, filtro, orden, los dos estados vacíos, tope de página en servidor, borrado suave |
| `tests/web/test_cuota.py` | 16 | El tope de gasto, con un doble de cliente que **lanza si alguien lo llama** |
| `tests/web/test_ia_degradacion.py` | 17 | Las cinco rutas de degradación, todas con dobles y sin red |
| `tests/web/test_corpus_indice.py` | 19 | El reindexado es idempotente y el índice coincide con los ficheros en disco |
| `tests/web/test_corpus.py` | 20 | Índice, ficha, `404` y `400` para una ruta fuera del corpus |
| `tests/web/test_estudio.py` | 21 | Publicadas frente a borradores, y **la invariante: una unidad de estudio nunca es fuente citable** |
| `tests/web/test_contrastados.py` | 22 | Un precedente publicado lo ve todo el mundo; curar no desprivatiza el caso original |
| `tests/web/test_evaluacion.py` | 23 | El arnés, con dobles; la puerta sale 1 al bajar de la línea base |
| `tests/web/test_copia.py` | 24 | Copia, restauración en limpio y comparación de recuentos de las ocho tablas |
| `tests/web/test_accesibilidad.py` | 25 | Landmarks, etiquetas, errores como texto, `role="img"` en el SVG, aviso de privacidad |
| `tests/web/test_seguridad.py` | 26 | Cabeceras, CSRF, y que las marcas seguras de cookie no están activas en local |

`tests/web/__init__.py` es **obligatorio** y lo crea el paso 2: sin él, pytest no inserta la raíz del
proyecto en `sys.path` para esa carpeta y ninguna prueba podría importar `config` ni `apps` (§19.6,
matriz de resolución).

### Aislamiento por propietario — la prueba que decide si el producto es publicable

`tests/web/test_aislamiento.py` monta **dos usuarios con un caso cada uno** y comprueba que cada
intento cruzado responde **`404`, nunca `403`**: ver el detalle, descargarse el informe, borrar, y
aparecer en el listado del otro. La distinción no es cosmética. Un `403` sobre un identificador ajeno
**confirma que ese identificador existe**, y con eso se enumera la base de datos de otro usuario sin
llegar a ver una sola fila. El `404` no distingue "no existe" de "no es tuyo", que es exactamente la
propiedad que se quiere.

La suite comprueba además el mismo `404` para un UUID que no existe en ninguna tabla: si las dos
respuestas no fueran idénticas, la diferencia sería el canal de fuga.

El fichero **crece con la superficie**: nace en el paso 7 con el detalle, y los pasos 11, 14 y 21 le
añaden su caso cruzado en el mismo paso en que crean la ruta. Nunca se aplaza a un paso posterior —una
ruta con propietario y sin su prueba de aislamiento es una ruta que nadie ha comprobado—.

**No hay capa E2E**, y es una decisión con nombre: es un No-Goal de §1. El cliente de pruebas de Django
recorre el ciclo completo —URL, middleware de sesión, vista, formulario, motor, base de datos,
plantilla— sin navegador. Lo único que no cubre es JavaScript, y este proyecto no tiene ni un fichero
`.js` (§6).

### Flujos críticos, cubiertos de extremo a extremo por la suite web

1. **Entrar, enviar una operación válida y descargar su informe.** Es el producto entero: si se rompe,
   no hay producto. Pasos 5, 11, 12 y 14.
2. **Pedir el caso de otro usuario.** Si esto falla, el sistema no es publicable a un segundo usuario, y
   el esquema es multiusuario desde el paso 4. Paso 7 y siguientes.
3. **Enviar una operación inválida.** El caso que más veces se ejecuta en la vida real y el que peor se
   suele cubrir. Pasos 10 y 11.
4. **Analizar sin clave de API, o con la cuota agotada.** Es la ruta por defecto: la mayoría de las
   ejecuciones no tendrán clave, y el informe tiene que salir completo declarando la ausencia. Pasos
   16 y 17.
5. **Analizar una operación sin comparables aceptados.** Un rango que no se puede calcular es un
   resultado, no un fallo, y la pantalla y el PDF tienen que decirlo. Pasos 11, 12 y 14.
6. **Perder la base de datos y recuperarla.** Copia, restauración en un directorio limpio y comparación
   de recuentos de las ocho tablas. Paso 24.

### Datos de prueba

`pytest-django` crea y destruye una base de datos SQLite temporal por sesión; con SQLite no hace falta
ningún servicio, ningún contenedor y ningún fichero de aprovisionamiento —por eso §19.6 no emite
ninguno—. Cada prueba que escribe usa el marcador `django_db`, que envuelve cada caso en una
transacción y la revierte: **ninguna prueba comparte estado mutable con otra y ninguna depende del
orden de ejecución.**

Los usuarios de prueba los crean los *fixtures* de `tests/web/conftest.py` —`usuario`,
`otro_usuario` y `administrador`—, que **escribe el paso 4**, nunca el comando de alta inicial: los tres se construyen en memoria y desaparecen con
la transacción. Los objetos de dominio se construyen con los *fixtures* que ya existen en
`tests/domain/conftest.py` (`make_transaction`) y en `tests/ai/mocks.py`.

**La capa de IA se prueba siempre con dobles inyectados por parámetro: ni una prueba de este proyecto
toca la red.** En el paso 16 el doble es más exigente todavía —lanza `AssertionError` si alguien lo
llama—, que es la única forma de comprobar *"antes de cualquier llamada al proveedor"* en un medio
donde esa propiedad es observable (§9 regla 12).

### Lo que deliberadamente no se prueba

- **El aspecto.** No hay pruebas de píxel ni de instantánea visual. Se fijan los contenidos y la
  estructura del HTML; el color y la disposición se miran.
- **El renderizado del PDF, más allá de su texto.** `pypdf` extrae texto, no maquetación. Que una tabla
  no se salga de la caja se comprueba abriendo el documento.
- **El comportamiento real de un lector de pantalla y el reflujo a 320 px.** No son observables desde un
  análisis del HTML (§9 regla 12); están en los gates manuales de §20.1.
- **El contenido de la explicación de IA.** Se valida su *forma* y sus *citas* —que es lo que el
  producto garantiza—, no su calidad literaria, que no es falsable. Lo más cerca que se llega es el
  arnés del paso 23, que mide una tasa de acierto contra propiedades comprobables, no contra el gusto.
- **La concurrencia.** Un proceso, un usuario a la vez, SQLite. No hay carreras que provocar.

---

## 14. Seguridad y secretos

| Preocupación | Control | Implementado en |
|---|---|---|
| Almacenamiento de secretos | `.env` fuera del control de versiones, con `!.env.example` como única excepción explícita | §10 Bootstrap, paso 3 del bloque |
| Rotación de secretos | Manual. `ANTHROPIC_API_KEY` se revoca y se regenera en la consola de Anthropic; `DJANGO_SECRET_KEY` se regenera con `secrets.token_urlsafe(64)`. Sin cadencia fija: no hay sesiones que invalidar ni usuarios a los que echar | §10, tabla de variables |
| Validación de entrada | Doble y en un solo mensaje: `django.forms` para la forma, `Transaction` de pydantic para las invariantes del dominio | `apps/analisis/forms.py`, paso 10 |
| Codificación de salida / XSS | Autoescapado de las plantillas de Django, activo por defecto. **Ninguna plantilla usa `|safe` sobre datos de entrada.** Hay dos excepciones y las dos son contenido de confianza escrito por quien administra: el Markdown del corpus, que vive en el repositorio, y el de las unidades de estudio, redactado desde el panel por una cuenta `is_staff` | `templates/`, `apps/corpus/views.py`, `apps/estudio/views.py`, pasos 20 y 21 |
| Inyección SQL | Solo el ORM. No hay ni una consulta construida con cadenas en todo el proyecto | `apps/`, pasos 6 en adelante |
| Autenticación | `django.contrib.auth` con modelo propio `cuentas.Usuario`; sesión en cookie `HttpOnly` respaldada en base de datos; alta y baja desde el panel; **cierre por omisión** vía `ExigirAutenticacion`, que exige sesión en todo salvo una lista blanca explícita (§8) | `apps/comun/middleware.py`, `apps/cuentas/`, pasos 4 y 5 |
| Autorización y aislamiento por propietario | **Una guarda única con nombre**, `apps/comun/guardas.py::caso_del_usuario()`, por la que pasa todo lector de una fila con dueño. Un recurso ajeno responde **404, nunca 403**: un 403 confirmaría que el id existe. Comprobado por `tests/web/test_aislamiento.py` y por la comprobación negativa de `test_guarda_unica.py`, ambas en el gate de §20.1 | `apps/comun/guardas.py`, `apps/comun/consultas.py`, paso 7 |
| Superficie de red | Complementa a lo anterior, no lo sustituye: el despliegue de la v1 es local, `ALLOWED_HOSTS = ["127.0.0.1", "localhost"]` y el servidor escucha solo en la interfaz local (§12, §20.3 decisión 3b) | `config/settings/`, pasos 1 y 25 |
| CSRF | `CsrfViewMiddleware` activo y `{% csrf_token %}` en el formulario, aunque no haya sesiones: es la defensa contra que otra pestaña haga POST a `127.0.0.1:8000` | `config/settings/base.py`, `templates/analisis/form.html`, pasos 1 y 12 |
| Recorrido de rutas | `apps/corpus/indexador.py` resuelve la ruta pedida y comprueba que sigue dentro de `documentation/tax-research/`; cualquier `..`, ruta absoluta o enlace que se salga responde `400` sin leer nada | `apps/corpus/indexador.py`, pasos 19 y 20 |
| Contraseñas | Los cuatro `AUTH_PASSWORD_VALIDATORS` por defecto de Django y su hasher por defecto, sin tocar. Mensaje de acceso **genérico e idéntico** para usuario inexistente, contraseña incorrecta y cuenta inactiva: distinguirlos revelaría qué cuentas existen | `apps/cuentas/views.py`, paso 5 |
| Redirección abierta | El `next` del formulario de acceso se acepta **solo si apunta a una ruta local**; cualquier destino externo se descarta en silencio | `apps/cuentas/views.py`, paso 5 |
| Tope de gasto | `comprobar_cuota()` **antes** de construir el cliente, nunca dentro. Superarlo desactiva la sección de IA sin bloquear el producto y sin registrar gasto (§17) | `apps/ia/cuota.py`, paso 16 |
| Copia de seguridad | Copia en línea de SQLite —copiar el fichero con el proceso escribiendo produce un fichero corrupto sin avisar— y **restauración verificada por recuento de filas** de las ocho tablas. `copias/` está fuera del repositorio (§20.2, riesgo 3) | `apps/comun/management/commands/`, paso 24 |
| Límite de peticiones / abuso | Ninguno en la aplicación. Un usuario, en local. El consumo que sí puede dispararse es el de tokens, acotado en §17 | — |
| Verificación de webhooks | NO APLICA — este proyecto no recibe ningún webhook | — |
| Auditoría de dependencias | `uv sync --frozen` en CI garantiza que se instala exactamente el árbol de `uv.lock`; cualquier deriva rompe el trabajo | `.github/workflows/ci.yml`, paso 27 |
| Cabeceras de seguridad | Literales: `SECURE_HSTS_SECONDS = 31536000`, `SECURE_HSTS_INCLUDE_SUBDOMAINS = True`, `SECURE_HSTS_PRELOAD = True`, `SECURE_SSL_REDIRECT = True`, `SECURE_CONTENT_TYPE_NOSNIFF = True`, `SECURE_REFERRER_POLICY = "same-origin"`, `CSRF_COOKIE_SECURE = True`, `X_FRAME_OPTIONS = "DENY"` | `config/settings/production.py`, paso 26 |
| Datos personales | **El sistema sí almacena algunos, y hay que decirlo.** `Usuario` guarda nombre de cuenta, correo y hash de contraseña; `Caso` guarda una descripción de operación, dos códigos de país, un importe, un tipo y una fecha, y si el usuario escribe en la descripción el nombre de una persona física, ese texto queda en `payload` y en el PDF. `LlamadaLLM` guarda gasto imputado a una cuenta. Retención: ninguna automática en la v1. Vía de borrado: un caso se borra en suave desde su propia página (paso 15) y de forma definitiva por el administrador; una cuenta se desactiva, **nunca se borra**, porque las claves foráneas son `PROTECT` (§4.2). Todo esto se declara al usuario en `/privacidad/` (§8, paso 25) | `apps/cuentas/models.py` y `apps/analisis/models.py`, pasos 4, 6 y 24 |
| Acceso del administrador a datos ajenos | Una cuenta con `is_staff` ve los casos de todos los usuarios desde el panel. Es inevitable —alguien tiene que curar precedentes y auditar el gasto— y por eso **no se deja implícito**: el aviso de privacidad aparece en el pie de toda página autenticada y junto al formulario de creación, antes de que el usuario escriba el dato | `templates/base.html`, `templates/analisis/form.html`, paso 25 |
| Higiene del registro | `structlog` registra ids, usuario, países y resultados. **Nunca registra la clave de API, ni la contraseña, ni el cuerpo del formulario, ni el texto que devuelve el modelo.** Los eventos de la capa de IA registran la *categoría* del fallo, no su contenido, y `LlamadaLLM.error` guarda esa categoría, nunca la respuesta | `config/logging.py`, `apps/analisis/services.py`, pasos 2 y 17 |

**Reglas duras**

- Ningún secreto se versiona, se imprime en un registro, se envía a un rastreador de errores ni se
  incrusta en nada que llegue al navegador. Todo lo que llega al navegador es público.
- Toda comprobación del servidor se hace **antes** del trabajo, no después.
- La capa de IA **nunca** recibe la clave por descubrimiento propio: se la inyecta `services.py` desde
  la configuración (paso 5, paso 12).

**Datos regulados.** Este sistema no trata datos de salud, ni financieros de personas físicas, ni de
menores. Trata información fiscal de entidades jurídicas, que **no** es dato personal en el sentido del
RGPD mientras no identifique a una persona física. Con una excepción a la que hay que estar atento: si
el usuario escribe en `description` el nombre de una persona física —un administrador, un consultor—,
ese texto entra en `payload` y en el PDF. La mitigación es de producto y está escrita: el campo pide
una descripción de la operación, no de sus intervinientes.

---

## 15. Accesibilidad

**Objetivo: WCAG 2.2 nivel AA.** No es acabado: en la UE es una obligación legal en expansión, y
retrofitarla cuesta varias veces lo que cuesta construirla dentro. Por eso los criterios de
accesibilidad están en las listas "Done when" del paso 14 y no en un backlog.

### Requisitos base

| Requisito | Regla en este proyecto |
|---|---|
| HTML semántico | `<header>`, `<main id="contenido">`, `<footer>` en `base.html`; un solo `<h1>` por página; encabezados en orden; listas para lo que es una lista (factores de riesgo, fuentes, comparables) |
| Teclado | Todo elemento interactivo alcanzable y operable con teclado. El proyecto no tiene JavaScript, así que no hay ninguna trampa de foco que crear: los controles son los nativos del navegador |
| Enlace de salto | Primer elemento enfocable del documento, `href="#contenido"`, visible al recibir el foco |
| Foco visible | `:focus-visible` con anillo de `var(--tpip-focus)` (`#1F4E79`, 8,66:1 contra blanco) de 2px y `outline-offset: 2px` |
| Contraste | Texto 4,5:1; texto grande y límites de componente 3:1. La paleta de §7 ya lo cumple, con los tres pares ajustados medidos y anotados |
| Formularios | `<label for>` programático en todos los campos; los errores son **texto**, nunca solo color; los errores generales en un contenedor `role="alert"`, los de campo referenciados por `aria-describedby` |
| Imágenes | El SVG del rango lleva `role="img"` y un `<title>` que dice en palabras dónde cae el tipo respecto del rango — el equivalente textual **es** la información que el producto da |
| Movimiento | Las dos únicas transiciones del proyecto viven dentro de `@media (prefers-reduced-motion: no-preference)`: la ausencia de movimiento es el estado por defecto |
| Zoom y reflujo | Usable al 200% y a 320 px de ancho sin desplazamiento horizontal. Las tablas anchas (anexo de comparables) se desplazan dentro de su propio contenedor con `overflow-x: auto`, no arrastran la página |
| Regiones activas | No hay contenido asíncrono: todo cambio de estado llega con una respuesta completa del servidor. No hace falta ningún `aria-live`, y ponerlo sin motivo sería ruido para un lector de pantalla |

### Añadidos de WCAG 2.2 — los que más se olvidan

| Criterio | Cómo se cumple aquí |
|---|---|
| 2.4.11 Foco no oculto (mínimo) | No hay cabeceras fijas, ni barras de cookies, ni notificaciones flotantes. Nada puede tapar el elemento enfocado, y es una razón más para no añadirlas |
| 2.5.7 Movimientos de arrastre | No hay ninguna interacción de arrastre en el producto |
| 2.5.8 Tamaño del objetivo (mínimo) | Botones y enlaces de acción con al menos 24×24 px CSS; los enlaces en línea dentro de un párrafo quedan amparados por la excepción de texto en línea |
| 3.3.7 Entrada redundante | El formulario es de un solo paso: no hay nada que volver a teclear. Cuando una validación falla, **el formulario se reenvía con todos los valores ya introducidos**, nunca en blanco |
| 3.3.8 Autenticación accesible (mínimo) | **Sí aplica desde el paso 5.** El acceso es usuario y contraseña, sin CAPTCHA, sin acertijo y sin ninguna prueba de función cognitiva. Los campos llevan `autocomplete="username"` y `autocomplete="current-password"` para que un gestor de contraseñas los rellene, y **no se bloquea el pegado** en ningún campo. Es un requisito con criterio propio en el paso 25 |

### Verificación

```powershell
uv run pytest tests/web/test_accesibilidad.py -q
if ($LASTEXITCODE -ne 0) { throw 'las comprobaciones de accesibilidad fallan' }   # expect: exit 0, 0 violaciones estructurales
```

**No hay `axe` y es deliberado:** ejecutarlo exigiría un runtime de Node y un navegador, que son
No-Goals de §1. Lo que se comprueba automáticamente es lo que un análisis del HTML renderizado puede
decidir: `lang`, landmarks, un solo `h1`, enlace de salto, etiquetas de campo, errores como texto,
`role` y `<title>` del SVG. Es aproximadamente lo mismo que detectaría una herramienta automática, que
en cualquier caso cubre en torno a un tercio de los problemas reales.

El resto son pases manuales, una vez, antes de dar el proyecto por cerrado, y están en §20.1:
recorrido completo con teclado del flujo formulario → resultado → descarga; un pase con lector de
pantalla sobre ese mismo flujo, con atención al `<title>` del gráfico; y un pase al 200% de zoom y a
320 px de ancho.

---

## 16. Observabilidad y coste

### Instrumentación

| Señal | Herramienta | Qué captura | Quién la mira |
|---|---|---|---|
| Errores | La traza de Django en consola, en desarrollo; `structlog` a nivel `error` con el id del análisis | Excepciones no controladas | El propio usuario, en el momento |
| Registros | `structlog` sobre `logging`, a consola, con marca de tiempo ISO | Un evento por análisis: id, jurisdicciones, posición en el rango, si hubo explicación de IA y, si no, por qué categoría | El propio usuario |
| Métricas | Consultas sobre las tablas `casos` y `llamadas_llm` | Las cuatro de abajo | El propio usuario, cuando quiera |
| Disponibilidad | NO APLICA | No hay nada desplegado que vigilar (§12) | — |

**No hay Sentry, ni Datadog, ni nada externo, y es una decisión.** Un servicio de rastreo de errores
para una aplicación local con un usuario añade una cuenta, una clave, una dependencia y un canal por el
que se pueden escapar datos —justo lo que §14 prohíbe—, a cambio de avisar a la misma persona que ya
está mirando la consola.

### Las métricas que importan en este proyecto

Son cuatro, y las cuatro se responden con una consulta sobre `casos` y `llamadas_llm`. Ninguna necesita
instrumentación adicional; ese es el motivo de que `engine_version`, `dataset_version` y
`has_ai_explanation` estén desnormalizados fuera de `payload` (§4).

| Métrica | Objetivo | Se avisa cuando |
|---|---|---|
| Tasa de degradación de la capa de IA — `has_ai_explanation=False` con clave configurada | < 10% de los análisis | Supera el 25%: significa que los borradores se están rechazando de forma sistemática y hay que mirar el prompt o el validador |
| Análisis con un factor de riesgo `no_comparables` | < 5% | Supera el 20%: el dataset no cubre lo que la gente pregunta |
| Análisis con `thin_sample` (muestra por debajo de 5 comparables) | < 20% | Supera el 40%: el rango se está calculando sobre muestras que no lo sostienen |
| Mezcla de versiones de motor entre los análisis guardados | Una sola `engine_version` entre los 30 últimos | Aparecen tres o más: hay informes emitidos con lógicas distintas circulando a la vez |

### Comprobación de salud

**NO APLICA como endpoint** — no hay nada desplegado que sondear (§12). Su equivalente local es
`uv run python manage.py check`, que verifica configuración y aplicaciones, más
`uv run python manage.py migrate --check`, que verifica que el esquema está al día. Los dos están en el
gate de §20.1.

### Modelo de coste

| Servicio | Capa gratuita | Coste al volumen esperado de la v1 | Coste a 10× | Punto de inflexión |
|---|---|---|---|---|
| Alojamiento | — | **0 €** | 0 € | No hay: se ejecuta en el equipo del usuario |
| Base de datos | — | **0 €** | 0 € | SQLite es un fichero |
| API de Anthropic | Ninguna | Consumo por tokens de la explicación: `max_tokens = 1500` por intento y hasta 2 intentos por análisis. Con uso semanal, decenas de llamadas al mes | Sigue siendo consumo por tokens, lineal | Un bucle de reintentos. **No lo hay**: `MAX_ATTEMPTS = 2`, fijo en el código y cubierto por las pruebas rescatadas |

**Coste mensual estimado en el arranque: 0 € de infraestructura, más el consumo de tokens de la capa de
IA, que es opcional y se apaga quitando `ANTHROPIC_MODEL` del `.env`.** La partida mayor es, por tanto,
la única que existe, y la palanca más barata para recortarla es literalmente una línea del `.env`.
Ningún servicio de este proyecto escala de forma superlineal con el uso.

---

## 17. Enrutado de modelos

Este proyecto **sí** llama a un modelo de lenguaje en ejecución, en un único punto: la explicación
narrativa de un análisis **ya calculado**.

**Este blueprint no escribe ningún identificador de modelo, ningún precio y ningún límite de contexto,
y es deliberado.** El identificador es **configuración** (`ANTHROPIC_MODEL`), no código —esa es
exactamente la corrección del defecto 1 en el paso 8—, y fijar aquí un id concreto reintroduciría por
la puerta de atrás el problema que ese paso resuelve: un valor que envejece dentro de un artefacto que
nadie vuelve a mirar. Los únicos parámetros de API que este documento recoge son los que **ya están en
el código rescatado** y que esta migración no cambia: `max_tokens = 1500`, `temperature = 0.2` y
`MAX_ATTEMPTS = 2`, todos en `ai/claude_client.py`.

### Tabla de enrutado

| Tarea en este producto | Nivel de modelo | Por qué ese nivel | Alternativa si falla |
|---|---|---|---|
| Redactar la explicación narrativa de un análisis ya calculado, citando solo fuentes que el motor emitió | Nivel intermedio de la familia (el que el usuario fije en `ANTHROPIC_MODEL`) | El trabajo es de redacción fiel sobre datos dados, con restricciones duras y verificables por el validador. No hay razonamiento abierto ni cálculo: **el motor ya calculó** | **Ninguna: no hay repliegue a otro modelo.** Si falla, la capa se desactiva y el informe sale completo declarando la ausencia. Un repliegue silencioso a otro modelo produciría informes redactados por modelos distintos sin que nadie lo hubiera decidido |
| Cualquier cálculo, veredicto, percentil, puntuación o clasificación | **Ninguno** | El principio rector: **el motor calcula; el modelo explica, fundamenta y puede sugerir, pero nunca decide y nunca escribe un número** | — |

### Prompt y estrategia de contexto

El prompt vive como fichero versionado en `ai/prompts/explain_analysis_v1.md`, y **el nombre del
fichero es la versión**: `PROMPT_VERSION` en `ai/schemas.py` lo referencia, y esa cadena viaja dentro de
`AIExplanation.prompt_version`, de modo que un informe emitido hoy dice con qué prompt se redactó. El
bloque de sistema se extrae del fichero delimitado por una valla de código; cambiar el prompt significa
crear `explain_analysis_v2.md` y cambiar la constante, nunca editar el v1 en su sitio.

El turno de usuario es **exclusivamente** el volcado JSON de `ExplanationRequest`, construido por
`ExplanationRequest.from_result`: la transacción, el rango, los veredictos, los factores de riesgo y la
lista cerrada de fuentes permitidas. El modelo no ve nada más, y en particular no ve el registro
completo de fuentes: solo las que el motor emitió para **este** análisis.

No hay caché de prefijo estable y no hace falta: el volumen es de decenas de llamadas al mes y cada
petición lleva un análisis distinto.

### Controles de coste

Son cuatro, y están ordenados de más duro a más blando: los dos primeros son mecanismos que el
sistema impone, el tercero es un interruptor y el cuarto es una señal.

**1. El tope mensual por cuenta — el freno de mano.** Cada `Usuario` lleva `tope_gasto_mensual_eur`
(§4), con `5,00 €` por defecto, que fija el administrador desde el panel. Antes de **cada** llamada,
`apps/ia/cuota.py::comprobar_cuota(usuario)` suma el `coste_eur` de las `LlamadaLLM` de ese usuario en
el mes natural en curso y, si alcanza o supera el tope, levanta `CuotaSuperada`:

> **CUANDO un usuario supere su tope EL SISTEMA DEBERÁ rechazar la petición antes de cualquier llamada
> al proveedor, con cero gasto registrado.**

Tres cosas hacen que esa frase sea comprobable y no un deseo. La comprobación va **antes de construir
el cliente**, no dentro de él, y el paso 17 lo verifica por posición en el fichero. La prueba del
paso 16 inyecta un doble que **lanza si alguien lo llama**: si la cuota funciona, ese doble no se toca
nunca. Y el freno se construye en el paso 16, **antes** de que la capa de IA se conecte en el 17 —un
tope que se añade después de que algo ya funciona es un tope que nunca se prueba en el camino que
importa—.

Superar el tope **desactiva la sección de IA, nunca bloquea el producto**: el análisis se calcula, el
caso se persiste y el informe sale completo declarando la ausencia de la explicación. Es la misma ruta
de degradación que la falta de clave.

**2. El techo por llamada, en el código.** `max_tokens = 1500` por intento y `MAX_ATTEMPTS = 2`, ambos
en `ai/claude_client.py` y cubiertos por las pruebas rescatadas. El segundo intento envía **únicamente
los motivos de rechazo**, nunca el análisis otra vez: además de ser más barato, cierra una puerta —
añadir contexto nuevo en la corrección permitiría que el segundo borrador dijera cosas que el primero
no podía decir—.

**3. El interruptor general.** Vaciar `ANTHROPIC_MODEL` en el `.env` desactiva la capa entera, sin
tocar código y sin degradar el informe. Desde el paso 8 el modelo no se descubre solo, así que esa
variable vacía es una decisión efectiva y no una sugerencia.

**4. La señal.** La tasa de degradación de §16: si sube, se está pagando por borradores que se
rechazan. Y `EjecucionEvaluacion` (§4) registra `coste_total_eur` **junto a** `tasa_acierto`, porque
una mejora de precisión que triplica el coste es una decisión, no una mejora.

#### Cómo se mide el gasto — reportado, nunca estimado

`LlamadaLLM` (§4) guarda los cuatro contadores que devuelve el proveedor en `usage` —entrada, salida,
escritura de caché y lectura de caché—, la razón de finalización, la latencia, el intento, el propósito
(`explicacion` o `evaluacion`) y el usuario al que se imputa. **`ai/` no cuenta tokens: los transporta**
(paso 8), y `apps/ia/cuota.py::coste_de()` los convierte a euros con las tarifas de la configuración.

Un recuento propio divergiría del que factura el proveedor, y entonces el tope vigilaría un número que
no es el que se paga. El paso 16 lo comprueba buscando en `apps/ia/` cualquier rastro de estimación
local (`count_tokens`, `tiktoken`, contar palabras) y fallando si aparece.

El campo `proposito` existe por una razón concreta: sin él, el coste del arnés de evaluación (paso 23)
y el del producto se sumarían en el mismo número, y una pasada de evaluación consumiría el tope mensual
de un usuario real.

#### Coste por análisis, con las cifras verificadas

| Concepto | Valor |
|---|---|
| Modelo de referencia | `claude-opus-5` |
| Tarifa de entrada | **5 $ por millón de tokens** |
| Tarifa de salida | **25 $ por millón de tokens** |
| Coste por análisis, sin caché | **entre 4 y 5 céntimos** |
| Coste por análisis, con caché de prompt | **entre 1 y 2 céntimos** |

Con el tope por defecto de `5,00 €` al mes eso son del orden de **100 a 125 análisis mensuales por
cuenta** sin caché, y de 250 a 500 con ella. Para un uso semanal sobra de largo, y ese es justamente el
punto: el tope no está para racionar, está para que un bucle accidental o una tanda de pruebas contra la
API real no se lleven por delante una factura antes de que nadie lo note.

**El identificador del modelo y sus tarifas son configuración, no código.** `ANTHROPIC_MODEL`,
`PRECIO_ENTRADA_EUR_POR_MTOK` y `PRECIO_SALIDA_EUR_POR_MTOK` viven en el `.env` (§10) y se leen desde
`config/settings/base.py`. Las cifras de la tabla son las verificadas para el modelo de referencia el
2026-08-15 y están en dólares tal como las publica el proveedor; la conversión a euros la fija el
administrador al rellenar esas dos variables, que es donde tiene que estar una decisión que depende del
tipo de cambio del día. Con las tarifas sin fijar, `coste_de()` devuelve `0` en vez de fallar: un
sistema sin tarifas configuradas registra uso pero no puede imputar gasto, y decirlo con un cero es más
honesto que inventar un precio.

### Manejo de fallos

**El contrato de esta capa, en una frase: puede fallar entera sin que se note en el informe.** Está ya
implementado en `ai/claude_client.explain_analysis`, que **no lanza nunca**, y esta migración lo
mantiene:

| Fallo | Qué ocurre |
|---|---|
| No hay `ANTHROPIC_API_KEY` | La capa se desactiva. Ni una llamada de red |
| No hay `ANTHROPIC_MODEL` | La capa se desactiva. Ni una llamada de red. **Desde el paso 8 el modelo no se descubre solo** |
| La API falla, agota el tiempo o devuelve un error | `ClaudeUnavailable`, registrado a nivel `info`, y `None` hacia arriba |
| El borrador no es JSON válido, o no cumple el esquema | Rechazo, un reintento con los motivos, y si vuelve a fallar, `None` |
| El borrador cita una fuente que el motor no emitió | Rechazo del validador. Y aunque el validador fallara, `AnalysisResult` **no se puede construir** con esa explicación: la gobernanza está en el modelo de datos, no solo en el prompt |
| Cualquier otra excepción inesperada | Se captura, se registra con traza y se devuelve `None`. Nada puede tumbar el informe |

Lo que el usuario ve en todos esos casos es el mismo informe completo, con la sección de IA declarando
su ausencia en vez de dejar un hueco.

### Evaluación

El conjunto fijo de entradas con propiedades esperadas que corre antes de cualquier cambio de prompt o
de modelo es **`tests/ai/`, las 53 pruebas rescatadas**, más las cuatro rutas de degradación de
`tests/web/test_ia_degradacion.py` (paso 17). Comprueban lo que el producto garantiza y que es
falsable: que un borrador con una cita no emitida se rechaza, que un borrador fuera del rango de
extensión se rechaza, que el reintento solo lleva los motivos, y que el fallo nunca sale de la capa. No
comprueban la calidad literaria del texto, que no es falsable (§13).

**Regla de despliegue de prompts:** ningún cambio de `explain_analysis_v*.md` ni de `ANTHROPIC_MODEL` se
da por bueno sin que esa suite pase entera. Sin ella, editar un prompt es una operación sin evidencia.

---

## 18. Skills a usar durante la construcción

Nombres, forma de invocación y comandos de instalación copiados literalmente de
`knowledge/skills-registry.md`. **Ninguna de las tres lleva barra inclinada: las tres se activan solas
por intención**, y escribir una forma con barra sería una no-operación silenciosa que dejaría el paso
sin la ayuda que este blueprint da por supuesta.

| Skill | Pasos de construcción | Qué aporta ahí | Instalación |
|---|---|---|---|
| `ui-ux-pro-max` | 12, 13, 15, 24 | El sistema visual concreto sobre la paleta ampliada del paso 9: escala tipográfica, ritmo vertical, estilo de componente y decisiones de disposición para que el rango funcione como protagonista | `/plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill`<br>`/plugin install ui-ux-pro-max@ui-ux-pro-max-skill` |
| `frontend-design` | 12, 15, 19, 20, 24 | Plantillas y CSS con acabado de producción y accesibilidad incorporada, en vez de la maqueta por defecto que sale de un framework de servidor | `/plugin marketplace add anthropics/skills`<br>`/plugin install example-skills@anthropic-agent-skills` |
| `pdf` | 14 | Lectura y comprobación de PDF cuando la extracción de texto del paso 14 no dé lo esperado; es el sitio donde asomaría un cambio de comportamiento de `reportlab` (§20.2, riesgo 2) | `/plugin marketplace add anthropics/skills`<br>`/plugin install document-skills@anthropic-agent-skills` |

**Ninguna es una dependencia dura.** Si una no está disponible, el constructor sigue con lo que dice
este blueprint —§7 tiene la paleta, la tipografía y el espaciado en literales; §15 tiene los requisitos
de accesibilidad uno a uno; §13 tiene la estrategia de comprobación del PDF—, anota el repliegue en una
línea y continúa. Ningún paso se bloquea por una skill ausente.

No se recomienda `playwright-cli` (no hay E2E, No-Goal de §1) ni `/claude-seo-ai` (no hay superficie
pública que indexar).

---

## 19. Espacio de trabajo del agente

El proyecto se entrega con su propia configuración de agente. No es un solo `CLAUDE.md`: es un espacio
de trabajo, porque un fichero plano de instrucciones deja de leerse a medida que crece y no puede
expresar reglas acotadas por ruta.

En modo bundle, estos ficheros son reales y viven bajo `blueprints/tpip/workspace/`, que **replica
exactamente la disposición del proyecto**: la ruta de un fichero dentro de `workspace/` es su ruta en el
proyecto.

```
./blueprints/tpip/workspace/
├── CLAUDE.md                    # §19.1
├── AGENTS.md                    # §19.2
├── pyproject.toml               # §19.6 — YA EMITIDO
├── .gitignore                   # §19.6
├── .env.example                 # §19.6
└── .claude/
    ├── settings.json            # §19.3
    ├── skills/<nombre>/SKILL.md # §19.4
    └── rules/<nombre>.md        # §19.5
```

**La copia es una sola, no destructiva, y la escribe §10** (paso 2 de su bloque): recorre
`workspace/` y copia únicamente los ficheros que no existen ya en destino. Está escrita así porque
volver a ejecutar el bootstrap es la reacción más natural de un constructor atascado, y una copia
recursiva sin guarda revertiría `pyproject.toml` a su versión sin dependencias resueltas —con lo que el
comando siguiente fallaría diciendo que falta un binario, que se lee como una instalación rota y no
como un fichero pisado—. **Nunca se sobrescriben, una vez existen: `pyproject.toml`, `uv.lock`,
`.gitignore`, `.env.example` y `.claude/settings.json`.** La forma elegida (`Test-Path` antes de
`Copy-Item`) **sale con 0 tanto si copia como si no**, en PowerShell 5.1 y superiores, que es la única
plataforma que este proyecto tiene como objetivo.

**Todo lo que se emite aquí pasa los gates del propio proyecto.** Conviene decir por qué es fácil en
este caso: **ninguno de los ficheros emitidos es Python.** `pyproject.toml` es TOML, `.gitignore` y
`.env.example` son texto plano y `settings.json` es JSON; `ruff format` y `ruff check` solo miran
ficheros `.py`, y `mypy` también. El único fichero emitido que una herramienta del proyecto lee de
verdad es `pyproject.toml`, y lo lee como configuración suya.

**`.claude/commands/` no se emite jamás** —ni aquí, ni en el bundle, ni en ningún modo—. Una orden de
barra solo se dispara cuando la teclea una persona, y un constructor autónomo no teclea nada: sería
peso muerto que no se invoca ni una vez. Todo flujo de trabajo repetible va a
`.claude/skills/<nombre>/SKILL.md` (§19.4), que se activa por intención.

### 19.1 `CLAUDE.md`

Se emite como fichero real en `blueprints/tpip/workspace/CLAUDE.md`, por debajo de 200 líneas,
siguiendo `templates/claude-md-template.md`, con **los comandos primero**. Su contenido cubre, en este
orden: los comandos de `uv run` de §10 y §20.1; la arquitectura en cinco frases (dominio rescatado /
capa de IA inyectada / infraestructura de informe / aplicaciones de Django / plantillas y tokens); el
principio rector literal; las reglas de frontera de §3; la convención de invocar los scripts con `-m`;
la invariante de las 180 pruebas rescatadas; y la prohibición de tocar `tp_domain/`, `ai/schemas.py`,
`ai/validators.py` e `infrastructure/report/` fuera de los pasos 8 y 9.

### 19.2 `AGENTS.md`

Se emite como fichero real en `blueprints/tpip/workspace/AGENTS.md`. Es un puente corto —entre 15 y 40
líneas— para las herramientas de agente que no leen `CLAUDE.md`: qué es el proyecto, los cinco comandos
que hacen falta, las tres reglas que más importan (el principio rector; el motor y sus pruebas no se
tocan; los scripts se invocan con `-m`) y un puntero a `CLAUDE.md` como fuente de verdad. **No es
opcional**: los agentes que no son Claude Code leen este fichero y ninguno más.

### 19.3 `.claude/settings.json`

Se emite como fichero real en `blueprints/tpip/workspace/.claude/settings.json`. Pre-aprueba **todos**
los comandos que aparecen en algún bloque `Verify` de §9 y en el gate de §20.1; sin eso, una
construcción desatendida se para a pedir permiso en cada gate, que es exactamente donde muere.

Las entradas de `permissions.allow` cubren, como conjunto mínimo: `uv sync`, `uv python install`,
`uv run` (que engloba `pytest`, `ruff`, `mypy`, `manage.py` y `python -m scripts.build_tokens`), y las
órdenes de git de solo lectura y de checkpoint (`status`, `diff`, `log`, `add`, `commit`, `tag`,
`ls-files`, `check-ignore`, `rev-parse`, `init`, `config`). En `deny`: leer `.env` y cualquier `.env.*`,
`git push` y `git push --force`, y `rm -rf`.

**No se pre-aprueba ningún comando de un servicio que este blueprint no aprovisione**, porque no hay
ninguno: este proyecto no levanta contenedores ni bases de datos externas. Los cmdlets de PowerShell
que usan los bloques `Verify` (`Test-Path`, `Get-Content`, `Select-String`, `Copy-Item`,
`Get-ChildItem`, `Add-Content`, `Move-Item`) no necesitan entrada en la lista: no son invocaciones de
`Bash`.

**Es JSON**: cada elemento de los arrays es una cadena de permiso. Una frase en prosa dentro del array
no es un comentario, es una regla que no coincide nunca —y a diferencia de una sección de prosa a
medio rellenar, un JSON a medio sustituir falla de forma invisible en ejecución.

### 19.4 Skills del proyecto — `.claude/skills/<nombre>/SKILL.md`

Se emiten como ficheros reales bajo `blueprints/tpip/workspace/.claude/skills/`. Cada uno lleva
frontmatter YAML con `name` y una `description` que dice **cuándo** usarlo —la descripción es lo único
que se carga hasta que la skill se dispara, así que una vaga no se dispara nunca—, y cada uno termina
con su propia comprobación.

| Skill | Se dispara con | Qué automatiza |
|---|---|---|
| `anadir-jurisdiccion` | "añadir un país", "modelar Francia", "nueva jurisdicción" | El procedimiento completo y en orden: primero la ficha de investigación en `documentation/tax-research/jurisdictions/`, con fuente primaria y cita literal; después la entrada en `tp_domain/sources.py`; después el mapa de `JURISDICTION_RANGE_RULES`; y las pruebas de dominio que lo fijan. **Impide lo que existe para impedir: añadir un país al mapa por analogía, sin ficha.** Un país sin ficha se queda en `NOT_MODELLED`, que no es un hueco, es una respuesta |
| `regenerar-tokens` | "he cambiado un color", "la paleta", "tokens desincronizados" | `uv run python -m scripts.build_tokens`, después `--check`, después `uv run pytest tests/web/test_theme_tokens.py`. Recuerda que se invoca con `-m` y por qué, y que `app.css` no puede contener ni un literal hexadecimal |
| `verificar-migracion` | "¿sigue todo bien?", "antes de commitear", "comprobar el paso" | El gate completo de §20.1 en el orden correcto, terminando siempre por `uv run pytest tests/domain tests/ai tests/report`, que es la red de seguridad. Recuerda que ese recuento tiene que seguir siendo 180 |

### 19.5 `.claude/rules/*.md`

Se emiten como ficheros reales bajo `blueprints/tpip/workspace/.claude/rules/`. Son convenciones
acotadas por ruta: el agente recibe las reglas del dominio cuando edita el dominio y las de plantilla
cuando edita una plantilla, en vez de un único fichero donde todo compite por la atención.

| Fichero | Globs de `paths` | Qué cubre |
|---|---|---|
| `.claude/rules/dominio-rescatado.md` | `tp_domain/**`, `ai/**`, `infrastructure/**`, `tests/domain/**`, `tests/ai/**`, `tests/report/**` | Código rescatado: **no se toca fuera de los pasos 8 y 9**. La suite mantiene 180 pruebas: si se retira una, se sustituye por otra. `tp_domain/` no importa Django ni `apps/`. `ai/` no importa Django: su configuración se inyecta. Una fuente nueva va al registro cerrado, con jurisdicción, localizador tipado y fecha de verificación |
| `.claude/rules/capa-web.md` | `apps/**`, `config/**`, `templates/**` | **Toda lectura de una fila con propietario pasa por `apps/comun/guardas.py`; ninguna vista escribe `Caso.objects` por su cuenta.** Un recurso ajeno responde **404, nunca 403**: un 403 confirmaría que el id existe. Las vistas solo hacen HTTP y delegan en `services.py`; ninguna vista importa `tp_domain.calculations` ni `ai.claude_client`. El formulario inválido responde **422**, no 200. El borrado es **suave** (`deleted_at`): ninguna vista llama a `.delete()` sobre un `Caso`. Ninguna plantilla calcula ni escribe una URL a mano: `{% url %}` siempre. Nada de `\|safe` sobre datos de entrada |
| `.claude/rules/gasto-y-ia.md` | `apps/ia/**`, `apps/analisis/services.py`, `apps/evaluacion/**` | `comprobar_cuota()` se llama **antes** de construir el cliente, nunca dentro. Los tokens **los reporta el proveedor**: nada de `count_tokens`, `tiktoken` ni contar palabras. `apps/ia/registro.py` es el único escritor de `LlamadaLLM`. Toda llamada lleva su `proposito` (`explicacion` o `evaluacion`), para que una pasada del arnés no consuma el tope de un usuario. La capa de IA **nunca** lanza hacia arriba: si falla, el caso se guarda sin explicación |
| `.claude/rules/estilo-visual.md` | `static/**`, `templates/**` | `app.css` no contiene ni un color literal: todo sale de `var(--tpip-*)`. `tokens.css` es **generado**: se edita `infrastructure/theme.py` y se regenera, nunca al revés. La paleta se amplía añadiendo claves, jamás renombrando: un renombrado rompe el informe y las 38 pruebas que lo cubren |

---

### 19.6 Configuración crítica para los gates e infraestructura local

Todo fichero de configuración que un bloque `Verify` de §9 necesita para poder ejecutarse se emite aquí
como **fichero real, con contenido completo**, bajo `blueprints/tpip/workspace/`, en la ruta que ocupa
en el proyecto. Nombrarlo en el árbol de §3 no lo emite.

En este proyecto son cuatro, y ninguno más:

| Fichero | Ruta en el proyecto | Qué `Verify` lo necesitan | Resolución / carga de entorno que lleva escrita | Exclusión de la ruta del bundle |
|---|---|---|---|---|
| `pyproject.toml` | raíz | Todos, del 1 al 27, y el gate entero de §20.1 | `[tool.pytest.ini_options] DJANGO_SETTINGS_MODULE = "config.settings.local"` — **es el mecanismo por el que pytest carga la configuración y, con ella, el `.env`**, porque `config/settings/base.py` es lo único que lo lee. `[tool.uv] package = false` — el proyecto no se instala; los paquetes de primer nivel se importan porque `manage.py` y pytest ponen la raíz en `sys.path` | **Tres líneas, una por herramienta:** `extend-exclude` de ruff con `"blueprints"`; `exclude` de mypy con `"^blueprints/"`; `norecursedirs` de pytest con `"blueprints"`. Sin ellas, ruff encuentra dos raíces de configuración en un árbol y pytest recoge las pruebas dos veces |
| `.gitignore` | raíz | Ninguno directamente; gobierna qué recoge el primer commit de §10 y qué ve el gate manual de §20.1 | Ninguna: no resuelve módulos y no lee entorno | `blueprints/` — **es una línea distinta y adicional** a las tres de arriba: aquella mantiene el bundle fuera de las herramientas, esta lo mantiene fuera del repositorio del producto |
| `.env.example` | raíz | Ninguno directamente; §10 lo copia a `.env`, que es lo que `config/settings/base.py` lee. Lleva **todas** las claves de la tabla de §10 con valor vacío o evidentemente falso: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`, `PRECIO_ENTRADA_EUR_POR_MTOK`, `PRECIO_SALIDA_EUR_POR_MTOK`, `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL` y `DJANGO_SUPERUSER_PASSWORD` | Es el **contenido** que carga el mecanismo, no el mecanismo | No aplica: no recorre el árbol |
| `.claude/settings.json` | `.claude/` | Ninguno lo lee; **es lo que permite que se ejecuten sin pedir permiso**, del 1 al 27 y en §20.1 | Ninguna | No aplica: no recorre el árbol |

**`pyproject.toml` ya está emitido** en `blueprints/tpip/workspace/pyproject.toml`, con las 102 líneas
que contienen las dependencias fijadas de §11 y la configuración de ruff, mypy y pytest descrita
arriba. Los otros tres se emiten con el resto del bundle.

**No se emite ningún fichero de aprovisionamiento de servicios, y esa ausencia es una decisión
comprobable, no un olvido:** ningún `Verify` de §9 necesita una base de datos, una caché, una cola ni
un almacén de objetos. SQLite es un fichero que crea el propio Django, y `pytest-django` fabrica y
destruye la base de datos de prueba por su cuenta. Por el mismo motivo no hay ninguna orden de
`docker` en `permissions.allow`: **nunca se pre-aprueba un comando para un fichero que este blueprint
no emite.**

No hay fichero de configuración de e2e (no hay e2e, §13), ni fichero de arranque de entorno para las
pruebas (ningún módulo de este proyecto lanza una excepción al importarse por falta de una variable:
§10 lo garantiza haciéndolas todas opcionales), ni configuración de alias de rutas (no hay alias).

#### Una convención de resolución se decide una vez y se concilia contra todos los cargadores

**La convención, enunciada una sola vez:** imports absolutos desde la raíz del proyecto
(`from tp_domain.models import Transaction`), sin alias, sin imports relativos entre paquetes de primer
nivel, y **con el proyecto sin instalar** (`[tool.uv] package = false`). Los paquetes de primer nivel
son exactamente los cinco que declara `known-first-party` en el `pyproject.toml` emitido: `apps`,
`config`, `tp_domain`, `ai`, `infrastructure`.

Eso obliga a que **algo** ponga la raíz del proyecto en `sys.path` en cada contexto, y cada contexto lo
hace por un mecanismo distinto:

| Contexto | Comando que lo ejercita | La convención tal como aparece ahí | Configuración y ajuste literal que la hace funcionar |
|---|---|---|---|
| Código de la aplicación | `uv run python manage.py check` (pasos 1–27) | `from apps.analisis.services import crear_caso` | `manage.py` — Python pone el directorio del script en `sys.path[0]`, y `manage.py` está en la raíz. Nada más que configurar |
| Ficheros de prueba | `uv run pytest tests/domain tests/ai tests/report` y `uv run pytest tests/web` | `from tp_domain.models import Transaction` | `pyproject.toml` — `testpaths = ["tests"]` y el modo de importación `prepend` por defecto: como `tests/`, `tests/domain/`, `tests/ai/`, `tests/report/` y `tests/web/` **tienen `__init__.py`**, pytest sube hasta el primer directorio sin `__init__.py` —la raíz— y **esa** es la que inserta. Por eso `tests/web/__init__.py` es obligatorio (paso 2) y no cosmético |
| Configuración de Django bajo pytest | `uv run pytest` | `config.settings.local` | `pyproject.toml` — `[tool.pytest.ini_options] DJANGO_SETTINGS_MODULE = "config.settings.local"`, resuelto contra la misma raíz que acaba de insertarse |
| Scripts sueltos | `uv run python -m scripts.build_tokens --check` (pasos 13 y 27) | `from infrastructure.theme import COLORS` | **`scripts/__init__.py` más la forma `-m`.** Este es el contexto que rompe: `python scripts/build_tokens.py` pondría `scripts/` en `sys.path[0]` en vez de la raíz, y `infrastructure` no se encontraría. Con `-m`, el intérprete pone el **directorio de trabajo** —la raíz— en `sys.path`, y el import resuelve. Está escrito aquí, en el paso 13 y en `.claude/rules/`, con el motivo, para que nadie "simplifique" el `-m` |
| Construcción de estáticos | `uv run python manage.py collectstatic --noinput` (paso 27) | Rutas de `STATICFILES_DIRS`, no imports | `config/settings/base.py` — `STATIC_ROOT = BASE_DIR / "staticfiles"`, con `BASE_DIR` derivado de la ubicación del propio fichero. La convención sobrevive porque no hay empaquetado que la reescriba |
| Lint y tipos | `uv run ruff check .` · `uv run mypy .` | Los mismos imports | `pyproject.toml` — `known-first-party` de isort para el orden; `ignore_missing_imports = true` de mypy, que evita exigir stubs de Django. Ambos con el bundle excluido |

**Ninguna celda dice "funciona por defecto" sin decir de qué resolutor es ese defecto.** El único
contexto que necesitaba un ajuste distinto del resto —los scripts— lo lleva escrito en el fichero que
le corresponde (`scripts/__init__.py`) y en la forma de invocación, no en una frase a tres secciones de
distancia.

#### Todo lo que lee una variable de entorno tiene un mecanismo de carga

**Un mecanismo, y solo uno, para todo el proyecto:** el `SettingsConfigDict(env_file=".env")` de
`pydantic-settings`, escrito dentro de `config/settings/base.py` (paso 2). Es la opción más duradera de
las tres posibles, porque se escribe una vez en un fichero que siempre se evalúa y no se puede olvidar
en un sitio de llamada.

| Herramienta que se invoca por su nombre | ¿Lee variables de entorno? | Mecanismo de carga |
|---|---|---|
| `manage.py <cualquier orden>` | Sí, a través de la configuración | `manage.py` fija `DJANGO_SETTINGS_MODULE=config.settings.local`; Django importa `config.settings.base`; **ahí** se lee `.env` |
| `pytest` | Sí, igual | `pyproject.toml` fija `DJANGO_SETTINGS_MODULE`; `pytest-django` importa la misma configuración; misma lectura de `.env` |
| `python -m scripts.build_tokens` | **No.** Solo importa `infrastructure.theme`, que es un diccionario de literales | Ninguno necesario, y se dice explícitamente para que nadie añada uno "por si acaso" |
| `ruff`, `mypy` | No | Ninguno necesario |
| `uv sync`, `uv python install` | No lee ninguna variable de este proyecto | Ninguno necesario |
| El cliente de Anthropic | Sí, `ANTHROPIC_API_KEY` y `ANTHROPIC_MODEL` | **Inyectados**, no descubiertos: `apps/analisis/services.py` los lee de la configuración de Django y se los pasa a `explain_analysis` (pasos 8 y 17). `ai/` no lee `.env` por su cuenta desde el paso 8, y desde ahí tampoco consulta el catálogo de modelos |

No hay ni un comando en §10, §9, §19.1 o §20.1 que invoque una herramienta que lea una variable de
entorno sin pasar por esa cadena. Esa es la razón de que ningún bloque `Verify` lleve una línea de
`$env:` delante, con la única excepción del paso 26, donde se genera una `DJANGO_SECRET_KEY` efímera
para auditar los ajustes de producción y se borra a continuación.

#### Conciliación de valores entre artefactos

| Valor compartido | Fuente única — el fichero que lo decide | Valor literal | Dónde más aparece | Comparado |
|---|---|---|---|---|
| Módulo de configuración | `pyproject.toml` — `[tool.pytest.ini_options] DJANGO_SETTINGS_MODULE` | `config.settings.local` | `manage.py` (línea `os.environ.setdefault`) · §3 árbol · §9 pasos 1, 2, 13 · §10 tabla de variables · §19.6 matriz de resolución | sí |
| Directorio de estáticos recopilados | `config/settings/base.py` — `STATIC_ROOT` | `staticfiles/` | §3 árbol · `.gitignore` (§19.6) · §9 paso 27 · §12 · §20.1 | sí |
| Fichero de base de datos | `config/settings/base.py` — `DATABASES["default"]["NAME"]` | `db.sqlite3` | §3 árbol · `.gitignore` · §2 · §12 | sí |
| CSS de tokens generado | `scripts/build_tokens.py` — ruta de salida | `static/css/tokens.css` | §3 árbol · §7 · §9 pasos 13 y 27 · §10 *Ficheros que deben quedar versionados* · `.claude/rules/estilo-visual.md` | sí |
| Ruta del bundle | Este bundle — su propia ubicación | `blueprints/` | `pyproject.toml` en tres sitios (`extend-exclude` de ruff, `exclude` de mypy como `^blueprints/`, `norecursedirs` de pytest) · `.gitignore` · §10 Bootstrap (`blueprints/tpip/workspace`) · §3 árbol | sí |
| Etiqueta de la aplicación de análisis | `apps/analisis/apps.py` — `label` | `analisis` | `INSTALLED_APPS` como `apps.analisis` · `app_name` de las rutas · `{% url 'analisis:...' %}` en las plantillas · §3 árbol | sí |
| Nombres de tabla | `Meta.db_table` de cada modelo (§4.0) | `usuarios` · `casos` · `fichas` · `unidades_estudio` · `casos_contrastados` · `llamadas_llm` · `casos_evaluacion` · `ejecuciones_evaluacion` | §4.3 índices · §16 métricas · el comando de copia y su fichero de recuentos (paso 24) · §20.1 | sí |
| Modelo de usuario | `config/settings/base.py` — `AUTH_USER_MODEL` | `cuentas.Usuario` | `apps/cuentas/models.py` · toda `ForeignKey(settings.AUTH_USER_MODEL, …)` de §4 · §9 paso 4 · §20.1 | sí |
| Directorio de copias | `apps/comun/management/commands/copia_seguridad.py` — ruta de salida | `copias/` | `.gitignore` (§10 Bootstrap) · §9 paso 24 · §20.1 | sí |
| Puerto del servidor de desarrollo | El valor por defecto de `manage.py runserver` | `8000` | §10 Bootstrap (comentario final) · §12 · §14 | sí |
| Paquetes de primer nivel | `pyproject.toml` — `known-first-party` | `apps`, `config`, `tp_domain`, `ai`, `infrastructure` | §3 árbol · §19.6 matriz de resolución | sí |

**El contrato que más cerca está de romperse es el primero**, y por eso se ejercita en el **paso 1**,
que es el primer paso en el que existen los dos lados: `manage.py` y `pyproject.toml` declaran el mismo
literal, y el `Verify` del paso 1 los compara los dos contra `config.settings.local` además de importar
el módulo para comprobar que resuelve de verdad. Un desacuerdo aquí —`config.settings` frente a
`config.settings.local`, que se leen igual de un vistazo— habría dejado a pytest cargando una
configuración distinta de la de `manage.py` durante toda la construcción.

#### Conciliación de artefactos byte a byte

| Artefacto byte a byte | Escrito por | Primer `diff` en | Reglas del blueprint que lo condicionan | Llamada que lo produce, sobre la versión fijada en §11 | Ambos confirmados |
|---|---|---|---|---|---|
| El literal `DATOS SINTÉTICOS` que el paso 14 busca en el PDF servido | **Nadie de este blueprint.** Procede del `disclaimer` de `TPIP_DATASET_V1` en `tp_domain/sources.py`, código rescatado leído en disco el 2026-08-15 | Paso 14 | §4 *Vocabulario del dominio* (`Source`: el registro es cerrado y su texto no se reescribe) · §20.2 riesgo 1 (el aviso es inamovible) · §9.1 fila 5 de paridad | `infrastructure.report.render_report_bytes(result)` sobre `reportlab` fijado, y su extracción con `pypdf`. **Ya se ejecuta hoy** en `tests/report/test_pdf_report.py::test_cover_discloses_the_synthetic_dataset`, que pasa: la comprobación del paso 3 vuelve a ejecutarla sobre la versión fijada antes de que el paso 14 dependa de ella | sí |
| `static/css/tokens.css` | `scripts/build_tokens.py` (paso 13) | Paso 13, y de nuevo en el 27 | §7 *Colores* — los 14 literales hexadecimales; §7 *Espaciado* — la escala de 8 valores | `python -m scripts.build_tokens`. **No es una predicción**: el fichero lo genera el propio script desde `infrastructure.theme.COLORS`, y el modo `--check` compara la salida del generador contra el disco. No hay ningún byte escrito a mano que pueda contradecir al productor | sí |

**Este blueprint no escribe ningún otro literal que algo vaya a comparar carácter a carácter.** No hay
ficheros dorados de salida esperada, ni instantáneas, ni fixtures con bytes predichos: todo lo que se
compara, o lo genera el propio productor (los tokens), o ya existe en disco y se ha leído (el aviso del
dataset). Es la razón de que ninguna fila de esta tabla dependa de recordar cómo formatea un mensaje
una versión concreta de una biblioteca.

---

## 20. Gate de aceptación, riesgos y registro de decisiones

### 20.1 Gate de aceptación global

El proyecto está **terminado** cuando cada comando de abajo sale con 0 sobre un clon limpio, y no
antes. Es el mismo conjunto que ejecuta CI y contra el que se mide cada uno de los 27 pasos de §9.

```powershell
$ErrorActionPreference = 'Stop'

uv sync --frozen
if ($LASTEXITCODE -ne 0) { throw 'el arbol de dependencias no coincide con uv.lock' }   # expect: exit 0

uv run ruff check .
if ($LASTEXITCODE -ne 0) { throw 'lint' }                    # expect: exit 0, cero errores y cero avisos
uv run ruff format --check .
if ($LASTEXITCODE -ne 0) { throw 'formato' }                 # expect: exit 0
uv run mypy .
if ($LASTEXITCODE -ne 0) { throw 'tipos' }                   # expect: exit 0

uv run python manage.py check
if ($LASTEXITCODE -ne 0) { throw 'comprobacion de Django' }  # expect: exit 0, cero incidencias
uv run python manage.py migrate --check
if ($LASTEXITCODE -ne 0) { throw 'la base de datos no esta al dia' }        # expect: exit 0
uv run python manage.py makemigrations --check --dry-run
if ($LASTEXITCODE -ne 0) { throw 'quedan cambios de modelo sin migrar' }    # expect: exit 0

# AUTH_USER_MODEL es el punto sin retorno del paso 4: se comprueba en cada pasada del gate.
uv run python -c "import os; os.environ['DJANGO_SETTINGS_MODULE']='config.settings.local'; import django; django.setup(); from django.conf import settings; assert settings.AUTH_USER_MODEL=='cuentas.Usuario', settings.AUTH_USER_MODEL; print('AUTH_USER_MODEL OK')"
if ($LASTEXITCODE -ne 0) { throw 'AUTH_USER_MODEL no es cuentas.Usuario' }  # expect: exit 0

# Los dos indices reconstruibles: el .md y el .json en disco son la fuente de verdad.
uv run python manage.py reindexar_corpus
if ($LASTEXITCODE -ne 0) { throw 'el reindexado del corpus falla' }         # expect: exit 0
uv run python manage.py reindexar_evaluacion
if ($LASTEXITCODE -ne 0) { throw 'el reindexado del conjunto dorado falla' }# expect: exit 0

uv run python -m scripts.build_tokens --check
if ($LASTEXITCODE -ne 0) { throw 'tokens.css desincronizado con theme.py' } # expect: exit 0

uv run pytest
if ($LASTEXITCODE -ne 0) { throw 'la suite completa falla' }               # expect: exit 0, 0 failed, 0 skipped

# La red de seguridad de la migracion, como comprobacion aparte y explicita.
uv run pytest tests/domain tests/ai tests/report -q
if ($LASTEXITCODE -ne 0) { throw 'la suite rescatada falla' }
$n = (uv run pytest tests/domain tests/ai tests/report --collect-only -q 2>&1 | Select-String -Pattern '^(\d+) tests collected').Matches[0].Groups[1].Value
if ([int]$n -ne 180) { throw "la suite rescatada tiene $n pruebas, se esperaban 180" }   # expect: 180

# El aislamiento por propietario: si esto no pasa, el producto no es publicable.
uv run pytest tests/web/test_aislamiento.py tests/web/test_guarda_unica.py -q
if ($LASTEXITCODE -ne 0) { throw 'el aislamiento por propietario falla' }  # expect: exit 0

# La puerta de regresion del arnes (paso 23). La linea base la fija el propio paso 23;
# si no existiese, este comando saldria con 2 y el gate no podria salir 0 nunca.
uv run python manage.py evaluar --contra-linea-base
if ($LASTEXITCODE -ne 0) { throw "la tasa de acierto ha bajado de la linea base (codigo $LASTEXITCODE)" }
# expect: exit 0 — 1 = regresion · 2 = no hay linea base

# La copia de seguridad, restaurada y COMPARADA POR RECUENTO DE FILAS (paso 24).
uv run python manage.py copia_seguridad
if ($LASTEXITCODE -ne 0) { throw 'la copia de seguridad falla' }           # expect: exit 0
$copia = Get-ChildItem 'copias' -Filter '*.sqlite3' | Sort-Object LastWriteTime | Select-Object -Last 1
$destino = Join-Path $env:TEMP ("tpip-gate-" + [guid]::NewGuid().ToString('N'))
uv run python manage.py restaurar_copia --copia $copia.FullName --destino $destino
if ($LASTEXITCODE -ne 0) { throw "la restauracion no coincide en recuentos (codigo $LASTEXITCODE)" }
# expect: exit 0 — 1 = discrepancia de recuentos · 2 = copia inexistente
Remove-Item -Recurse -Force $destino

# Se EJECUTA lo que se construye, no solo se construye.
uv run python manage.py collectstatic --noinput
if ($LASTEXITCODE -ne 0) { throw 'collectstatic falla' }                   # expect: exit 0
uv run python manage.py check --list-tags
if ($LASTEXITCODE -ne 0) { throw 'el punto de entrada no es ejecutable' }  # expect: exit 0

$env:DJANGO_SECRET_KEY = 'clave-solo-para-el-gate-no-usar'
uv run python manage.py check --deploy --settings=config.settings.production
if ($LASTEXITCODE -ne 0) { throw 'check --deploy senala problemas' }       # expect: exit 0
Remove-Item Env:\DJANGO_SECRET_KEY

# El gate de sincronia de tokens PUEDE fallar: se afirma el codigo 1 concreto.
Copy-Item 'static/css/tokens.css' 'static/css/tokens.css.bak'
Add-Content 'static/css/tokens.css' '/* alteracion deliberada */'
uv run python -m scripts.build_tokens --check
$codigo = $LASTEXITCODE
Move-Item 'static/css/tokens.css.bak' 'static/css/tokens.css' -Force
if ($codigo -ne 1) { throw "se esperaba codigo 1 con tokens.css alterado, obtenido $codigo" }
# 1 = desincronizado (la propiedad) · 2 = error de uso · 0 = la comprobacion no detecta nada
```

**Cada expectativa de arriba es una propiedad, no un recuento**, salvo una: el **180**, que es la
invariante de paridad de esta migración y está contado sobre el propio repositorio (89 + 53 + 38, el
2026-08-15). Aparece con el mismo valor en §1, §9 regla 10, §9 pasos 3, 8 y 9, §9.1, §13 y aquí.

**Cada línea sale con 0 en una construcción correcta**, y las dos cuyo resultado correcto es un fallo
—la alteración deliberada de `tokens.css` y la regresión del arnés— **afirman el código concreto**, no
"distinto de cero": un error de uso también saldría distinto de cero y esas comprobaciones pasarían en
vacío, y seguirían pasando después de romperse justo lo que vigilan.

Además, estos gates manuales, comprobados una vez antes de dar el proyecto por cerrado:

- [ ] Cada paso de §9 tiene su etiqueta de checkpoint en git: `git tag -l 'step-*'` lista **27**. El
      repositorio en el que viven esas etiquetas lo crea el bloque Bootstrap de §10, no un generador.
- [ ] Cada fichero de la tabla *Ficheros que deben quedar versionados* de §10 está presente en un clon
      limpio: `git ls-files --error-unmatch <ruta>` sale 0 para cada uno, **una ruta por invocación**,
      de modo que un fallo sea del fichero y no del comando. Y la comprobación complementaria de que
      no está ignorado, **también una ruta por invocación y afirmando el código**:
      `git check-ignore -q <ruta>; if ($LASTEXITCODE -ne 1) { throw "$ruta esta ignorada o el comando esta mal formado" }`
      — 1 significa "ninguna regla lo captura"; 128 significa error de uso, y así falla en vez de pasar
      en vacío. Nunca `git check-ignore -q <a> <b>`, que admite un solo argumento y sale 128.
- [ ] El fichero de ignorados estaba en su sitio antes del primer commit:
      `git log --diff-filter=A --format=%H -- .gitignore` lo sitúa en el commit de bootstrap de §10, no
      en el de un paso de §9. Una vez que git sigue una ruta, ninguna regla de ignorados la excluye ya.
- [ ] `.env`, `db.sqlite3`, `staticfiles/` y `copias/` **no** están versionados: `git ls-files` no
      devuelve nada para ninguno de los cuatro. Los tres últimos contienen datos, no código.
- [ ] Las dos filas de la tabla *Conciliación de artefactos byte a byte* de §19.6 leen
      `Ambos confirmados: sí`.
- [ ] El bloque Bootstrap de §10 se ha vuelto a ejecutar una vez sobre un árbol ya inicializado,
      **ha salido con 0**, y no ha cambiado nada que importe: `pyproject.toml` sigue listando las
      dependencias, `uv.lock` sigue en su sitio y el comando siguiente sigue encontrando sus binarios.
- [ ] **Todas** las filas de la tabla *Conciliación de valores entre artefactos* de §19.6 leen
      `Comparado: sí`, y los gates de lint, formato y tipos de arriba se han ejecutado **desde la raíz
      del proyecto con el bundle presente** en `blueprints/tpip/`.
- [ ] §9.1 aplica: las cinco filas de paridad demostradas, y la etiqueta `step-02-configuracion`
      —que aún contiene `ui/app.py`— sigue existiendo como vuelta atrás.
- [ ] Cada No-Goal de §1 sigue sin construirse. En particular: ni un fichero `.js`, ni `package.json`,
      ni conmutador de tema, ni auto-registro, ni servidor de correo saliente, ni API JSON.
- [ ] Cada variable de §10 está en el `.env` local y **ninguna** está en el repositorio.
- [ ] La cuenta de administrador inicial existe y **`is_staff` está restringido a quien debe tenerlo**:
      ninguna cuenta de uso normal lo lleva.
- [ ] Los seis flujos críticos de §13 pasan contra la aplicación arrancada con
      `uv run python manage.py runserver`, no solo contra el cliente de pruebas. **Incluido el segundo**:
      dos cuentas reales, y una pide el caso de la otra y recibe `404`.
- [ ] El aviso de privacidad se ve en el pie de toda página autenticada **y** junto al formulario de
      creación, y `/privacidad/` responde `200` (§8, paso 25).
- [ ] Pase completo con teclado del flujo entrar → formulario → resultado → descarga, y un pase con
      lector de pantalla sobre ese mismo flujo, prestando atención al `<title>` del gráfico del rango
      (§15).
- [ ] Pase al 200% de zoom y a 320 px de ancho, comprobando que la tabla del anexo de comparables y la
      del listado se desplazan dentro de su contenedor y no arrastran la página (§15).
- [ ] Una vuelta atrás ejecutada una vez, a propósito: `git reset --hard step-26-seguridad`, `uv sync`,
      y comprobar que la aplicación arranca. Después, volver adelante.

**Ningún aviso se tolera.** Un aviso tolerado se convierte en un aviso permanente, y el siguiente aviso
de verdad se esconde dentro.

### 20.2 Registro de riesgos

| Riesgo | Probabilidad | Impacto | Señal temprana | Mitigación |
|---|---|---|---|---|
| **1. Los comparables son sintéticos.** Ningún resultado de esta herramienta es un estudio de benchmarking utilizable ante una administración tributaria | **Certeza — es un hecho, no una probabilidad** | **Alto** | No hay señal: es la condición de partida | **ACEPTADO Y BLOQUEANTE.** El aviso es inamovible y está en tres sitios del documento: el `disclaimer` de `TPIP_DATASET_V1` en la portada, el pie de **todas** las páginas, y un `RiskFactor` de código `synthetic_data` dentro del propio análisis. El paso 14 comprueba que el literal `DATOS SINTÉTICOS` sigue en el PDF **que sirve la web**, y §9.1 lo hace criterio de aborto: si no se puede extraer, la construcción se detiene. Sustituir el dataset por uno comercial es un No-Goal de §1, con su disparador de revisión |
| **2. `reportlab` 5.0 sobre código escrito para 4.x.** El informe rescatado son 613 líneas contra una API de rama mayor anterior, y el informe de versiones señala un cambio de comportamiento | Media | Alto — sin informe no hay producto | Las 38 pruebas de `tests/report` fallando en el **paso 3**, que es lo primero que se ejecuta contra las versiones fijadas | La detección está colocada lo más pronto posible a propósito: el paso 3 corre la suite de informe completa antes de que ningún código nuevo dependa de ella. Si falla, §9.1 obliga a **parar y reportar**, no a adaptar el código rescatado a un comportamiento nuevo sin decisión. El repliegue es fijar `reportlab>=4,<5` en `pyproject.toml` y volver a ejecutar el paso 3 |
| **3. Pérdida de la base de datos.** Todo el sistema vive en un fichero SQLite en el equipo del usuario. Un disco que muere, un borrado accidental o una restauración de sistema se llevan todos los casos, todo el gasto registrado y toda la biblioteca de precedentes | Media | **Alto e irreversible** — no hay copia en ninguna otra parte | No la hay hasta que ya ha ocurrido, y ese es justamente el problema de esta clase de riesgo | **El paso 24, dentro de la v1 y no en el backlog.** `copia_seguridad` usa la API de copia en línea de SQLite —copiar el fichero con el proceso escribiendo produce un fichero corrupto sin avisar— y escribe junto a la copia un `.recuentos.json` con las filas de las ocho tablas. **El criterio es la restauración, no la existencia del fichero**: `restaurar_copia` restaura en un directorio limpio y **compara los recuentos de las ocho tablas**, saliendo 1 si alguno difiere. Una copia sin restaurar no es una copia, y por eso la restauración está en el gate de §20.1, no solo en el paso |
| **4. Dependencia de un proveedor externo para la capa de IA.** La API de Anthropic puede caer, cambiar de precio, retirar un modelo o rechazar la clave | Media | **Bajo, y eso es el diseño** | Subida de la tasa de degradación de §16 por encima del 25% | La capa entera está construida para poder fallar sin que se note: `explain_analysis` no lanza nunca, el informe se genera sin red y la sección declara su ausencia. Desde el paso 8 tampoco puede tumbarla una consulta de catálogo. CI corre **siempre sin clave**, así que la ruta de degradación se ejercita en cada push, que es la única forma de que un camino de fallo siga funcionando. El gasto está acotado por cuenta y comprobado **antes** de llamar (paso 16) |
| **5. Alcance jurisdiccional estrecho leído como cobertura.** Solo ES y DE están modeladas; cualquier otro país devuelve `NOT_MODELLED`, y un usuario podría leerlo como "sin regla estadística", que es precisamente la regla española | Media | Alto — es un error de interpretación jurídica, no de software | Una consulta con un tercer país cuyo veredicto se dé por bueno sin leer la etiqueta | El dominio ya se niega a suponer: `rule_for()` devuelve `NOT_MODELLED` y nunca la regla de otro país por analogía. La etiqueta humana es explícita —*"Jurisdicción no modelada en esta versión"*— y el paso 12 la imprime en la tarjeta de jurisdicción. La skill `anadir-jurisdiccion` de §19.4 impide ampliarlo por atajo: primero la ficha con fuente primaria, después el mapa |
| **6. Deriva entre pantalla e informe.** Dos renderizadores del mismo análisis, y en cuanto divergen dejan de parecer el mismo producto — que es el problema que ya existía antes de `theme.py` | Media | Medio | Un color en `app.css` que no salga de `theme.py`, o una etiqueta de enum distinta en pantalla y en PDF | Una sola fuente: `infrastructure/theme.py`, con la paleta, las etiquetas humanas y la geometría del rango normalizada. `tokens.css` se **genera** desde ahí y el gate `--check` falla si se desincroniza; el paso 27 comprueba además que ese gate **puede** fallar. `app.css` no puede contener ni un literal hexadecimal, y el paso 13 lo verifica |

### 20.3 Registro de decisiones

| # | Decisión | Alternativa rechazada | Por qué | Se revertiría si |
|---|---|---|---|---|
| 1 | Django como marco web | FastAPI + plantillas Jinja | Aquí no hay API, hay páginas. Y sobre todo: **el panel de administración es la razón de la elección**, no un extra. Da a un jurista no-ingeniero el alta y baja de cuentas, la curación de precedentes y la redacción de material de estudio sin escribir una línea de código. Con FastAPI habría que construir todo eso | El producto pasara a ser mayoritariamente una API para otro cliente |
| 2 | `uv` como gestor de paquetes e intérpretes | `pip` + `venv`, que es lo que había | Es lo único de la lista que resuelve, fija **e instala el propio Python 3.12** en una máquina que tiene 3.11.9 | `uv` dejara de mantenerse |
| **3** | **Modelo de usuario propio y `usuario_id` en toda tabla de usuario, desde la primera migración** | **El usuario por defecto de Django, o directamente ninguna cuenta** | **Esta decisión se tomó, se revirtió y se volvió a tomar, así que conviene dejar escrito por qué gana.** El argumento **no es de seguridad**: es que *"de quién es esta fila"* tiene que tener respuesta desde la primera fila que se escribe. Cambiar `AUTH_USER_MODEL` o añadir el propietario después de migrar **no es una migración, es reescribir la capa de datos entera** —toda clave foránea al usuario apunta a una tabla que deja de existir—, y Django lo documenta como trabajo de varios días con riesgo de pérdida. Una columna hoy cuesta una línea. Y el requisito de partida era literal: *"cuentas que yo puedo dar de alta o baja cuando quiera"* | Nunca por comodidad. Solo si el producto dejara de tener filas con dueño, que es tanto como decir que dejara de ser este producto |
| **3b** | **La lectura contraria que se consideró y no gana** | *"Es local, hay un solo usuario y escucha en `127.0.0.1`: el marco de autenticación deja tablas que nadie ejercita"* | Es **cierto** y está recogido: en un despliegue local monousuario, sesiones y roles no protegen de nadie. Pero es un argumento sobre **la superficie de red**, no sobre **el modelo de datos**, y las dos cosas conviven: el esquema es multiusuario desde el día uno **y** el despliegue de la v1 sigue siendo local, con `ALLOWED_HOSTS = ["127.0.0.1", "localhost"]` y CSRF activo (§12, §14). Aplicar el argumento de red al esquema es lo que produjo el recorte que hubo que revertir | La aplicación se publicara en una red: entonces el argumento de red deja de valer también, y refuerza la decisión 3 en vez de contradecirla |
| 4 | SQLite, con las ocho tablas de §4 | PostgreSQL | Un proceso, cero operaciones, un fichero. El coste de esta elección es el riesgo 3, y se paga con el paso 24, no ignorándolo | Hubiera más de un proceso escribiendo a la vez |
| 5 | El dominio sigue en pydantic; el ORM guarda su volcado JSON en `payload` | Traducir `tp_domain` a modelos de Django | Traducirlo sería mantener dos veces el mismo vocabulario y tirar las 89 pruebas de dominio. `AnalysisResult` se basta solo por diseño: trocearlo en tablas lo haría depender de que las cinco fuentes sigan existiendo con el mismo texto dentro de dos años | Hiciera falta consultar por campos de dentro del análisis con frecuencia y a volumen |
| 6 | **404 y no 403** para un recurso ajeno | 403, que es lo que "significa" no autorizado | Un 403 sobre un identificador ajeno **confirma que ese identificador existe**, y con eso se enumera la base de datos de otro usuario sin ver una sola fila. El 404 no distingue "no existe" de "no es tuyo" | Nunca en una superficie multiusuario. Solo tendría sentido en una API interna donde el enumerado ya fuera irrelevante |
| 7 | Una **guarda única con nombre**, no una condición repetida en cada vista | `filter(usuario=request.user)` escrito en cada vista | Una comprobación duplicada en siete sitios es una comprobación que un día falta en el octavo, y ese octavo **no da error: devuelve los datos de otro**. Al ser una función con nombre, se puede buscar quién la llama y quién no, y esa búsqueda es un criterio de aceptación del paso 7 | Nunca. Es más barata que la alternativa en todos los ejes |
| 8 | `Ficha` como **índice reconstruible**, con el `.md` como fuente de verdad | La ficha como contenido editable en la base de datos | El usuario escribe en Obsidian y quiere seguir haciéndolo; el corpus se revisa en `git` como el código. Por eso el panel muestra `Ficha` en solo lectura: una edición allí se perdería en el siguiente reindexado, y una tabla que miente es peor que una tabla que no existe | El corpus dejara de vivir en ficheros |
| 9 | `UnidadEstudio` **separada** de `Ficha` | Una sola tabla con una bandera `es_citable` | Decisión textual del usuario: *"el estudio que no entre dentro de las fichas, deben de ser contenidos independientes"*. Y es la correcta: la ficha es fuente citable **con rango normativo**, la unidad es material de aprendizaje. Con una bandera, tarde o temprano un informe cita material de estudio como si fuera Derecho | Nunca mientras el producto emita documentos con valor jurídico |
| 10 | El tope de gasto se construye **antes** que la capa de IA (paso 16 antes del 17) | Añadir el tope después, cuando ya funcione la llamada | Un freno que se instala después de rodar es un freno que nunca se ha probado en el camino que importa. La prueba del paso 16 usa un doble que **lanza si alguien lo llama**: solo pasa si la cuota corta antes | Nunca. Invertir el orden solo ahorra tiempo el primer día y lo cobra el resto |
| 11 | El uso de tokens **lo reporta el proveedor**; nunca se estima | Contar tokens localmente con un tokenizador | Un recuento propio diverge del que factura el proveedor, y entonces el tope vigila un número que no es el que se paga | El proveedor dejara de reportar uso, en cuyo caso el tope pasaría a ser por número de llamadas, no por coste |
| 12 | El identificador de modelo y sus tarifas son configuración, y este blueprint **no fija el id** | Fijar un id concreto en el código o en el documento | Fijarlo aquí reintroduciría el defecto que el paso 8 corrige: un valor que envejece dentro de un artefacto que nadie vuelve a mirar. Resolverlo en ejecución rompe la reproducibilidad, que es la premisa del sistema | Anthropic ofreciera un alias estable con garantías de comportamiento entre versiones |
| 13 | El formulario inválido responde **422**, no el 200 habitual de Django | Seguir la convención de Django | Un estado distinto convierte "el formulario ha rechazado la entrada" en algo que una máquina puede decidir, y §9 lo usa como criterio de aceptación | Un cliente externo esperara el comportamiento estándar |
| 14 | Sesión en **cookie `HttpOnly`** respaldada en base de datos | Un token en `localStorage`, o una cookie firmada sin estado | Un token en `localStorage` lo lee cualquier script inyectado; una cookie firmada sin estado no se puede invalidar desde el servidor, y al dar de baja una cuenta su sesión tiene que dejar de valer **inmediatamente** | El sistema necesitara autenticar clientes que no son navegadores |
| 15 | Sin E2E de navegador | Playwright | Runtime de Node, binarios de navegador y una fuente de intermitencia, para cubrir un JavaScript que no existe | La aplicación incorporara JavaScript con estado propio |
| 16 | Los scripts se invocan con `-m` y `scripts/` es un paquete | `python scripts/build_tokens.py` | La forma directa pone `scripts/` en `sys.path[0]` y no encuentra `infrastructure`. Es el único punto del proyecto donde la convención de imports necesitaba un ajuste, y está escrito donde se rompe | El proyecto pasara a instalarse como paquete |
| 17 | La suite rescatada mantiene exactamente **180** pruebas durante toda la migración | Dejar que el recuento crezca con las pruebas nuevas | Convierte la red de seguridad en una **invariante comprobable**: si el número cambia, alguien ha retirado cobertura del motor. Las pruebas nuevas van a `tests/web/` | El motor se ampliara de verdad, que sería un cambio de alcance, no una migración |
| 18 | Sin rastreo de errores externo (Sentry) | Sentry o equivalente | Una cuenta, una clave, una dependencia y un canal por el que se pueden escapar datos, para avisar a la misma persona que ya está mirando la consola | La aplicación se desplegara para alguien que no sea el autor |
| 19 | **Nueve tareas exceden el tope de tamaño de `tasks-schema.md` (5 ficheros · 6 criterios) y no se dividen** | Partirlas en ~37 pasos para cumplir la regla al pie de la letra | La regla existe porque la tasa de acierto de un agente cae de forma no lineal con la longitud de la tarea. Seis de las nueve se pasan **por un solo fichero**, y el caso extremo, el paso 1, toca seis ficheros que **genera un único comando** (`django-admin startproject`): dividirlo no acorta ninguna tarea, crea dos que no se pueden separar. Las tres restantes —pasos 12, 19 y 22, con 10, 8 y 9 ficheros— son mayoritariamente **plantillas HTML**, no lógica: el riesgo de que un agente se pierda a mitad es muchísimo menor que en una tarea de igual tamaño llena de decisiones. Y el coste del remedio es real y medido: renumerar los pasos introdujo defectos nuevos en seis de las siete auditorías de este blueprint, siempre en secciones distintas a las corregidas. | Si al construir una de esas tres tareas se atasca o falla parcialmente, se parte **en ese momento**, con el fallo concreto delante en vez de una estimación a priori. Su etiqueta de checkpoint es el punto de retorno. |

### 20.4 Qué construir a continuación

Los cuatro primeros salen de la tabla de No-Goals de §1, con su disparador:

1. **Servicios intragrupo (`MANAGEMENT_FEE`) con su propia rama de cálculo.** Es el tipo de operación
   que más se pide después del canon, y ya está bloqueado en el dominio esperando que exista una lógica
   con sentido económico —hoy, compararlo contra el margen operativo del dataset clasificaba como riesgo
   alto un 5%, que es el safe harbour de la OCDE para servicios de bajo valor añadido—.
   *Disparador: que ese tipo tenga su propia rama de cálculo y sus propios comparables.*
2. **Una tercera jurisdicción.** El procedimiento ya está escrito y automatizado en la skill
   `anadir-jurisdiccion`: ficha con fuente primaria, entrada en el registro cerrado, mapa de reglas y
   pruebas. *Disparador: que exista la ficha de investigación, verificada contra su texto primario.*
3. **Comparables reales.** Es lo único que convertiría la salida de esta herramienta en algo utilizable
   ante una administración, y por tanto lo único que desactivaría el riesgo 1.
   *Disparador: licencia contratada de una base comercial.*
4. **Incorporar el código rescatado al lint y a los tipos.** Hoy `tp_domain/`, `ai/` e `infrastructure/`
   están excluidos en `pyproject.toml`, y con razón: lintarlos durante la migración produciría fallos
   que no corresponden a ningún paso de construcción. Una vez estabilizada, se incorporan de uno en uno.
   *Disparador: que el gate de §20.1 lleve un mes en verde sin cambios en el motor.*
5. **Política de retención y purga definitiva.** La v1 ya lista, busca y borra en suave los casos
   (paso 15), pero un caso borrado en suave se queda en la tabla `casos` para siempre y `llamadas_llm`
   crece con cada análisis. Falta decidir cuánto tiempo se conserva un caso borrado antes de purgarlo
   de verdad, y un comando que lo haga respetando las claves foráneas `PROTECT` de §4.2.
   *Disparador: el primer dato personal escrito por descuido en una descripción, o que el fichero
   SQLite pase de un tamaño que incomode a la copia de seguridad del paso 24.*
6. **Recuperación de contraseña sin administrador.** Hoy la restablece una persona desde el panel
   (§8), lo que funciona mientras esa persona esté disponible. *Disparador: que haya que dar de alta a
   alguien a quien no se le puede entregar la contraseña en persona.*

---

*Fin del blueprint. El orden de construcción es §9. Se para cuando §20.1 está en verde.*
