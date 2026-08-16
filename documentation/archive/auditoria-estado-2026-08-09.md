# Auditoría de estado — TPIP

Fecha: 2026-08-09
Alcance: estado del repositorio antes de continuar desarrollo. Sin cambios de código.
Método: lectura completa del árbol de ficheros, historial git y documentación; ejecución real de la suite de tests en sandbox Linux.

---

## 1. Estado del repositorio

| Dato | Valor |
|---|---|
| Commits | 12, rama única `main` |
| **Commits locales sin pushear** | **4** (`0978a6b`, `d6a5a78`, `1b1a625`, `95c250a`) |
| Código Python propio | ~600 líneas (modelos 176, UI 217, cálculo 210) |
| Tests | 33, **todos pasan** (verificado, 0,92 s) |
| CI | GitHub Actions, Python 3.9, activo |
| Ficheros trackeados | 282, de los cuales **115 son PDF** del corpus |
| Peso del repo | 193 MB de corpus + 148 MB en `.git` |
| Sin trackear | `AGENTS.md`, `Catalogo_Herramientas_IA_Daru.md`, `documentation/entrevista-definicion-tpip.md`; `LICENSE` modificado |

Directorios `api/`, `ai/`, `infrastructure/` existen pero están **vacíos** (solo `__init__.py`). No hay `database/`, `tp_domain/rules/` ni `tp_domain/validators/`.

---

## 2. Arquitectura existente

Flujo real hoy:

```
ui/app.py  →  tp_domain.calculations.arm_length_range  →  tp_domain/comparables.json
                        ↓
              tp_domain/models.py (Pydantic v2)
```

**Lo que está bien:** la UI no calcula nada. Construye un `Transaction`, llama a `calculate_arm_length_range()` y pinta el `AnalysisResult`. La regla nuclear del proyecto (§3.1, lógica fiscal como fuente de verdad) se respeta hoy.

**Lo que no existe:** capa API y capa IA. No es un defecto: meter FastAPI entre Streamlit y el dominio con un solo consumidor sería sobreingeniería en Fase 1. El riesgo a vigilar no es la ausencia de API, es que empiece a colarse lógica en `app.py`.

**Desviaciones respecto a las instrucciones del proyecto**, ambas ya registradas y correctas:

- Streamlit en lugar de React/TS/Tailwind (registrada en §8bis-D de la entrevista).
- `models.py` como módulo plano en vez de `models/` como paquete. Irrelevante a esta escala.

---

## 3. Funcionalidades implementadas

- Modelos de dominio: `Transaction`, `Comparable`, `BenchmarkRange`, `AnalysisResult`, enums `TransactionType` / `TPMethod` / `DefensibilityLevel`. Validación Pydantic activa (rate 0-100, importe > 0).
- Dataset sintético: 55 comparables, 3 industrias (pharma 18, software 19, manufacturing 18), 5 países, años 2024-2025, con bloque `_metadata` que documenta la calibración (seed 3870).
- Filtrado de comparables por industria (obligatorio), antigüedad (≥ año-2) y disponibilidad de dato según tipo de operación.
- Percentiles P25/P50/P75 redondeados a 2 decimales.
- Score de defensibilidad 1-10 y nivel STRONG/MODERATE/WEAK.
- Factores de riesgo y conclusión textual, distinguiendo por encima / por debajo del rango.
- Rama sin comparables que devuelve `None` limpio en lugar de excepción.
- UI Streamlit completa: formulario, métricas, rango, semáforo, factores de riesgo, conclusión, comparables usados.
- Suite de 33 tests que fija percentiles, filtrado, scoring, casos borde y los 3 escenarios de demo.

---

## 4. Funcionalidades pendientes del MVP

Contrastado contra Fase 1 de las instrucciones y contra la entrevista de definición:

| Pendiente | Origen del requisito | Estado |
|---|---|---|
| **Informe PDF profesional** | Instrucciones §5, output explícito del MVP | No existe |
| **Explicación IA** | Instrucciones §5 y §10; `ai/prompts/` versionado | `ai/` vacío |
| **TNMM como método del MVP** | Entrevista §2 ("solo TNMM") | El motor devuelve siempre `TPMethod.CUP` |
| **Reglas por jurisdicción (ES real + UE simplificado)** | Entrevista §2 | `tp_domain/rules/` no existe; país no afecta al cálculo |
| Industria "services" | Instrucciones §8 | Dataset tiene 3 industrias, no 4 |
| Caso de ejemplo cargable en un clic | Entrevista §8bis-A | No implementado |
| Persistencia SQLite | Instrucciones §12 | No existe — **y probablemente no hace falta en Fase 1** |

---

## 5. Decisiones técnicas ya tomadas (no se reabren)

Streamlit como frontend · Pydantic v2 · JSON como almacén de comparables · dataset sintético calibrado con seed documentado · repo público desde el día uno · tests como red de seguridad previa a la capa de jurisdicción · corpus fiscal reutilizado, no duplicado.

Ninguna de ellas presenta un problema que justifique revisarla ahora.

---

## 6. Coherencia entre arquitectura y objetivos del MVP

Coherencia general buena. Tres grietas concretas, en orden de visibilidad para un evaluador:

**a) El caso keynote no produce el resultado declarado.**
La entrevista (§8bis-B) describe la demo como royalty del 12 % ES→LU en software, benchmark 5-8 %, veredicto *fuera de rango*. El motor real da para software P25 8,35 % – P75 11,2 %, y un 12 % cae en score 6 → **MODERATE**, no en riesgo alto. El caso de demostración documentado y el motor dicen cosas distintas. Hay que reconciliarlo: o se recalibra el dataset de software, o se actualiza el caso.

**b) Método: `CUP` constante frente a la decisión "solo TNMM".**
`method_recommended` está fijado a CUP en las cuatro ramas de retorno, y hay un test que lo pinta como comportamiento deseado. Además, para royalties el motor compara `royalty_rate` (lógica CUP de facto) y para `management_fee` compara `operating_margin` (lógica TNMM de facto). El código hace lo razonable; lo que está mal es la etiqueta y su desajuste con la decisión de producto escrita.

**c) La jurisdicción es decorativa.**
`from_country` y `to_country` se recogen, se validan y no influyen en absolutamente nada. Es la grieta más cara en términos de portfolio: es precisamente donde vive el conocimiento diferencial (§1.3a AStG frente al art. 18.4 LIS, ya analizado en `analisis-cerebros-fiscales.md`) y hoy la herramienta no lo usa.

Añadido menor: el tramo MODERATE se aproxima con `p25*0,7` y `p75*1,3` y el comentario lo llama "rough P10-P90". No tiene anclaje normativo ni estadístico, y con P25=8,35 el suelo queda en 5,85 %, que no es el P10 de nada. Si alguien pregunta de dónde sale, no hay respuesta defendible. Calcular P10/P90 reales sobre la muestra filtrada cuesta cuatro líneas.

---

## 7. Riesgos técnicos

1. **Corpus de 193 MB dentro de `tp_domain/` y ya committeado** (`95c250a`). Contamina el paquete de dominio, hace el clone impracticable y ata el historial a 115 PDF. **Todavía no está pusheado: es reversible ahora y casi irreversible después del push.** Fichero mayor: 35 MB.
2. Dataset rígido por diseño: tres tests fijan P25/P75 exactos por industria. Cualquier recalibración del dataset rompe la suite. Es intencional, pero implica que corregir el caso keynote (§6.a) toca tests.
3. `effective_date` con `default_factory=datetime.now` en el modelo de dominio: introduce no determinismo en el filtro de antigüedad. Los tests lo esquivan con fecha fija; el código de producción no.
4. `class Config` de Pydantic v1 en los cuatro modelos: 4 warnings de deprecación, ruptura en Pydantic v3.
5. El CI no ejecuta `pip install -e .` pese a que el README lo marca como obligatorio. Funciona por casualidad (rootdir), no por diseño.
6. `.git` con 4 objetos basura y 7,2 MB de garbage.

## 8. Riesgos de producto

1. **Copyright.** Repo público, con nombre y apellidos, dirigido a recruiters de Big Four, que contiene PDFs de notas de EY, KPMG, Deloitte, Garrigues y Uría, doctrina de revista y las Directrices OCDE de Precios de Transferencia 2022 (publicación de pago). No es un problema técnico y es, ahora mismo, el riesgo mayor del proyecto. La legislación (BOE, EUR-Lex) no plantea problema; el resto sí. No soy abogado y esto no es asesoramiento legal, pero la exposición es evidente y la decisión no admite demora porque basta un `git push` para consolidarla.
2. El "pendiente 9" de la entrevista sigue abierto: qué resuelve TPIP frente a lo que existe. Es la primera pregunta de cualquier entrevistador y no hay respuesta escrita.
3. La demo actual dura menos de un minuto y termina en una pantalla de métricas. Sin informe ni explicación no hay entregable profesional, que es justo el criterio de "Demo First" de las instrucciones.
4. Riesgo de deriva: el corpus recién incorporado empuja hacia el Research Companion (Fase 3) antes de haber cerrado la Fase 1.

---

## 9. Uso de MCPs, plugins y skills del catálogo

Criterio aplicado: usar lo mínimo que aporte valor verificable, no activar por activar.

**Útil ahora (poco):**

- **MCP-BOE** — una sola vez, cuando se codifiquen los umbrales del art. 18 LIS en `tp_domain/rules/`, para verificar el texto vigente en fuente primaria en lugar de citarlo de memoria o de ficha. Aporta trazabilidad real al informe.
- **Skill `pdf`** — cuando toque construir el informe. No antes.
- **Skill `humanizar-textos`** — ya es el estándar por defecto de todo texto redactado.
- **Subagentes** — solo si se construye el parser del wiki, para no meter 114 fichas en el contexto principal.

**Útil más adelante:** EUR-Lex y CENDOJ en Fase 2/3 (retenciones sobre cánones en los 10 CDI, doctrina TEAC como factor de riesgo cualitativo).

**Descartado ahora:** Zotero (el corpus ya está en markdown estructurado, sería duplicar), Firecrawl (no hay fuente web sin API que haga falta), frontend-design (aporta poco sobre Streamlit), skill-creator (no hay flujo repetido todavía), montar un RAG sobre el corpus (es Fase 3 y consumiría el mes).

---

## 10. Próximo paso recomendado

**Orden propuesto, con el porqué:**

**Paso 0 — bloqueante, hoy: decidir qué se hace con el corpus.** Sacarlo de `tp_domain/`, reescribir el commit `95c250a` antes de pushear y dejar en el repo solo lo derivado (un `corpus_index.json` con metadatos y citas, sin PDFs de terceros). Es la única tarea del proyecto cuyo coste se multiplica por esperar.

**Paso 1 — medio día: reconciliar caso keynote y método.** Ajustar `method_recommended` para que se derive del tipo de operación en lugar de ser constante, y alinear el caso de demostración documentado con lo que el motor produce de verdad. Elimina la incoherencia más fácil de detectar en una entrevista.

**Paso 2 — resto de la semana: cerrar el output de Fase 1.** Explicación IA (`ai/prompts/explain_analysis_v1.md`, sobre resultado ya calculado) + informe PDF. Es lo que convierte una pantalla de métricas en un entregable profesional y lo que la Fase 1 exige literalmente.

**Trade-off de la alternativa descartada:** ir primero a `tp_domain/rules/` (reglas ES/DE) daría antes el diferencial fiscal, que es lo más impresionante del proyecto. Se descarta porque se llegaría a la semana 2 con un motor más listo pero sin nada exportable, y la Fase 1 quedaría declarada "hecha" sin PDF ni explicación, que son output explícito del roadmap. Este criterio cambiaría si la fecha de la demo se adelantara y hubiera que enseñar profundidad fiscal antes que entregable.
