# TPIP — instrucciones para agentes

Contrasta el tipo de un canon intragrupo contra un rango de plena competencia y dice, por cada
jurisdicción implicada, qué le pasa a ese tipo según el Derecho de esa jurisdicción. Django 5.2 sobre
Python 3.12, gestionado con `uv`. El usuario es **jurista, no ingeniero**: escríbele para alguien que
entiende de Derecho tributario y no de Django.

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
| Tokens de diseño | `uv run python -m scripts.build_tokens --check` |
| Copia de seguridad | `uv run python manage.py copia_seguridad` |

**Gate:** `uv run ruff check . && uv run mypy . && uv run pytest` pasa antes de dar por hecha
cualquier tarea.

## Innegociable

1. **El motor calcula; el modelo explica, fundamenta y puede sugerir, pero nunca decide y nunca
   escribe un número.**
2. **Los comparables son sintéticos.** El aviso `DATOS SINTÉTICOS` no se quita del PDF. Ningún
   resultado sirve ante una administración tributaria.
3. **La suite rescatada mantiene exactamente 180 pruebas** (`tests/domain` 89 + `tests/ai` 53 +
   `tests/report` 38). Las pruebas nuevas van a `tests/web/`.
4. **Nunca se toca `tp_domain/`, `ai/schemas.py`, `ai/validators.py` ni `infrastructure/report/`.**
5. **Toda lectura de una fila con dueño pasa por `apps/comun/guardas.py`**, y un recurso ajeno
   responde **404, nunca 403**.
6. **Los scripts se invocan con `-m`**: `uv run python -m scripts.build_tokens`.
7. **El tope de gasto se comprueba antes de construir el cliente de Anthropic, jamás dentro.**
8. Nunca se versionan secretos, `.env`, `db.sqlite3`, `copias/` ni `staticfiles/`. Nunca se da una
   tarea por hecha con un comando del gate en rojo.

Arquitectura completa, fronteras entre capas, tokens de diseño y variables de entorno: **`CLAUDE.md`,
en este mismo directorio.** Orden de construcción: `blueprints/tpip/tasks.json` y
`blueprints/tpip/epics/`.
