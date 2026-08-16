# Revisión de arquitectura — estado tras `154dd0b`

Fecha: 2026-08-09
Alcance: madurez del MVP, deuda técnica bloqueante, conversión de `tax-research` en reglas, y orden de implementación hasta la demo. Sin cambios de código.
Base: 35 ficheros trackeados, 33 tests en verde, dataset de 55 comparables en 3 industrias.

---

## 1. Qué está suficientemente maduro

**Se toca solo si hay una razón concreta:**

| Componente | Estado | Nota |
|---|---|---|
| Separación dominio / UI | Maduro | `app.py` no calcula nada. Es la regla §3.1 y se cumple |
| `calculate_percentiles()` | Maduro | Correcto y cubierto. Ver salvedad abajo |
| Filtro por industria | Suficiente para MVP | Limitación documentada. El test de regresión que demuestra por qué el filtro es obligatorio es de lo mejor del repo |
| Suite de tests | Maduro | 33 tests con intención real, no de relleno. Es el activo que permite refactorizar sin miedo |
| Rama sin comparables | Maduro | Devuelve `None` limpio, con test |
| Dataset sintético | Suficiente, rígido | Calibrado y documentado. Tres tests fijan percentiles exactos: recalibrar cuesta tocarlos |
| CI | Suficiente | Falta `pip install -e .`; funciona por rootdir, no por diseño |

**Salvedad sobre los percentiles:** `np.percentile` usa interpolación lineal por defecto. La OCDE no impone un método de cálculo, pero distintas administraciones asumen convenciones distintas. Hoy la elección es implícita. Antes de que un informe salga con un P25 impreso, esa decisión debería estar escrita en el docstring y en el propio informe. No es un bug; es una decisión metodológica que ahora mismo nadie ha tomado explícitamente.

---

## 2. Deuda técnica a corregir antes de añadir IA y PDF

Ordenada por si bloquea o no. Los cinco primeros bloquean.

### 2.1 El motor contradice a la OCDE en servicios intragrupo — BLOQUEANTE

Verificado ejecutando el motor:

```
management_fee, software, 5%  →  rango 16,2% – 28,75%  →  score 2, WEAK
"RISKY. Rate 5.0% significantly BELOW benchmark (16.2%). High audit probability."
```

El 5 % es el *safe harbour* de la OCDE para servicios de bajo valor añadido (TPG 2022, cap. VII, párr. 7.61-7.62): un margen que **no necesita justificarse con estudio de comparables**. TPIP lo califica hoy como posición de riesgo alto.

La causa es conceptual: para `management_fee` el motor compara un margen sobre costes contra el *operating margin* de compañías del dataset. Son dos magnitudes distintas. No es TNMM mal implementado: es una comparación que no significa nada.

Los servicios intragrupo están dentro del alcance declarado del MVP. Hay que decidir una de dos:

- **Recomendado:** estrechar el alcance de la Fase 1 a intangibles/cánones, bloquear los demás tipos de operación en la UI con un mensaje explícito ("no soportado en esta versión"), y traer servicios en la Fase 2 con su safe harbour. Coste: el alcance del MVP declarado en la entrevista se reduce. Beneficio: nada de lo que se enseña está mal.
- Alternativa: implementar ya el safe harbour del 5 % y una rama de cálculo para servicios. Coste: dataset nuevo con márgenes sobre costes, cuestionario de calificación del servicio, y Fase 1 se alarga una semana larga.

Lo que no es opción es dejarlo como está: un revisor de Big Four probará servicios intragrupo, porque es la mitad del alcance que anuncias.

### 2.2 No hay fuentes en el resultado — BLOQUEANTE para la capa IA

`AnalysisResult` no tiene ningún campo de base legal. La regla §10 dice que la IA recibe "resultado calculado + benchmark + **fuentes**". Hoy solo existen los dos primeros.

Si se conecta la IA sin ese campo, producirá referencias a párrafos de las Directrices que suenan bien y que nadie ha verificado. Eso no es un fallo de *prompt*: es la infracción exacta de la regla de gobernanza §3.2. **La capa IA no debe construirse hasta que el resultado lleve sus fuentes dentro.** Es la deuda que más barato sale pagar antes y más cara después.

### 2.3 `comparables_used = filtered[:5]` — BLOQUEANTE para el PDF

El truncado a 5 vive en el dominio y su motivo es de UI ("la UI muestra como mucho 5"). Un informe de precios de transferencia se sostiene sobre el conjunto completo de comparables aceptados y rechazados: ese anexo *es* el estudio. El dominio debe devolver el conjunto íntegro y que decida la UI cuántos pinta.

### 2.4 `method_recommended` constante y `transaction_id = "unknown"` — BLOQUEANTE para el PDF

Todo informe saldría con "Method: CUP" y referencia "unknown", incluidos los de servicios. El método debe derivarse del tipo de operación, y cada análisis necesita identificador y fecha estables para ser citable. En pantalla se perdona; impreso, no.

### 2.5 El score no es explicable — BLOQUEANTE para la IA

`p25*0,7` y `p75*1,3` etiquetados como "rough P10-P90". Con P25 = 8,35 el suelo queda en 5,85 %, que no es el P10 de nada. En cuanto la IA redacte "la operación obtiene un 6 sobre 10 porque…", habrá que completar esa frase. Calcular P10 y P90 reales sobre la muestra filtrada es trivial y convierte el tramo en algo defendible.

Aparte: los saltos 9 / 6 / 2 son tres valores fijos disfrazados de escala de 1 a 10. O se documenta que son tres niveles con etiqueta numérica, o se convierte en escala real. Preferible lo primero: menos código y más honesto.

### 2.6 No bloqueantes, pero conviene arrastrarlos en el mismo paso

- `effective_date: datetime` con `default_factory=datetime.now` — no determinismo en el filtro de antigüedad; la UI además pasa un `date`.
- `class Config` de Pydantic v1 en los cuatro modelos: se van a usar mucho `model_dump()` al serializar hacia IA y PDF; migrar ahora a `ConfigDict` evita hacerlo dos veces.
- CI sin `pip install -e .`.

---

## 3. Qué de `tax-research` se convierte en regla en Fase 1

Criterio: entra en Fase 1 lo que **cambia el veredicto sin ampliar el modelo de datos ni exigir cuestionario**. Todo lo demás espera.

### Entra en Fase 1 (2 fichas)

**`jurisdictions/germany/astg-rango-intercuartilico-ajuste-mediana.md` + `jurisdictions/spain/art18-lis-operaciones-vinculadas.md` (solo la parte de regla estadística).**

Es un enum, un diccionario de dos entradas y una rama que devuelve `adjusted_rate = p50` cuando la jurisdicción impone ajuste. No necesita campos nuevos en `Transaction`: `to_country` ya existe y hoy no se usa para nada.

Por qué esta y no otra: es lo único que convierte una calculadora de percentiles en un motor con criterio jurisdiccional, y es la diferencia entre "sé usar numpy" y "sé por qué el mismo precio tiene consecuencias distintas en dos países". Coste estimado: dos días con tests.

**Efecto lateral que resuelve un problema abierto.** La auditoría señalaba que el caso keynote no produce el veredicto documentado (12 % en software cae en MODERATE, no fuera de rango). Con la regla alemana el caso deja de necesitar recalibración: el mismo 12 % arroja "sin regla estadística legal, valoración caso por caso" frente a "ajuste automático a la mediana, 10,1 %". Eso es mejor demo que un semáforo en rojo.

**Pero obliga a una decisión de producto:** el corredor documentado es España → Luxemburgo, y el §1.3a AStG no se aplica a Luxemburgo. Para enseñar la comparación hay que cambiar el caso a España → Alemania, o presentar Alemania como escenario alternativo. Recomiendo cambiar el corredor: una pantalla, un caso. Se pierde el guiño a Luxemburgo como jurisdicción de estructuración de intangibles, que es evocador pero no aporta nada al motor.

### Espera a Fase 2

| Ficha | Motivo |
|---|---|
| `frameworks/safe-harbours-y-htvi.md` | Exige calificar la operación como servicio de bajo valor añadido → cuestionario + dataset de márgenes sobre costes |
| `frameworks/ocde-directrices-2022-...` | Marcos de 6 pasos, DEMPE y *benefits test* son cuestionario, no cálculo |
| `frameworks/criterios-seleccion-comparables.md` | Exige enriquecer el dataset con campos funcionales que hoy no existen |
| `jurisdictions/eu/directiva-intereses-canones-2003-49.md` | Es el Tax Impact Modeler. Motor distinto, Fase 2 por roadmap |
| `jurisdictions/spain/ris-documentacion-...` | Requiere añadir cifra de negocios a `Transaction`. Barato, pero es alcance nuevo en Fase 1 |
| `processes/doctrina-teac-...` | Factor cualitativo. Solo si queda tiempo al final y se condiciona de verdad; si no, es decoración |
| `jurisdictions/eu/propuesta-directiva-tp-2023-retirada.md` | Nunca es regla. Sirve como nota de contexto en el informe |

Tentación a resistir: meter el régimen sancionador del art. 18.13 LIS dentro del score. Apilar una segunda heurística sobre una que aún no es explicable empeora el problema 2.5.

---

## 4. Orden de implementación hasta la demo

Cuatro semanas, 20 h/semana. El orden lo fija una regla: **todo lo que consume `AnalysisResult` se construye después de que `AnalysisResult` esté estable.**

| # | Bloque | Días | Por qué en esta posición |
|---|---|---|---|
| 1 | **Saneamiento del dominio**: 2.3, 2.4, 2.5, 2.6 + decisión sobre servicios (2.1) | 1,5 | PDF e IA consumen esta estructura. Cambiarla después obliga a rehacer los dos |
| 2 | **`tp_domain/rules/` — regla estadística ES/DE** + campo `sources` en el resultado (2.2) | 2 | Da al informe algo que decir y a la IA algo que citar. Con el campo de fuentes desde el principio, no como parche |
| 3 | **Informe PDF** | 2,5 | Es el entregable. Sin él la Fase 1 no está cerrada aunque el motor funcione |
| 4 | **Capa IA** sobre resultado + fuentes, con `ai/prompts/explain_analysis_v1.md` versionado | 2 | Va último de los funcionales: consume todo lo anterior y su salida es una sección del informe |
| 5 | **Pase de presentación**: gráfico del rango, registro profesional, caso de ejemplo en un clic | 1 | Sobre estructura ya congelada. Antes sería tirar el trabajo |

Total ≈ 9 días de trabajo efectivo sobre ~11 disponibles. El margen es estrecho y deliberado.

**Por qué el PDF antes que la IA**, siendo la IA lo que da nombre al proyecto: sin PDF no hay entregable y la Fase 1 no cierra; sin IA hay una herramienta completa a la que le falta una sección. Además la explicación generada se maqueta dentro del informe, así que construir la IA primero significa integrarla dos veces. El coste de este orden es que la parte de IA queda para la última semana y es la que más margen de sorpresa tiene; se mitiga porque, con el resultado y las fuentes ya estables, es la pieza más acotada de las cinco.

**Lo que no entra en estas cuatro semanas, y conviene decirlo en voz alta:** servicios intragrupo con safe harbour, cuestionario DEMPE, scoring de comparables, retenciones, persistencia en SQLite y capa FastAPI. Todo eso es Fase 2 o más allá. Un MVP cerrado vale más que una plataforma a medias — es la regla §13 del propio proyecto.
