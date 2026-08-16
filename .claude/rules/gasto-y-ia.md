---
description: Freno de gasto, registro de llamadas al modelo y arnés de evaluación. Léelas antes de tocar apps/ia/, el servicio de análisis o apps/evaluacion/.
paths:
  - "apps/ia/**"
  - "apps/analisis/services.py"
  - "apps/evaluacion/**"
---

# Gasto y capa de IA

## El principio rector

**El motor calcula; el modelo explica, fundamenta y puede sugerir, pero nunca decide y nunca escribe un
número.** Cuando `services.py` llama al modelo, el `AnalysisResult` ya está calculado entero: los
percentiles, los veredictos por jurisdicción y los factores de riesgo. La explicación se añade encima y
**no puede modificar nada de lo anterior**.

## El freno, y su orden

- **`comprobar_cuota(usuario)` se llama ANTES de construir el cliente, nunca dentro de él.** Para
  cuando el cliente existe, ya se ha decidido gastar.
- El orden dentro de `crear_caso` se comprueba por posición en el fichero: `comprobar_cuota` aparece
  **antes** que `explain_analysis`.
- **Superar el tope desactiva la sección de IA; nunca bloquea el producto.** El análisis se calcula, el
  caso se persiste y el informe sale completo declarando la ausencia. Es la misma ruta de degradación
  que la falta de clave.
- El límite es **inclusivo por el lado del rechazo**: alcanzar el tope ya rechaza.

## El uso lo reporta el proveedor

**Nunca se estiman tokens.** Nada de `tiktoken`, nada de `count_tokens`, nada de contar palabras. Un
recuento propio diverge del que factura el proveedor, y entonces el tope vigila un número que no es el
que se paga. `ai/claude_client.py` devuelve el `usage` tal cual; `apps/ia/cuota.py::coste_de()` lo
convierte a euros con las tarifas de la configuración.

**Con las tarifas sin fijar, `coste_de()` devuelve `0` en vez de fallar.** Un sistema sin tarifas
registra uso pero no puede imputar gasto, y decirlo con un cero es más honesto que inventar un precio.

## `LlamadaLLM`

- **`apps/ia/registro.py` es el único escritor.** El panel la muestra en solo lectura: es un registro
  contable, no un formulario.
- **Toda llamada lleva su `proposito`**: `explicacion` o `evaluacion`. Sin ese campo, el coste del arnés
  y el del producto se suman en el mismo número, y una pasada de evaluación consumiría el tope mensual
  de un usuario real.
- `error` guarda **la categoría** del fallo, nunca el contenido de la respuesta. Igual que el registro
  de eventos: ni la clave, ni el cuerpo del formulario, ni el texto que devuelve el modelo.

## Degradación

La capa entera está construida para poder fallar sin que se note. Cinco caminos, y los cinco acaban
igual —el caso se guarda sin explicación y el informe la declara ausente—:

| Situación | Llamada de red | Fila en `llamadas_llm` |
|---|---|---|
| Sin `ANTHROPIC_API_KEY` | no | no |
| Sin `ANTHROPIC_MODEL` | no | no |
| Cuota agotada | no | no |
| La API falla o agota el tiempo | sí | sí, con `error` y coste 0 |
| El borrador no pasa el validador | sí | sí |

**`explain_analysis` no lanza nunca.** Si lo hace, es un defecto.

## El arnés de evaluación

- **El conjunto dorado vive en `evaluacion/casos/*.json`, en control de versiones.** Un conjunto que
  solo existe en la base de datos no se revisa en un *pull request*, y entonces deja de ser dorado. La
  tabla `CasoEvaluacion` es un índice reconstruible, igual que `Ficha` lo es del corpus.
- **Los puntuadores van de lo más barato a lo más caro y paran en el primero que decide**: primero las
  comprobaciones deterministas —fuentes dentro del registro emitido, ninguna cifra nueva, extensión
  dentro de `MIN_WORDS`/`MAX_WORDS`—, después las coincidencias léxicas, y solo si no deciden, un
  juicio del modelo. La mayoría de los casos se resuelven en la primera capa, que no cuesta nada.
- **La puerta sale con el código concreto**, no con «algo distinto de cero»: `0` si la tasa iguala o
  mejora la línea base, `1` si baja, `2` si no hay línea base. Un error de uso también sale distinto de
  cero, y una puerta escrita así pasaría en vacío para siempre.
- **`EjecucionEvaluacion` registra el coste y las latencias JUNTO a la tasa de acierto.** Una mejora de
  precisión que triplica el coste es una decisión, no una mejora. Y `sha_commit` es lo que hace
  reproducible una tasa: sin él no se sabe contra qué código ni contra qué conjunto se midió.
- Ninguna prueba del arnés toca la red: se ejercita con dobles.
