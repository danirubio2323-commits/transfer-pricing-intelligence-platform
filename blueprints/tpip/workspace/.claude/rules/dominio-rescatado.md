---
description: Reglas del código rescatado — dominio, capa de IA e infraestructura de informe. Léelas antes de tocar nada bajo tp_domain/, ai/ o infrastructure/.
paths:
  - "tp_domain/**"
  - "ai/**"
  - "infrastructure/**"
  - "tests/domain/**"
  - "tests/ai/**"
  - "tests/report/**"
---

# Código rescatado

Este código **existía antes de la migración y funciona**. Son 2.684 líneas de Python y 180 pruebas que
pasan. No es legado que haya que modernizar: es el producto.

## La invariante que manda sobre todo lo demás

**La suite rescatada mantiene exactamente 180 pruebas**: `tests/domain` 89 + `tests/ai` 53 +
`tests/report` 38. Si retiras una, la sustituyes por otra en el mismo fichero.

- **Las pruebas nuevas van a `tests/web/`.** Añadir una aquí cambia el recuento y rompe hacia atrás el
  gate del paso 3, que se vuelve a ejecutar al final de cada paso posterior.
- El comando que lo comprueba es `uv run pytest tests/domain tests/ai tests/report`.

## Qué se puede tocar y qué no

| Ruta | Regla |
|---|---|
| `tp_domain/**` | **No se toca.** Ni el modelo, ni las reglas, ni el registro de fuentes, ni el dataset |
| `ai/schemas.py`, `ai/validators.py`, `ai/prompts/**` | **No se tocan.** Son el contrato de gobernanza de la capa de IA |
| `ai/claude_client.py` | Solo en el paso 8, para retirar la resolución dinámica del modelo |
| `infrastructure/theme.py` | Solo en el paso 9, y **solo añadiendo claves** a `COLORS` |
| `infrastructure/report/**`, `infrastructure/charts.py` | **No se tocan** |

## Fronteras

- **`tp_domain/` no importa nada del proyecto.** Ni Django, ni `apps/`, ni `ai/`, ni
  `infrastructure/`. Es el núcleo: todo apunta hacia dentro. Un `import django` aquí es un defecto.
- **`ai/` importa de `tp_domain` y de nada más.** **No importa Django**: desde el paso 8 su
  configuración —clave y modelo— se le inyecta desde fuera, no la descubre. `apps/analisis/services.py`
  es el único puente.
- **`infrastructure/` importa de `tp_domain`.** No importa de `apps/` ni de Django.

## Reglas del dominio

- **El registro de fuentes es cerrado.** Toda fuente citable está en `tp_domain/sources.py`, y son 5.
  `AnalysisResult` **no se puede construir** si un `source_ids` cita un id que el motor no emitió: la
  gobernanza es una restricción del modelo de datos, no una instrucción en un prompt.
- **Una fuente nueva lleva jurisdicción, localizador tipado y fecha de verificación.** Si su
  `locator_type` es `OFFLINE`, exige además `quote` y `disclaimer`: es la única evidencia verificable
  que queda cuando no hay identificador público resoluble.
- **Una jurisdicción sin ficha de investigación se queda en `NOT_MODELLED`.** Nunca se le asigna la
  regla de otro país por analogía: eso es inventar Derecho comparado. El mapa de
  `JURISDICTION_RANGE_RULES` crece ficha a ficha.
- **`ENGINE_VERSION` viaja dentro de cada `AnalysisResult`.** Si cambias la lógica de cálculo, súbela:
  un análisis emitido hoy tiene que poder reproducirse mañana sabiendo con qué lógica salió.

## La capa de IA

**El motor calcula; el modelo explica, fundamenta y puede sugerir, pero nunca decide y nunca escribe
un número.** Cuando se llama al modelo, el `AnalysisResult` ya está calculado entero.

- `explain_analysis` **no lanza nunca.** Devuelve la explicación validada o `None`. Ninguna ruta de
  error propaga hacia arriba: el informe se genera igual.
- El reintento es **uno**, y envía **solo los motivos de rechazo**. Añadir contexto nuevo en la
  corrección permitiría que el segundo borrador dijera cosas que el primero no podía decir.
- `ai/` **no cuenta tokens**: transporta el `usage` que reporta el proveedor, sin interpretarlo.
