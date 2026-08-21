# Transfer Pricing Intelligence Platform (TPIP)

![Gate](https://github.com/danirubio2323-commits/transfer-pricing-intelligence-platform/actions/workflows/ci.yml/badge.svg)

Contrasta el tipo de un canon intragrupo contra un rango de plena competencia y dice, por cada
jurisdicción implicada, qué le pasa a ese tipo según el Derecho de esa jurisdicción.

> **Los comparables son sintéticos.** El aviso `DATOS SINTÉTICOS` aparece en la portada, en el cuerpo
> y en el pie de cada informe, y no se quita. Ningún resultado de esta herramienta sirve ante una
> administración tributaria.

## Puesta en marcha

Python y las dependencias están fijados en `pyproject.toml` y resueltos en `uv.lock`. `uv` los
provisiona; no hace falta instalar Python a mano ni crear el entorno virtual.

```bash
uv sync
```

```bash
uv run python manage.py migrate
```

```bash
uv run python manage.py runserver
```

La aplicación queda en http://127.0.0.1:8000. **Escucha solo en la interfaz local**: la v1 no se
despliega en abierto, a propósito.

### La primera cuenta

No hay auto-registro. Las cuentas las da de alta quien administra, y hasta que exista una la
aplicación no deja pasar de la pantalla de acceso.

```bash
uv run python manage.py createsuperuser
```

Sin interacción, tomando los valores de `.env` (`DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`
y `DJANGO_SUPERUSER_PASSWORD`):

```bash
uv run python manage.py createsuperuser --noinput
```

`is_staff` se reserva a quien administra. Una cuenta con ese permiso ve los casos de todos los
usuarios desde el panel, y por eso el aviso de privacidad lo dice sin eufemismos en el pie de toda
página y junto al formulario de creación.

### Los dos índices reconstruibles

El corpus jurídico vive en los `.md` de `documentation/tax-research/` y el conjunto dorado en los
`.json` de `evaluacion/casos/`. Las tablas `Ficha` y `CasoEvaluacion` son **índices**: se tiran y se
reconstruyen desde el disco, que es la fuente de verdad.

```bash
uv run python manage.py reindexar_corpus
```

```bash
uv run python manage.py reindexar_evaluacion
```

### Copia de seguridad

Usa la API de copia en línea de SQLite, no un `cp`: copiar el fichero mientras el proceso escribe
produce algo corrupto sin avisar. Junto a la copia se escribe un `.recuentos.json` con las filas de
cada una de las ocho tablas.

```bash
uv run python manage.py copia_seguridad
```

Una copia sin restaurar no es una copia. La restauración compara los recuentos y sale con `1` si
alguna tabla no coincide, con `2` si no hay nada contra lo que comparar:

```bash
uv run python manage.py restaurar_copia --copia copias/tpip-AAAAMMDD-HHMMSS.sqlite3 --destino /tmp/verificacion
```

### Antes de dar nada por hecho

```bash
uv run ruff check . && uv run mypy . && uv run pytest
```

El gate completo está en el apartado 20.1 de `blueprints/tpip/blueprint.md`, y CI ejecuta el
mismo conjunto.

## El informe

Cada análisis produce un PDF: portada con la declaración del conjunto de datos, resumen ejecutivo,
gráfico del rango, fundamento jurídico por jurisdicción y el anexo completo de comparables aceptados
y rechazados.

```python
from infrastructure.report import build_report

build_report(result, "informe.pdf")
```

**El informe se genera sin una sola llamada de red.** La explicación de la IA es una sección
aditiva: su ausencia no degrada el documento, lo declara.

## Trazabilidad jurídica

Toda fuente que el motor puede citar vive en un registro **cerrado** (`tp_domain/sources.py`), no en
texto libre. Cada entrada lleva su jurisdicción, un localizador tipado —un identificador del BOE, una
URL oficial o una referencia a un documento local, nunca una cadena suelta sin estructura—, la fecha
en que se comprobó por última vez y, cuando no tiene identificador público, la cita literal del
precepto más la advertencia de por qué un tercero no puede resolverlo.

Las fuentes confirmadas contra su texto primario se marcan de forma distinta de las leídas solo a
través de un resumen secundario y no exhaustivo (`verification_confidence`): una fecha de
verificación a secas no debe leerse como más certeza de la que realmente se comprobó.

El informe en PDF y la pantalla imprimen esto de cada fuente que un análisis cita: jurisdicción,
localizador, fecha y confianza. **El motor solo puede citar lo que ya está en el registro** —
`AnalysisResult` no se construye si referencia un id de fuente que el motor no emitió.

Una jurisdicción sin ficha de investigación se queda en `NOT_MODELLED`. Nunca se le asigna la regla
de otro país por analogía: eso sería inventar Derecho comparado.

## Capa de IA (opcional)

El modelo escribe una explicación narrativa **de un análisis ya calculado**. Nunca calcula, nunca
decide y nunca introduce una fuente que el motor no emitiera.

```bash
cp .env.example .env    # y rellena ANTHROPIC_API_KEY y ANTHROPIC_MODEL
```

La clave sale del entorno o de `.env`, leídos en un único punto del proyecto
(`config/settings/base.py`). **Sin clave la aplicación funciona igual**: el informe se genera completo
y la sección de IA declara su ausencia en vez de dejar un hueco.

**El modelo ya no se resuelve en ejecución.** Se fija a mano en `ANTHROPIC_MODEL`, y sin esa variable
la capa de IA queda desactivada. La razón es el tope de gasto: un modelo que no se conoce antes de
llamar tampoco se puede tarifar antes de llamar, y sin tarifa el tope vigilaría un número que no se
paga. Los tokens los reporta siempre el proveedor; nunca se estiman aquí.

Cada borrador se valida antes de llegar al informe: los ids de fuente citados deben pertenecer al
registro cerrado que el motor emitió, y las referencias jurídicas que aparezcan en la prosa se
contrastan también contra él. Un borrador rechazado se reintenta una vez, pasándole solo los motivos
del rechazo; si vuelve a fallar, el informe sale sin la sección.

## Documentación

| Asunto | Dónde |
|---|---|
| Convenciones y fronteras del proyecto | `CLAUDE.md` |
| Diseño completo, gate y orden de construcción | `blueprints/tpip/blueprint.md` |
| Reglas por área | `.claude/rules/` |
