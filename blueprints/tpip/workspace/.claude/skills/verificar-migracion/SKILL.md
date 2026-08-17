---
name: verificar-migracion
description: Ejecutar el gate completo antes de dar un paso por hecho o de hacer commit — "¿sigue todo bien?", "antes de commitear", "comprueba el paso", "¿puedo cerrar la tarea?", "run the gate". Termina siempre por la red de seguridad de 180 pruebas rescatadas, que es la evidencia de paridad de esta migración.
---

# Verificar la migración

## Cuándo usarla

- Antes de marcar una tarea como `done` en `tasks.json`.
- Antes de cualquier commit y de cualquier etiqueta de checkpoint.
- «¿Sigue todo bien?», «¿he roto algo?», «¿puedo cerrar esto?».
- Después de tocar cualquier cosa bajo `tp_domain/`, `ai/` o `infrastructure/`.

## Por qué existe

Esto es una **migración**, no un proyecto nuevo. La forma en que una migración falla es distinta: lo
nuevo funciona, lo viejo hacía algo que nadie había escrito, y la diferencia la descubre el usuario.

Las **180 pruebas rescatadas** son la evidencia de paridad: pasaban antes de tocar nada y tienen que
seguir pasando en cada uno de los pasos. Por eso el gate **termina** por ellas y no empieza: es lo
último que se mira y lo que decide.

## Pasos

Ejecuta en este orden, desde la raíz del proyecto. Si algo falla, para ahí: no sigas hacia abajo.

1. **Formato y lint** — `uv run ruff check .` y `uv run ruff format --check .`
2. **Tipos** — `uv run mypy .`
3. **Django** — `uv run python manage.py check`, más `migrate --check` y
   `makemigrations --check --dry-run`
4. **Sincronía de tokens** — `uv run python -m scripts.build_tokens --check`
5. **Suite completa** — `uv run pytest`
6. **Aislamiento por propietario** — `uv run pytest tests/web/test_aislamiento.py tests/web/test_guarda_unica.py`
7. **La red de seguridad** — `uv run pytest tests/domain tests/ai tests/report`, y **el recuento tiene
   que seguir siendo 180**

## Verify

```powershell
uv run ruff check .; if ($LASTEXITCODE -ne 0) { throw 'lint' }
uv run ruff format --check .; if ($LASTEXITCODE -ne 0) { throw 'formato' }
uv run mypy .; if ($LASTEXITCODE -ne 0) { throw 'tipos' }
uv run python manage.py check; if ($LASTEXITCODE -ne 0) { throw 'comprobacion de Django' }
uv run python manage.py migrate --check; if ($LASTEXITCODE -ne 0) { throw 'la base de datos no esta al dia' }
uv run python manage.py makemigrations --check --dry-run; if ($LASTEXITCODE -ne 0) { throw 'quedan cambios de modelo sin migrar' }
uv run python -m scripts.build_tokens --check; if ($LASTEXITCODE -ne 0) { throw 'tokens desincronizados' }
uv run pytest; if ($LASTEXITCODE -ne 0) { throw 'la suite completa falla' }
uv run pytest tests/web/test_aislamiento.py tests/web/test_guarda_unica.py -q; if ($LASTEXITCODE -ne 0) { throw 'el aislamiento por propietario falla' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
$n = (uv run pytest tests/domain tests/ai tests/report --collect-only -q 2>&1 | Select-String -Pattern '^(\d+) tests collected').Matches[0].Groups[1].Value; if ([int]$n -ne 180) { throw "la suite rescatada tiene $n pruebas, se esperaban 180" }
```

## No hagas

- **No marques una tarea como hecha con un comando del gate en rojo.**
- **No edites un comando de verificación para que pase.** Un `verify` que falla nunca es motivo para
  cambiar el `verify`.
- **No ejecutes esto desde `blueprints/tpip/`.** El gate corre desde la **raíz del proyecto**; dentro
  del bundle falla por motivos que no tienen nada que ver con el código.
- **No des por buena una suite rescatada con un recuento distinto de 180.** Si baja, se ha retirado
  cobertura del motor; si sube, se ha añadido una prueba nueva en el sitio equivocado — van a
  `tests/web/`.
