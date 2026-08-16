# Auditoría técnica — capa jurídica, evidencia y herramientas de IA

Fecha: 10 agosto 2026
Commit auditado: `f9c7fb3` · árbol limpio (`git status` sin cambios)
Alcance: lectura completa del código, documentación e historial. Sondeo en vivo de los MCP del entorno.
**No se ha modificado código. No se han creado commits.**

Nivel de confianza de cada afirmación, marcado a lo largo del documento:

- **[V]** verificado leyendo el código o ejecutando la herramienta
- **[I]** inferencia razonada a partir de lo verificado
- **[NV]** no verificado en esta auditoría

Limitación de método declarada: **la suite de tests no se ha ejecutado**. El sandbox Linux no pudo instalar las dependencias (timeout de `pip install`). El recuento de tests procede de contar funciones `def test_` en el árbol, no de una ejecución. **[V]** en el recuento, **[NV]** en que pasen hoy.

---

## 1. Qué tenemos realmente hoy

Código Python propio: **4.740 líneas** en 29 ficheros (excluidos `.venv` y corpus). **[V]**

| Capa | Estado real | Líneas | Tests (recuento) |
|---|---|---|---|
| `tp_domain/models.py` | Completo y en uso | 374 | 20 |
| `tp_domain/calculations/arm_length_range.py` | Completo y en uso | 342 | 27 |
| `tp_domain/rules/statistical_rules.py` | Completo y en uso, 2 jurisdicciones | 165 | 16 |
| `tp_domain/sources.py` | Completo, registro de **5 entradas** | 117 | (cubierto indirectamente) |
| `ai/schemas.py` + `ai/validators.py` + `ai/claude_client.py` | Completo y conectado | 441 | 46 |
| `ai/prompts/explain_analysis_v1.md` | Versionado, cargado en ejecución | — | 1 (comprueba versión) |
| `infrastructure/report/pdf_report.py` | Completo y en uso | 608 | 22 |
| `infrastructure/theme.py` + `charts.py` | Completo | 291 | 13 |
| `ui/app.py` (Streamlit) | Completo, único consumidor | 403 | — |
| **`api/`** | **Vacío. Solo `__init__.py` de 0 bytes** | 0 | — |

Total funciones de test: **144**. **[V]** (por recuento, no por ejecución)

El flujo real, verificado línea a línea:

```
ui/app.py
  → tp_domain.calculations.calculate_arm_length_range(Transaction)
      → load_dataset()  →  tp_domain/comparables.json  (55 registros sintéticos, v1.0)
      → filter_comparables()  →  aceptados + RejectedComparable con motivo
      → calculate_percentiles()  →  numpy, P10/25/50/75/90
      → statistical_rules.assess() × 2 (pagador y perceptor)
      → _risk_factors()  →  RiskFactor con source_ids
      → source_registry.resolve(ids)  →  KeyError si un id no existe
      → AnalysisResult  (validator: toda cita debe existir en sources)
  → [opcional] ai.claude_client.explain_analysis(result)  →  AIExplanation | None
  → infrastructure.report.pdf_report.render_report_bytes(result)
```

Lo que este flujo demuestra y conviene no perder de vista: **el motor no depende de la IA en ninguna rama**. El PDF se genera completo sin clave de API. **[V]**

---

## 2. Qué creemos tener pero no está implementado

Esta es la sección que motiva la auditoría, así que va sin adornos.

### 2.1 El corpus fiscal no forma parte del repositorio

`tp_domain/knowledge/Cerebros_Fiscales/` existe físicamente en disco: 116 fichas Markdown en `wiki/` y ~117 PDFs en `raw/`. **[V]**

Pero:

- `git ls-files tp_domain/knowledge` devuelve **0 ficheros**. **[V]**
- `.gitignore` líneas 229-234 lo excluyen explícitamente. **[V]**
- **Ningún fichero `.py` del proyecto contiene la cadena `knowledge` ni `Cerebros`.** Grep sobre `ai/`, `api/`, `ui/`, `tp_domain/`, `infrastructure/`, `tests/`: cero coincidencias. **[V]**

Traducción: el corpus es material de trabajo del analista (tú, o Claude asistiéndote), **no un activo del producto**. Hoy no alimenta nada en ejecución.

Hay además una inconsistencia declarativa: `documentation/tax-research/README.md` afirma que "el corpus documental completo vive fuera de este repositorio, en el proyecto `Cerebros_Fiscales`". Físicamente vive dentro del árbol, en `tp_domain/`, que es precisamente el directorio que las instrucciones del proyecto reservan para lógica ejecutable. **[V]**

### 2.2 `infrastructure/wiki_parser.py` no existe

`documentation/analisis-cerebros-fiscales.md` §3 lo propone como pieza de integración ("lo más barato de todo el paquete"). No se implementó. **[V]**

### 2.3 Ninguna herramienta de investigación jurídica está integrada en el código

`Catalogo_Herramientas_IA_Daru.md` documenta MCP-BOE, EUR-Lex, CENDOJ, Zotero y Firecrawl como "✅ Activo". Es correcto — **pero activos en el entorno de Claude, no en TPIP**. Ninguna aparece en `requirements.txt`, en `pyproject.toml` ni en ningún import. **[V]**

Esta distinción es el hallazgo más importante de toda la auditoría y condiciona la sección 10.

### 2.4 Lo que la propia documentación anuncia y no está

| Anunciado en | Qué | Estado |
|---|---|---|
| `documentation/tax-research/README.md` | `tp_domain/rules/spanish_rules.py`, `german_rules.py`, `safe_harbours.py`, `comparable_selection.py`, `comparable_scoring.py`, `calculations/withholding.py` | Ninguno existe. Solo `statistical_rules.py` **[V]** |
| Instrucciones §6 | `database/`, `tests/` como capa, `tp_domain/validators/`, `tp_domain/comparables/` | Solo `tests/` existe **[V]** |
| Instrucciones §12 | FastAPI, React/TS/Tailwind, SQLite | Ninguno. Streamlit + JSON plano (desviación consciente y registrada) **[V]** |
| Entrevista §2 | TNMM como método del MVP | El motor devuelve siempre `TPMethod.CUP`, con justificación razonada en `METHOD_RATIONALE_ROYALTY` **[V]** |

---

## 3. Auditoría de herramientas de IA

### 3.1 Realmente implementadas y utilizables

**Única herramienta de IA en el producto: el cliente de Anthropic Messages API.**

| Dimensión | Detalle |
|---|---|
| Archivo | `ai/claude_client.py` (267 líneas) |
| Quién la invoca | `ui/app.py:375`, dentro de `if resolve_api_key():` + checkbox de usuario. **Nunca se invoca automáticamente.** |
| Entrada | `ExplanationRequest.from_result(result).model_dump_json(indent=2)` como único mensaje de usuario; system prompt extraído del bloque ` ```text ` de `ai/prompts/explain_analysis_v1.md` |
| Salida | `AIExplanation` validado, o `None` |
| Punto del flujo | Posterior al cálculo, previo al PDF. Sección 4 del informe |
| Llamadas externas | **Sí, dos endpoints**: `client.messages.create()` y `client.models.list(limit=50)` (este último solo si `ANTHROPIC_MODEL` no está definida) |
| Parámetros | `max_tokens=1500`, `temperature=0.2`, `MAX_ATTEMPTS=2` |
| Tests | 46 funciones entre `tests/ai/test_explanation_flow.py` y `test_validators.py`, con `FakeAnthropic` en `tests/ai/mocks.py`. Ningún test golpea la API real |
| Función en TPIP | Redactar en prosa un análisis ya cerrado. Nada más |

Sub-herramienta relevante y fácil de pasar por alto: **`resolve_model()` hace una llamada de red adicional** para elegir el Sonnet más reciente cuando `ANTHROPIC_MODEL` está vacía. Es una decisión defendible (el default envejece solo) pero introduce una dependencia de red en el arranque de la capa y un resultado no determinista entre ejecuciones: dos informes emitidos el mismo día pueden usar modelos distintos si Anthropic publica uno nuevo entre medias. Queda registrado en `AIExplanation.model`, así que es trazable a posteriori. **[V]**

### 3.2 Implementadas pero no conectadas al flujo

**Ninguna.** No hay código de IA muerto. `api/` está vacío, pero eso es ausencia de capa API, no una herramienta desconectada. **[V]**

### 3.3 Solamente documentadas

Todas las del catálogo. Ninguna es invocable desde TPIP.

| Herramienta | Dónde se documenta | Verificación en vivo (10 ago 2026) | Integrada en código |
|---|---|---|---|
| MCP-BOE | `Catalogo` §1 | ✅ responde **[V]** | No |
| EUR-Lex MCP | `Catalogo` §1 | ✅ responde **[V]** | No |
| CENDOJ MCP | `Catalogo` §1 | ✅ responde **[V]** | No |
| Zotero MCP | `Catalogo` §1 | ✅ conecta, **0 ítems** **[V]** | No |
| Firecrawl | `Catalogo` §1 | **[NV]** no sondeado | No |
| Skills (`analiza-cdi`, `ficha-jurisprudencia`) | `Catalogo` §3 | Disponibles en el entorno **[V]** | No |

### 3.4 Previstas para fases futuras

- Research Companion completo: instrucciones §5, Fase 3 (ingesta documental, búsqueda semántica, búsqueda sobre Directrices OCDE).
- `wiki_parser.py` + `corpus_index.json`: `documentation/analisis-cerebros-fiscales.md` §3.
- Uso del corpus como contexto documental del prompt: propuesto en el mismo documento §3, **explícitamente descartado en la implementación real** — el prompt v1 no recibe extractos de ficha, solo `allowed_sources` con cita e id. **[V]**

---

## 4. Auditoría de investigación jurídica

### A. Conocimiento ya almacenado

**A.1 — Registro de fuentes ejecutable: 5 entradas.** `tp_domain/sources.py`. Es lo único que el motor puede citar. **[V]**

| id | kind | pinpoint | `official_ref` |
|---|---|---|---|
| `es-lis-art18-4` | legislation | Art. 18.4 — determinación del valor de mercado | `BOE-A-2014-12328` |
| `de-astg-1-3a` | legislation | §1.3a — estrechamiento del rango y ajuste a la mediana | `AStG §1 Abs. 3a` |
| `oecd-tpg-2022-cap3` | guidelines | Análisis de comparabilidad y rango | — (sin `official_ref`) |
| `oecd-tpg-2022-cap6` | guidelines | Intangibles — DEMPE (párr. 6.34) | — (sin `official_ref`) |
| `tpip-dataset-v1` | dataset | — | — |

Cero entradas de tipo `CASE_LAW`, pese a que el enum lo contempla. **[V]**

**A.2 — Fichas de investigación versionadas: 9.** `documentation/tax-research/`. Cubren España (Art. 18 LIS, RIS), Alemania (AStG), UE (2003/49, COM(2023)529 retirada), marcos OCDE, criterios de comparabilidad, safe harbours/HTVI, doctrina TEAC. **[V]**

Detalle que importa para la fase que viene: **ninguna tiene frontmatter YAML**. Son prosa Markdown con negritas (`**Origen:**`, `**Fuente primaria:**`). No son parseables sin heurísticas frágiles. **[V]**

Contraste incómodo: las 116 fichas de `Cerebros_Fiscales/wiki/` **sí** tienen frontmatter YAML estructurado (`titulo`, `fecha`, `origen`, `fuente_raw`, `enlaces`) y, según `documentation/analisis-cerebros-fiscales.md`, parsea el 100%. **La capa derivada perdió la estructura legible por máquina que sí tenía la capa origen.** **[V]**

**A.3 — Corpus `Cerebros_Fiscales`:** 116 fichas + ~117 PDFs. Gitignored, no leído por código. Ver §2.1.

### B. Fuentes consultables mediante herramientas

**Ninguna desde TPIP. Todas desde Claude como asistente.** Verificado en vivo:

| Fuente | Herramienta | Resultado del sondeo |
|---|---|---|
| Legislación española consolidada | `mcp-boe` | `search_law_articles(BOE-A-2014-12328, "operaciones vinculadas")` → devuelve `a18` con texto. **Funciona bien cuando ya sabes el `law_id`** **[V]** |
| Legislación española (búsqueda ciega) | `mcp-boe` | `search_consolidated_legislation("impuesto sobre sociedades operaciones vinculadas")` → devolvió tres normas urbanísticas y ambientales de la Comunitat Valenciana. **La búsqueda global es ruidosa y no relevante** **[V]** |
| Derecho UE | `eur-lex` | `lookup_celex(32003L0049)` → resuelve a work URI CELLAR, tipo DIR, fecha 2003-06-03. Limpio **[V]** |
| Jurisprudencia española | `cendoj` | `buscar_jurisprudencia("operaciones vinculadas precios de transferencia", jurisdiccion=["contencioso"])` → 7.970 resultados. **Entre los 10 primeros hay tráfico de drogas, blanqueo y despido objetivo.** El orden es por fecha, no por relevancia, y el filtro de jurisdicción no filtró **[V]** |
| Corpus bibliográfico propio | `zotero` | Conecta. **"My Library — 0 items"**. La capa de trazabilidad bibliográfica está vacía **[V]** |

### C. Fuentes que el sistema todavía no puede consultar

Ni TPIP ni Claude tienen acceso instrumentado a:

- **Directrices OCDE de Precios de Transferencia 2022.** No hay MCP ni API. Existe el PDF en el corpus local (`raw/Normativa_Internacional/OCDE_BEPS/`), pero ningún código lo lee y `oecd-tpg-2022-cap3/cap6` no tienen `official_ref`. **Las dos fuentes que el motor cita en casi todos los análisis son las menos verificables del registro.** **[V]**
- **Fuentes alemanas.** No hay MCP para `gesetze-im-internet.de`, ni para el BMF (circulares administrativas: VWG Verrechnungspreise), ni para el BFH. **[V]** El propio `Source` alemán lleva un disclaimer que dice: *"la ficha marca la lectura del §1.3 como dirigida, no exhaustiva. Verificar el texto vigente antes de usar como asesoramiento"*. **[V]**
- **Doctrina administrativa española.** DGT (consultas vinculantes) y TEAC no están cubiertos por CENDOJ, que es judicial. **[V]**
- **AEAT** (informes, notas, criterios de la Oficina Nacional de Fiscalidad Internacional). **[V]**
- **Bases de comparables comerciales** (Orbis, Amadeus, RoyaltyRange, ktMINE). Sin acceso, y correctamente declarado como limitación en el disclaimer de `tpip-dataset-v1`. **[V]**

### D. Capacidades previstas en el roadmap

Fase 3 (Research Companion): ingesta documental, búsqueda semántica, búsqueda sobre Directrices OCDE. Sin código, sin spec técnica más allá de las cuatro líneas de las instrucciones. **[V]**

---

## 5. Cómo se almacenan hoy las fuentes — auditoría de trazabilidad

### Lo que SÍ existe, y es mejor de lo que sugiere la pregunta

No tenemos "solo una lista textual de `sources_cited`". Existe un grafo tipado y validado:

```
AnalysisResult.sources: List[Source]          ← registro emitido, cerrado
      ↑ validado por _every_cited_source_exists (pydantic model_validator)
      │
JurisdictionAssessment.source_ids: List[str]  ← afirmación jurídica → fuente
RiskFactor.source_ids: List[str]              ← factor de riesgo → fuente
AIExplanation.sources_cited: List[str]        ← prosa de IA → fuente
```

Si cualquiera de esas listas contiene un id que no está en `sources`, **el `AnalysisResult` no se construye** — `ValueError` en el validador. Y `source_registry.resolve()` lanza `KeyError` si el motor pide un id inexistente. Son fallos ruidosos, no degradaciones silenciosas. **[V]**

El PDF imprime, por jurisdicción, la consecuencia y debajo sus fuentes con pinpoint (`pdf_report.py:400`), más un anexo de fuentes con tipo, referencia, `official_ref` y disclaimer (`:425-431`). **[V]**

### Lo que NO existe — el gap real

Contra el modelo que planteas (`afirmación → fuente → disposición → jurisdicción → vigencia → ubicación → fecha de consulta`):

| Eslabón | Estado | Detalle |
|---|---|---|
| afirmación → fuente | ✅ **Existe y está validado** | `source_ids` + validator |
| → disposición concreta | 🟡 **Parcial** | `pinpoint` es **texto libre**: `"Art. 18.4 — determinación del valor de mercado"`. No hay campo estructurado (norma / artículo / apartado) |
| → jurisdicción | ❌ **No existe como campo** | Se infiere del prefijo del id (`es-`, `de-`) por convención no forzada. `Source` no tiene `jurisdiction` |
| → vigencia | ❌ **No existe** | Ningún campo de fecha. La única marca de vigencia del sistema entero es un fichero de investigación (`propuesta-directiva-tp-2023-retirada.md`) que documenta una norma que *no* debe implementarse. Es un guardarraíl documental, no un dato |
| → ubicación / origen | 🟡 **Débil** | `official_ref` es `Optional[str]` sin tipar: `"BOE-A-2014-12328"` (identificador real) convive con `"AStG §1 Abs. 3a"` (que no es un identificador de nada). Dos de las cinco fuentes no lo tienen. Ninguna tiene URL, ELI ni CELEX |
| → fecha de consulta | ❌ **No existe** | Nada en `Source` ni en `AnalysisResult` registra cuándo se verificó la fuente |
| → texto de la disposición | ❌ **No existe** | No se guarda ni un extracto literal. La evidencia es una *cita*, no un *texto citado* |

Y un eslabón adicional que sí existe y conviene reconocer: `research_note` apunta a la ficha del repo, que apunta a la ficha del corpus, que apunta al PDF primario. La cadena documental existe **pero se rompe en el segundo salto**: la ficha del repo referencia `Cerebros_Fiscales/wiki/...`, que no está versionado. Quien clone el repo tiene el primer eslabón y nada más. **[V]**

---

## 6. Cómo se valida hoy la evidencia

Cuatro controles en `ai/validators.py`, en el orden en que se aplican. **[V]**

1. **`sources_cited` ⊆ `allowed_source_ids`.** Determinista, sin falsos negativos posibles.
2. **Referencias normativas en la prosa.** `extract_legal_references()` normaliza y extrae con 5 familias de regex (artículos/§, párrafos, capítulos romanos, normas con número/año, resoluciones y sentencias). `_is_covered()` acepta citas **menos** específicas que la emitida (`"artículo 18"` cubierto por `"art 18.4"`) y rechaza las **más** específicas (`"art 18.4.b"` → apartado inventado).
3. **Formato.** Rechaza markdown y listas (destino: PDF maquetado).
4. **Extensión.** 40–700 palabras (el prompt pide 120–450; el margen evita rechazos por un puñado de palabras).

Lo que **no** valida, y está documentado a propósito en el docstring del módulo:

- **Consistencia numérica.** Descartada: el modelo escribe "dos jurisdicciones" legítimamente.
- **Verbos de recomendación.** Descartada: la conclusión del propio motor usa "exigencia de documentación soporte", y una paráfrasis fiel dispararía el rechazo.
- **Contradicción semántica del veredicto.** Ver §7.

Sobre la evidencia *jurídica* (no la prosa de la IA): **no hay validación de ningún tipo**. Nada comprueba que `BOE-A-2014-12328` exista, que el Art. 18.4 siga vigente, ni que el §1.3a AStG diga lo que la ficha afirma. La verificación es humana, ocurrió una vez, y no dejó fecha. **[V]**

---

## 7. Auditoría de la capa IA — respuestas concretas

`ExplanationRequest → [Claude] → ExplanationDraft → validate_draft → AIExplanation`

**Qué información recibe Claude.** Solo la proyección de `ExplanationRequest`: `analysis_id`, `method`, `method_rationale`, `transaction` (descripción, sector, países, importe formateado, tipo), `benchmark` (5 percentiles, aceptados, rechazados, método de percentil), `position`, `assessments[]` (país, rol, regla, nivel, score, ajuste, consecuencia redactada, source_ids), `risk_factors[]` (severidad + mensaje), `engine_conclusion` y `allowed_sources[]` (id, citation, pinpoint). **[V]**

**Qué NO recibe.** El listado de comparables aceptados y rechazados (solo los recuentos); los `research_note` y `disclaimer` de las fuentes; el `official_ref`; cualquier texto normativo. Decisión declarada en el prompt: "menos superficie de entrada es menos superficie para alucinar". **[V]**

**Qué fuentes recibe.** Únicamente `id`, `citation` y `pinpoint` de las fuentes que el motor emitió en ese análisis concreto — típicamente 3 o 4 de las 5 del registro. **No recibe el texto de ninguna norma.** Claude cita literatura que no ha leído; se apoya en su conocimiento previo o parafrasea la `citation`. **[V]**

**Cómo se limita a explicar.** Por construcción (proyección cerrada, sin comparables ni texto normativo), por prompt (7 reglas inviolables), y por tipo (`ExplanationDraft` no es adjuntable a un `AnalysisResult`; solo `validate_draft` lo promueve). El nombre `Draft` hace el trabajo de recordarlo. **[V]**

**Cómo se valida.** Ver §6.

**Si introduce una fuente inexistente en `sources_cited`.** Rechazo con el id ofensor nombrado → reintento único con solo los motivos → si vuelve a fallar, `explain_analysis` devuelve `None` y el PDF sale sin sección 4. Doble red: aunque el validador fallase, `AnalysisResult._every_cited_source_exists` impediría construir el resultado. **[V]**

**Si introduce una norma no emitida en la prosa.** Extracción por regex y comparación contra las referencias derivadas de `citation` + `pinpoint`. Mismo destino. **Limitación real:** la cobertura depende de las 5 familias de regex. Una norma citada de forma no prevista (por ejemplo, "la Directiva matriz-filial", sin número; o `"Tz. 3.4.12.5 VWG"` alemán) **no se detecta**. **[I]** — el patrón no la cubre, aunque no lo he probado con un caso construido.

**Si contradice el resultado del motor.** **No se detecta.** Está documentado como límite conocido en `tests/ai/test_explanation_flow.py::test_verdict_change_is_not_machine_detectable`, que construye una narrativa afirmando "dentro del rango" cuando el tipo supera el P90, y comprueba que **pasa la validación**. La mitigación es de diseño, no de control: la prosa no puede alterar el análisis, y el PDF imprime "Por encima del P90", "Riesgo alto" y el ajuste alemán del 10,1 % **por encima** de la sección de IA, donde la contradicción queda a la vista de quien revise. **[V]**

Coincide con tu instrucción de no perseguir validación semántica perfecta. Registrarlo como límite explícito con un test que lo fija es mejor política que una heurística que dé falsa seguridad.

**Si no existe API key.** `resolve_api_key()` devuelve `None` → la UI ni siquiera muestra el checkbox, imprime un aviso; si se llamara igualmente, `build_client()` lanza `ClaudeUnavailable`, capturado por `explain_analysis`, que devuelve `None`. El PDF imprime en la sección 4 que el informe se generó sin IA y que su ausencia no afecta a la validez. Cubierto por `test_report_is_complete_without_an_api_key`. **[V]**

---

## 8. Separación de responsabilidades — evaluación

La regla que quieres preservar (*el motor calcula, la capa jurídica aporta evidencia, Claude explica*) **se respeta hoy, y no por disciplina sino por construcción**. Es el activo más valioso del repositorio y lo que hace que esta fase sea viable.

Mecanismos que la sostienen, todos verificados:

| Riesgo | Mecanismo que lo bloquea |
|---|---|
| Claude fija el score | `defensibility_score` viene de `POSITION_SCORING`, tabla estática. Claude lo recibe ya calculado |
| Claude fija la posición | `classify_position()`, aritmética pura |
| Claude fija la consecuencia jurisdiccional | `_consequence()` redacta texto determinista. Claude recibe la cadena hecha |
| Claude fija el riesgo | `_risk_factors()`, condiciones sobre percentiles |
| Claude fija las fuentes | Registro cerrado + validador + validador de modelo |
| Claude escribe en el resultado | `AIExplanation` es un campo `Optional` añadido por `model_copy`; no hay ruta en la que el modelo mute nada más |
| La UI calcula | `ui/app.py` no contiene aritmética fiscal (verificado por lectura) |

**Dónde se puede romper en la fase que viene** — señalado ahora porque es barato:

1. **Si la capa jurídica devuelve texto normativo a Claude.** Hoy Claude no ve texto de normas. Si la capa de evidencia empieza a inyectar el articulado del Art. 18.4, la superficie de alucinación crece y el validador actual (que compara referencias contra `citation`/`pinpoint`) queda corto: pasará a haber referencias legítimas en el input que no están en `allowed_sources`. **Hay que decidir esto antes de escribir código, no después.**
2. **Si la capa jurídica selecciona qué evidencia es relevante usando un LLM.** Sería Claude decidiendo fuentes, que es exactamente lo que la regla prohíbe. La selección debe ser determinista (mapa jurisdicción+tipo de operación → ids de evidencia), o bien humana-en-el-bucle con registro de quién decidió.
3. **Si `official_ref` pasa a resolverse en ejecución** (llamar al BOE para confirmar que la norma existe), el análisis deja de ser reproducible offline y adquiere una dependencia de red en la ruta crítica. Ver §10.

---

## 9. Arquitectura actual

```
                    ui/app.py  (Streamlit, sin lógica fiscal)
                         │
                         ▼
        tp_domain.calculations.calculate_arm_length_range
                         │
        ┌────────────────┼─────────────────┐
        ▼                ▼                 ▼
  comparables.json  statistical_rules   sources.py
   (55, sintético)   (ES, DE, resto      (registro CERRADO,
                      NOT_MODELLED)        5 entradas hardcoded)
        └────────────────┼─────────────────┘
                         ▼
                  AnalysisResult
              (validator: toda cita ⊆ sources)
                    │            │
        ┌───────────┘            └────────────┐
        ▼                                     ▼
ExplanationRequest ──► Claude ──► Draft   pdf_report.render_report_bytes
   (proyección                     │       (secciones 1-3 + anexo fuentes,
    cerrada)                       ▼        siempre; sección 4 aditiva)
                            validate_draft
                                  │
                            AIExplanation | None
```

Comparado con la arquitectura objetivo que planteas, faltan exactamente **dos** cajas: `Legal / Tax Research Layer` y `Verified Evidence`. Todo lo demás existe y funciona.

**Evaluación de la pregunta de fondo: ¿la arquitectura actual permite evolucionar hacia el objetivo?**

Sí, y con menos fricción de la que cabría esperar. Tres razones concretas:

1. `sources.py` ya es un punto de inserción único. Todo el sistema resuelve fuentes por ahí. Sustituir un `Dict[str, Source]` estático por un almacén de evidencia con la misma interfaz `resolve(ids) -> List[...]` no toca ni el motor ni el PDF ni la capa IA.
2. `Source` es `frozen=True` y `ExplanationRequest.from_result` proyecta explícitamente qué campos salen. Añadir campos a `Source` **no** los expone al modelo por accidente: hay que editar `AllowedSource` a mano. La barrera es opt-in, que es la dirección correcta.
3. `AnalysisResult` es autosuficiente por diseño ("el PDF y la IA no consultan nada más"). Eso permite que la capa de evidencia se ejecute **antes** de construir el resultado y quede congelada dentro de él, que es justo el orden del diagrama objetivo.

El punto de fricción real: `Source` está congelado y tiene 7 campos, todos opcionales salvo tres. Enriquecerlo con jurisdicción, vigencia, ubicación tipada, fecha de consulta y extracto exigirá tocar los tests que lo construyen. Es trabajo mecánico, no rediseño. **[I]**

---

## 10. Arquitectura recomendada para la capa jurídica

### La decisión que lo condiciona todo

**Los MCP jurídicos son herramientas de Claude, no de TPIP.** Un `AnalysisResult` generado por `python -m streamlit run ui/app.py` no puede llamar a MCP-BOE. Hay dos caminos, y no son equivalentes.

**Camino A — Investigación en ejecución.** Reimplementar clientes Python contra las APIs del BOE, EUR-Lex y CENDOJ dentro de `infrastructure/legal/`, y consultarlas al generar cada análisis.

**Camino B — Evidencia curada y congelada.** Un almacén versionado de evidencia jurídica (`tp_domain/evidence/`), poblado **fuera de ejecución** mediante el flujo asistido por Claude con los MCP, y consumido por el motor de forma determinista y offline.

**Recomiendo B, sin ambigüedad.**

Motivos: (i) A duplica exactamente lo que el ecosistema ya resuelve, y lo duplica peor — el sondeo en vivo muestra que la búsqueda ciega del BOE devuelve normativa urbanística valenciana para una consulta de IS, y que CENDOJ ordena por fecha y no filtra por jurisdicción; envolver eso en Python no lo arregla; (ii) A mete latencia y dependencia de red en la ruta crítica de una demo de 5 minutos; (iii) A hace que dos ejecuciones del mismo análisis puedan dar informes distintos, que es lo contrario de lo que un informe de precios de transferencia necesita; (iv) B mantiene el principio que ya funciona en `sources.py` — registro cerrado, fallo ruidoso.

**Qué se sacrifica con B, dicho claramente:** la evidencia envejece. Un informe emitido en 2027 puede citar una redacción derogada en 2026. La mitigación no es técnica sino de proceso: `verified_at` obligatorio + `review_due` + un chequeo (tarea programada con MCP-BOE, fuera del producto) que avisa cuando una fuente supera su fecha de revisión. Eso convierte el envejecimiento en un dato visible del informe en lugar de un fallo silencioso — y, de hecho, **es una funcionalidad demostrable en entrevista**: "el informe te dice cuándo se verificó cada fuente y cuándo toca revisarla".

**Bajo qué criterio cambiaría la recomendación:** si TPIP dejara de ser una herramienta de análisis puntual y pasara a ser un servicio de vigilancia normativa continua, A sería lo correcto. Hoy no es eso.

### Forma concreta propuesta (no implementar todavía)

```
tp_domain/evidence/
├── registry.py         # resolve(ids) -> List[Evidence].  Reemplaza sources.py
├── models.py           # Evidence, Provision, Validity, Provenance
└── store/
    ├── es.yaml         # evidencia española
    ├── de.yaml         # evidencia alemana
    └── oecd.yaml       # Directrices
```

Modelo mínimo que cierra la cadena que pides:

```
Evidence
├── id, kind                          (ya existe en Source)
├── jurisdiction: str                 ← NUEVO. "ES" | "DE" | "EU" | "OECD"
├── provision: Provision              ← NUEVO. instrumento / artículo / apartado, tipado
├── validity: Validity                ← NUEVO. in_force_from, in_force_to|None,
│                                        consolidated_version
├── provenance: Provenance            ← NUEVO. locator_type (BOE_ID|CELEX|ELI|ECLI|URL|OFFLINE),
│                                        locator, retrieved_at, retrieved_by
├── verified_at: date                 ← NUEVO. cuándo lo revisó un humano
├── review_due: date|None             ← NUEVO
├── quote: str|None                   ← NUEVO. extracto literal breve de la disposición
├── citation, pinpoint, disclaimer    (ya existen)
└── research_note                     (ya existe)
```

Tres reglas de gobernanza que propongo fijar con el modelo:

1. **`locator_type = OFFLINE` es legal pero visible.** Las Directrices OCDE no tienen identificador público resoluble; que el informe diga "verificado contra PDF local, sin localizador público" es más honesto que dejar `official_ref` vacío como hoy.
2. **`quote` no viaja a Claude en la v1.** Añadirlo a `AllowedSource` es una decisión separada, con su propia versión de prompt y su propia revisión del validador. Ver §8.1.
3. **La selección de evidencia es determinista.** Un mapa `(jurisdiccion, tipo_operacion, regla) → [evidence_ids]`, que ya existe embrionariamente en `_RULE_SOURCES` de `statistical_rules.py`. La capa jurídica **localiza y aporta**; no decide.

### Sobre no duplicar la base de conocimiento del ecosistema

`Cerebros_Fiscales` es la fuente de doctrina verificada; `tp_domain/evidence/` es el subconjunto ejecutable, con la disposición exacta que sostiene una regla del motor. La relación correcta es **puntero, no copia**: `Evidence.research_note` sigue apuntando a la ficha, y la ficha al PDF primario. Lo que hoy rompe esa cadena es que `Cerebros_Fiscales` no está versionado y vive dentro de `tp_domain/`. Eso hay que resolverlo antes de construir encima (ver gap crítico #1).

---

## 11. Gaps críticos

Ordenados por lo que rompen, no por esfuerzo.

**#1 — La cadena de trazabilidad se rompe fuera de tu máquina.** `research_note` apunta a fichas del repo; las fichas del repo apuntan a `Cerebros_Fiscales/wiki/...`, que está gitignored. Quien clone el repo (un evaluador de Big Four, por ejemplo) no puede seguir ni una sola cita hasta su origen. Además el corpus vive físicamente en `tp_domain/`, contradiciendo tanto el README como la separación de capas del propio proyecto.

**#2 — Las dos fuentes más citadas son las menos verificables.** `oecd-tpg-2022-cap3` aparece en prácticamente todos los análisis (es la fuente por defecto de los factores de riesgo y de la regla `NOT_MODELLED`) y no tiene `official_ref`, ni URL, ni extracto. Igual `cap6`.

**#3 — La regla alemana, que es el diferencial del producto, descansa sobre una lectura declarada como no exhaustiva.** El disclaimer de `de-astg-1-3a` lo dice literalmente. No hay ninguna herramienta en el entorno que permita verificar el §1.3a AStG vigente. Es el punto donde un especialista alemán rompería la demo.

**#4 — Cero vigencia, cero fecha de consulta.** El sistema no sabe *cuándo* se verificó nada. Un informe emitido hoy y otro dentro de tres años son indistinguibles en cuanto a frescura de la evidencia.

**#5 — El enum `CASE_LAW` existe y está vacío.** Hay una ficha de doctrina TEAC en `documentation/tax-research/processes/`, con la distinción relevante ya hecha (solo RG 7833/2023 tiene eficacia vinculante general), y no llegó al registro. Es evidencia ya investigada que el motor no puede citar.

**#6 — `official_ref` es texto libre sin tipo.** Convive un `BOE-A-2014-12328` resoluble con un `AStG §1 Abs. 3a` que no es identificador de nada. Impide cualquier verificación automatizada futura.

**#7 — Las fichas de investigación no son parseables.** Sin frontmatter, frente a un corpus origen que sí lo tiene. Cualquier automatización futura (índice, chequeo de vigencia, generación del store) empieza por resolver esto.

**#8 — Zotero vacío.** Está declarado en el catálogo como "la capa de trazabilidad de fuentes" y tiene 0 ítems. O se puebla, o deja de contarse como capacidad.

**#9 — Cobertura del validador de referencias.** Las 5 familias de regex no cubren citas alemanas (`Tz.`, `Abs.`, `BMF-Schreiben`) ni normas citadas por nombre sin número. Si la evidencia se internacionaliza, el agujero crece. **[I]**

**#10 — Regla estadística de solo 2 jurisdicciones.** Correctamente gestionado (`NOT_MODELLED` no presume nada), pero limita el alcance demostrable. No es un defecto de diseño; es alcance.

---

## 12. Orden de implementación recomendado

Criterio: cada paso deja el sistema demostrable, y ninguno toca el motor hasta que la evidencia esté en su sitio. Sin estimaciones de tiempo — las que salen de una auditoría estática no valen nada.

**Paso 0 — Resolver la ubicación del corpus.** Decidir si `Cerebros_Fiscales` se saca de `tp_domain/` y se referencia como dependencia externa documentada, o si las 9 fichas de `documentation/tax-research/` se declaran autosuficientes y dejan de apuntar al corpus. No se puede construir evidencia trazable sobre una cadena que se rompe. Es una decisión tuya, no técnica.

**Paso 1 — Modelo `Evidence` y almacén, sin cambiar comportamiento.** Definir el modelo de §10, migrar las 5 fuentes actuales rellenando los campos nuevos con lo que ya se sabe, y dejar `resolve()` con la misma firma. Al terminar, los 144 tests deben pasar sin tocarse salvo donde construyan `Source` directamente. Es el paso que compra todo lo demás.

**Paso 2 — Verificar y datar las 5 fuentes existentes.** Con los MCP, en sesión asistida, una por una: BOE para el Art. 18.4 LIS (id ya conocido, `search_law_articles` funciona bien); EUR-Lex para lo que aplique; OCDE queda como `OFFLINE` con extracto del PDF local; AStG es el caso difícil — **antes de dar el §1.3a por bueno hay que resolver cómo verificarlo**, y esa respuesta condiciona si la regla alemana sigue siendo el diferencial de la demo. Rellenar `verified_at`, `quote` y `provenance`. Cierra los gaps #2, #3, #4 y #6.

**Paso 3 — Imprimir la trazabilidad en el informe.** Anexo de fuentes con jurisdicción, vigencia, localizador y fecha de verificación. Es el paso de mayor rendimiento por esfuerzo en una demo: convierte trabajo invisible en pantalla visible, y es la respuesta directa a "¿de dónde sale esto?" en una entrevista.

**Paso 4 — Incorporar la doctrina TEAC como evidencia citable.** `CASE_LAW` deja de estar vacío; la ficha ya está escrita, y la distinción sobre eficacia vinculante ya está hecha. Requiere decidir a qué afirmación del motor se engancha — probablemente un `RiskFactor` cualitativo, no una regla de cálculo.

**Paso 5 — Frontmatter en las fichas de investigación.** Alinear con el esquema del corpus origen. Habilita el paso 6.

**Paso 6 — Chequeo de vigencia fuera del producto.** Tarea programada + MCP-BOE que revise `review_due` y avise. Fuera del runtime, respetando el Camino B.

**Fuera de esta fase, deliberadamente:**

- Validación semántica de la contradicción entre prosa y veredicto. Ya está registrada como límite conocido con un test que la fija. Perseguirla ahora daría falsa seguridad, que es peor que el límite documentado.
- Inyectar texto normativo en el prompt. Decisión separada, con versión de prompt propia. Ver §8.1.
- Capa API / FastAPI. Sigue sin haber un segundo consumidor.
- Ampliar jurisdicciones. Sin evidencia verificable para las dos actuales, añadir una tercera multiplica el problema.

---

## Anexo — método y límites de esta auditoría

Verificado leyendo código: estructura completa del árbol, `ai/schemas.py`, `ai/validators.py`, `ai/claude_client.py`, `ai/prompts/explain_analysis_v1.md`, `tp_domain/models.py`, `tp_domain/sources.py`, `tp_domain/rules/statistical_rules.py`, `tp_domain/calculations/arm_length_range.py`, secciones relevantes de `infrastructure/report/pdf_report.py` y `ui/app.py`, `documentation/tax-research/README.md` y cabeceras de las 9 fichas, `documentation/analisis-cerebros-fiscales.md`, `documentation/auditoria-estado-2026-08-09.md`, `Catalogo_Herramientas_IA_Daru.md`, `.gitignore`, `pyproject.toml`, `requirements.txt`, `.env.example`.

Verificado ejecutando: `git ls-files`, `git status` (limpio), `git log`, recuentos de líneas y de funciones de test, sondeos en vivo de MCP-BOE (2 llamadas), EUR-Lex (1), CENDOJ (1) y Zotero (1).

**No verificado:** ejecución de la suite de tests (fallo de instalación de dependencias en el sandbox); Firecrawl; comportamiento real de la API de Anthropic; contenido de los 117 PDFs del corpus; contenido íntegro de las 116 fichas de `wiki/` (leída la cabecera de `sub_tp/`, 9 fichas).
