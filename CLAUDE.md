# TPIP — Transfer Pricing Intelligence Platform

Contrasta el tipo de un canon intragrupo contra un rango de plena competencia y dice, por cada
jurisdicción implicada, qué le pasa a ese tipo según el Derecho de esa jurisdicción. Lo usa un asesor
de precios de transferencia, en su equipo.

<!-- El usuario es JURISTA, no ingeniero. Escribe los mensajes de error, los commits y las
     explicaciones para alguien que entiende de Derecho tributario y no de Django. "Migración" y
     "queryset" no significan nada para él; "el canon queda fuera del rango intercuartílico" sí. -->

## Comandos

| Tarea | Comando |
|---|---|
| Instalar | `uv sync` |
| Servidor de desarrollo | `uv run python manage.py runserver` — http://127.0.0.1:8000 |
| Comprobar el proyecto | `uv run python manage.py check` |
| Tipos | `uv run mypy .` |
| Lint · formato | `uv run ruff check .` · `uv run ruff format --check .` |
| Pruebas | `uv run pytest` · un fichero: `uv run pytest tests/web/test_forms.py` |
| **Red de seguridad** | `uv run pytest tests/domain tests/ai tests/report` |
| Migraciones | `uv run python manage.py makemigrations <app>` · `uv run python manage.py migrate` |
| Estáticos | `uv run python manage.py collectstatic --noinput` |
| Tokens de diseño | `uv run python -m scripts.build_tokens` · comprobar: `--check` |
| Reindexar corpus | `uv run python manage.py reindexar_corpus` |
| Reindexar evaluación | `uv run python manage.py reindexar_evaluacion` |
| Arnés de evaluación | `uv run python manage.py evaluar --contra-linea-base` |
| Copia de seguridad | `uv run python manage.py copia_seguridad` |
| Restaurar y verificar | `uv run python manage.py restaurar_copia --copia <ruta> --destino <dir>` |

**Gate:** `uv run ruff check . && uv run mypy . && uv run pytest` pasa antes de dar por hecha
cualquier tarea. El gate completo está en `blueprint.md` §20.1.

Python y las dependencias están fijados en `pyproject.toml` y resueltos en `uv.lock`. **Léelos, nunca
adivines una versión.**

## Pila

Django 5.2 · Python 3.12 (`uv`) · plantillas de Django · CSS plano con variables generadas · SQLite ·
ORM de Django para la persistencia y pydantic para el dominio · `django.contrib.auth` con modelo de
usuario propio · WhiteNoise · ejecución local.

## Arquitectura

**Camino de una petición.** Navegador → `config/urls.py` → `apps/comun/middleware.py`
(`ExigirAutenticacion`: exige sesión en todo salvo `/entrar/`, estáticos y páginas de error) →
`apps/analisis/views.py` → `apps/analisis/forms.py` (construye un `tp_domain.models.Transaction`) →
`apps/analisis/services.py` → `tp_domain/calculations/arm_length_range.py` → `apps/ia/cuota.py`
(comprueba el tope **antes** de llamar) → `ai/claude_client.py` → fila en `casos` → `302` al detalle.
El PDF sale de `infrastructure/report/pdf_report.py`, rehidratando el `payload` guardado.

**Fronteras.** Cruzar una de estas en el sentido equivocado rompe el proyecto:

| Capa | Puede importar de | Nunca debe |
|---|---|---|
| `tp_domain/**` | nada del proyecto | Importar Django, `apps/`, `ai/` o `infrastructure/` |
| `ai/**` | `tp_domain` | **Importar Django.** Su configuración se le inyecta desde fuera |
| `infrastructure/**` | `tp_domain` | Importar `apps/` o Django |
| `apps/*/views.py` | `services`, `forms`, `comun` | **Importar `tp_domain.calculations` o `ai.claude_client`** |
| `apps/analisis/services.py` | todo lo anterior | Contener nada de HTTP |
| `apps/**` | `apps/comun` | Consultar `Caso.objects` fuera de `apps/comun/` |

**Dónde vive cada cosa.**

| Asunto | Fuente única de verdad |
|---|---|
| Vocabulario del dominio | `tp_domain/models.py` — pydantic. No se traduce a modelos de Django |
| Fuentes citables | `tp_domain/sources.py` — registro **cerrado** de 5 entradas |
| Reglas por jurisdicción | `tp_domain/rules/statistical_rules.py` — crece ficha a ficha, nunca por analogía |
| Configuración y `.env` | `config/settings/base.py` — **el único punto que lee `.env`** |
| Lectura de una fila con dueño | `apps/comun/guardas.py` — `caso_del_usuario()`, y nada más |
| Paleta y etiquetas | `infrastructure/theme.py` → genera `static/css/tokens.css` |
| Corpus jurídico | Los `.md` de `documentation/tax-research/`. La tabla `Ficha` es un índice reconstruible |
| Conjunto dorado | `evaluacion/casos/*.json`. `CasoEvaluacion` es su índice |
| SDK de Anthropic | `ai/claude_client.py` — **el único fichero que lo importa** |

## Reglas de código

1. **El motor calcula; el modelo explica, fundamenta y puede sugerir, pero nunca decide y nunca
   escribe un número.** Cuando se llama al modelo, el `AnalysisResult` ya está calculado entero.
2. **La suite rescatada mantiene exactamente 180 pruebas.** `tests/domain` 89 + `tests/ai` 53 +
   `tests/report` 38. Si retiras una, la sustituyes por otra. Las pruebas nuevas van a `tests/web/`.
3. **Toda lectura de una fila con propietario pasa por `apps/comun/guardas.py`.** Un recurso ajeno
   responde **404, nunca 403**: un 403 confirmaría que el id existe.
4. **Los scripts se invocan con `-m`**: `uv run python -m scripts.build_tokens`. La forma directa
   pone `scripts/` en `sys.path[0]` y no encuentra `infrastructure`.
5. **El borrado es suave.** Se pone `deleted_at`; nunca `.delete()` sobre un `Caso`. Dar de baja una
   cuenta es `is_active = False`: un `DELETE` choca con los `PROTECT` y debe chocar.
6. **Un formulario inválido responde 422**, no el 200 habitual de Django.
7. **Ninguna plantilla calcula ni escribe una URL a mano.** `{% url %}` siempre. Nada de `|safe`
   sobre datos de entrada.
8. **`static/css/app.css` no contiene ni un color literal.** Todo sale de `var(--tpip-*)`.
   `tokens.css` se genera: se edita `theme.py` y se regenera, nunca al revés.
9. **Los tokens del modelo los reporta el proveedor.** Nada de `tiktoken` ni de contar palabras: un
   recuento propio diverge del que se factura, y entonces el tope vigila un número que no se paga.
10. **Ninguna dependencia nueva sin una razón en el mensaje del commit.** Mira antes en la biblioteca
    estándar y en lo que ya está instalado.

## Sistema de diseño

Los tokens se definen una vez en `infrastructure/theme.py` y se generan a `static/css/tokens.css`.

| Papel | Valor | Se usa para |
|---|---|---|
| Tinta | `#1A1A1A` | Texto principal |
| Atenuado | `#5A5A5A` | Texto secundario, metadatos |
| Fondo | `#FFFFFF` | Fondo de página |
| Superficie | `#F7F8FA` | Tarjetas y paneles |
| Superficie hundida | `#EBEEF3` | Cabeceras de tabla |
| Filete | `#C8C8C8` | Separadores |
| Borde de control | `#767676` | Inputs y selects |
| Foco | `#1F4E79` | Anillo de foco y enlaces |
| Defendible | `#2E6B4F` | Veredicto favorable |
| Moderado | `#8A6D1F` | Veredicto intermedio |
| Riesgo alto | `#8C2F2F` | Veredicto desfavorable, errores |

- **Tipografía:** `-apple-system, "Segoe UI", Roboto, system-ui, sans-serif`. Sin fuentes web.
- **Escala:** 0,875 / 1 / 1,0625 / 1,375 / 2 rem.
- **Espaciado:** base 4px — 4, 8, 12, 16, 24, 32, 48, 64. Nada de valores arbitrarios.
- **Radio:** 4px en controles, 8px en tarjetas, 0 en tablas.
- **Elevación:** plana. Solo bordes de 1px.
- **Movimiento:** 120ms `ease-out`, dentro de `prefers-reduced-motion: no-preference`.
- **Disposición:** ancho máximo 72rem; cortes en 40rem y 64rem. Sin modo oscuro.

## Entorno

| Variable | Obligatoria | La usa | De dónde sale |
|---|---|---|---|
| `DJANGO_SECRET_KEY` | Solo en producción | `config/settings/production.py` | `secrets.token_urlsafe(64)` |
| `DJANGO_DEBUG` | No | `config/settings/base.py` | `true` en local |
| `DJANGO_ALLOWED_HOSTS` | Solo en producción | `config/settings/base.py` | `127.0.0.1,localhost` |
| `ANTHROPIC_API_KEY` | No | `apps/analisis/services.py` | Consola de Anthropic |
| `ANTHROPIC_MODEL` | No | `apps/analisis/services.py` | Se elige a mano; sin ella la IA se desactiva |
| `PRECIO_ENTRADA_EUR_POR_MTOK` | No | `apps/ia/cuota.py` | Tarifa publicada, en euros |
| `PRECIO_SALIDA_EUR_POR_MTOK` | No | `apps/ia/cuota.py` | Tarifa publicada, en euros |
| `DJANGO_SUPERUSER_*` | Solo para el alta inicial | `createsuperuser --noinput` | Se eligen a mano |

`.env.example` se versiona y se mantiene al día. Ningún `.env` con valores reales entra en el
repositorio. **Ninguna variable es obligatoria en desarrollo**, a propósito.

## Reglas diferidas

Léelas antes de editar su área:

| Fichero | Se aplica a |
|---|---|
| `.claude/rules/dominio-rescatado.md` | `tp_domain/**`, `ai/**`, `infrastructure/**`, `tests/{domain,ai,report}/**` |
| `.claude/rules/capa-web.md` | `apps/**`, `config/**`, `templates/**` |
| `.claude/rules/estilo-visual.md` | `static/**`, `templates/**` |
| `.claude/rules/gasto-y-ia.md` | `apps/ia/**`, `apps/analisis/services.py`, `apps/evaluacion/**` |

Orden de construcción: `blueprints/tpip/tasks.json` y `blueprints/tpip/epics/`. No lo repitas aquí.

## Innegociable

1. **Los comparables son sintéticos.** El aviso `DATOS SINTÉTICOS` no se quita del PDF, ni de la
   portada, ni del pie de página. Ningún resultado sirve ante una administración tributaria.
2. **El modelo nunca escribe un número ni cita una fuente que el motor no emitiera.** Si lo intenta,
   `AnalysisResult` no se construye. La gobernanza está en el modelo de datos, no en el prompt.
3. **Nunca se toca `tp_domain/`, `ai/schemas.py`, `ai/validators.py` ni `infrastructure/report/`.**
4. **El tope de gasto se comprueba antes de construir el cliente, jamás dentro.**
5. **Una jurisdicción sin ficha de investigación se queda en `NOT_MODELLED`.** Nunca se le asigna la
   regla de otro país por analogía: eso es inventar Derecho comparado.
6. Nunca se versionan secretos, `.env`, `db.sqlite3`, `copias/` ni `staticfiles/`.
7. Nunca se edita a mano una migración generada, ni `static/css/tokens.css`.
8. Nunca se da una tarea por hecha con un comando del gate en rojo.
