# Especificación del modelo de datos — Fase 1

Fecha: 2026-08-09
Estado: **propuesta para validar. Sin implementar.**
Base: revisión de arquitectura sobre `154dd0b`.
Decisión de alcance confirmada: **Fase 1 cubre intangibles/cánones. Servicios intragrupo y demás tipos quedan excluidos temporalmente.**

---

## 0. Los cuatro principios que fijan el diseño

1. **El rango es un hecho de mercado; el veredicto es jurisdiccional.** Un benchmark no tiene nacionalidad. Lo que cambia por país es qué consecuencia tiene caer fuera de él. El modelo separa las dos cosas.
2. **Nada se afirma sin fuente identificable.** Toda conclusión y todo factor de riesgo apunta a una entrada de un registro de fuentes cerrado. La IA cita de ese registro o no cita.
3. **El informe debe generarse sin IA.** Sin clave de API, sin red, el PDF sale completo con la redacción determinista. La IA añade una sección; no sostiene ninguna.
4. **Un análisis emitido hoy debe reproducirse en 2027.** Versión de motor y versión de dataset viajan dentro del resultado.

---

## 1. `Transaction` — entrada

| Campo | Tipo | Cambio | Motivo |
|---|---|---|---|
| `id` | `str` | **Nuevo, autogenerado** | Hoy es `Optional` y acaba en `"unknown"` impreso en el informe |
| `description` | `str` | — | |
| `payer_country` | `CountryCode` | **Renombrado** desde `from_country` | `from`/`to` no dice quién paga. En un canon, quién deduce y quién percibe determina qué administración revisa qué |
| `recipient_country` | `CountryCode` | **Renombrado** desde `to_country` | ídem |
| `transaction_type` | `TransactionType` | **Validador nuevo** | En Fase 1 solo se acepta `ROYALTY`. El resto lanza error explícito de "no soportado en esta versión", no un resultado silencioso y erróneo |
| `industry` | `Industry` (enum) | **De `str` a enum** | Hoy acepta `"biotech"` y devuelve un resultado vacío. Un enum lo convierte en error de validación |
| `amount_eur` | `Decimal` | **De `float` a `Decimal`** | Importes monetarios que se imprimen en un informe. `float` da 999999.9999999999 |
| `rate_percent` | `Decimal` | **De `float` a `Decimal`** | ídem |
| `effective_date` | `date` | **De `datetime` y sin `default_factory`** | Elimina el no determinismo del filtro de antigüedad. Que la fecha sea obligatoria es correcto: no existe un análisis "de hoy por defecto" |
| `method_hint` | `TPMethod \| None` | — | |

**No se añade ahora** (aditivo, sin ruptura, cuando toque): `turnover_eur` (umbrales del RIS, Fase 2), `tested_party` (TNMM real, Fase 2), `currency` (Fase 2), campos funcionales de comparabilidad (Fase 2B).

**Coste del enum de industria:** el test `test_filter_unknown_industry_returns_empty` deja de poder construir una transacción "biotech" y pasa a ser un test de validación. Es un cambio de test, no una pérdida de cobertura.

---

## 2. Objetos nuevos

### 2.1 `Source` — registro de fuentes

La pieza que hace posible la capa IA sin infringir §3.2.

| Campo | Tipo | Ejemplo |
|---|---|---|
| `id` | `str` | `"es-lis-art18-4"` |
| `kind` | `SourceKind` | `LEGISLATION` · `GUIDELINES` · `CASE_LAW` · `DATASET` |
| `citation` | `str` | `"Ley 27/2014 (LIS), Art. 18.4"` |
| `pinpoint` | `str \| None` | `"§1.3a, párrafo segundo"` |
| `official_ref` | `str \| None` | `"BOE-A-2014-12328"` |
| `research_note` | `str \| None` | `"documentation/tax-research/jurisdictions/spain/art18-lis-operaciones-vinculadas.md"` |
| `disclaimer` | `str \| None` | Para el dataset sintético |

Vive en `tp_domain/sources.py` como diccionario de constantes, no en JSON: son pocas, estables y se referencian desde código.

**Registro mínimo de Fase 1 — cinco entradas:**

| id | Qué justifica |
|---|---|
| `es-lis-art18-4` | Que España no impone regla estadística |
| `de-astg-1-3a` | Rango intercuartílico obligatorio y ajuste a mediana |
| `oecd-tpg-2022-cap3` | Concepto de rango de plena competencia y uso de percentiles |
| `tpip-dataset-v1` | **El dataset sintético.** Con `disclaimer` obligatorio |
| `oecd-tpg-2022-cap6` | Intangibles: marco aplicable al tipo de operación |

Sobre `tpip-dataset-v1`: los comparables son sintéticos y **eso debe aparecer en la portada del informe**, no en una nota al pie. Un estudio de benchmarking que no revela el origen de sus comparables no vale nada, y en un portfolio la omisión se lee como intento de aparentar datos reales.

### 2.2 `RejectedComparable` — traza del filtro

| Campo | Tipo |
|---|---|
| `comparable_id` | `str` |
| `reason` | `RejectionReason` (`INDUSTRY_MISMATCH` · `STALE_YEAR` · `NO_RATE_DATA`) |
| `detail` | `str` |

El filtro ya conoce el motivo de cada descarte; hoy lo tira. Registrarlo cuesta casi nada y produce el anexo de comparables aceptados/rechazados, que es lo que distingue un estudio de benchmarking de una media.

### 2.3 `JurisdictionAssessment` — un veredicto por jurisdicción implicada

El núcleo del diseño. Una operación España → Alemania genera **dos** evaluaciones: cada administración aplica su regla a su lado.

| Campo | Tipo | Nota |
|---|---|---|
| `country` | `CountryCode` | |
| `role` | `PayerRole` | `PAYER` / `RECIPIENT` |
| `range_rule` | `RangeRule` | `NO_STATUTORY_RULE` (ES) · `INTERQUARTILE_MEDIAN_ADJUSTMENT` (DE) |
| `position` | `RangePosition` | `BELOW_P10` · `P10_TO_P25` · `WITHIN_IQR` · `P75_TO_P90` · `ABOVE_P90` |
| `defensibility_level` | `DefensibilityLevel` | `STRONG` / `MODERATE` / `WEAK` |
| `defensibility_score` | `int` | Derivado de `position` por tabla documentada, no por multiplicadores mágicos |
| `adjusted_rate` | `Decimal \| None` | Solo si la regla impone ajuste. En DE = mediana |
| `consequence` | `str` | Redacción determinista |
| `source_ids` | `list[str]` | |

Esta estructura absorbe la Fase 2 sin reformarse: la retención en fuente y el tipo efectivo son campos que se añaden aquí, uno por jurisdicción.

### 2.4 `RiskFactor` — con fuente y severidad

| Campo | Tipo |
|---|---|
| `code` | `RiskCode` (`RATE_ABOVE_RANGE` · `THIN_SAMPLE` · …) |
| `severity` | `Severity` (`INFO` / `WARNING` / `CRITICAL`) |
| `message` | `str` |
| `source_ids` | `list[str]` |

Hoy son strings sueltos. Con código y severidad, el PDF los ordena y la IA los explica sin reinterpretarlos.

### 2.5 `AIExplanation` — la IA como campo, no como narrador

| Campo | Tipo |
|---|---|
| `text` | `str` |
| `prompt_version` | `str` (`"explain_analysis_v1"`) |
| `model` | `str` |
| `generated_at` | `datetime` |
| `sources_cited` | `list[str]` |

`sources_cited` se **valida contra el registro del propio resultado**. Si la IA cita algo que no está, el objeto no se construye. La regla de gobernanza deja de ser una instrucción en un prompt y pasa a ser una restricción del modelo. Es la diferencia entre confiar y verificar.

---

## 3. `AnalysisResult` — salida

```
AnalysisResult
├── analysis_id, created_at
├── engine_version, dataset_version        # reproducibilidad
├── transaction: Transaction               # embebida: el informe imprime la entrada
├── method_applied: TPMethod               # derivado del tipo, no constante
├── method_rationale: str
├── benchmark: BenchmarkRange
│     p10, p25, p50, p75, p90              # P10/P90 reales, no p25*0,7
│     count_accepted
│     percentile_method: str = "linear"    # decisión metodológica explícita
├── comparables_accepted: list[Comparable] # COMPLETA, sin truncar
├── comparables_rejected: list[RejectedComparable]
├── assessments: list[JurisdictionAssessment]
├── risk_factors: list[RiskFactor]
├── sources: list[Source]                  # registro cerrado del análisis
├── conclusion: str                        # determinista, siempre presente
└── ai_explanation: AIExplanation | None    # opcional, aditiva
```

Cambios frente al modelo actual, y por qué:

| Cambio | Motivo |
|---|---|
| `comparables_used[:5]` → `comparables_accepted` completa | El truncado era una decisión de UI dentro del dominio. El anexo del informe necesita el conjunto entero |
| `transaction_id: str` → `transaction: Transaction` | El resultado se serializa hacia la IA y hacia el PDF; debe bastarse solo |
| `defensibility_*` sube a `JurisdictionAssessment` | Porque el veredicto depende del país, que es justo lo que hoy no se usa |
| `benchmark_range` → `benchmark` con P10/P90 y método | Hace explicable el tramo intermedio del score |
| `risk_factors: list[str]` → `list[RiskFactor]` | Severidad y trazabilidad |
| `+ sources`, `+ ai_explanation` | Habilitan IA y PDF sin reformar nada después |
| `+ engine_version`, `+ dataset_version` | Reproducibilidad |

**El score se mantiene**, pero derivado de `position` mediante tabla documentada:

| `position` | Nivel | Score |
|---|---|---|
| `WITHIN_IQR` | STRONG | 9 |
| `P10_TO_P25` / `P75_TO_P90` | MODERATE | 6 |
| `BELOW_P10` / `ABOVE_P90` | WEAK | 2 |

Son los mismos tres valores de hoy, pero con una frontera que existe de verdad (P10 y P90 calculados) y una regla que se puede enunciar en una frase. Mantiene `calculate_defensibility_score()` de las instrucciones §7 y el gancho de la demo, y elimina el "de dónde sale ese 0,7".

---

## 4. Esquema de datos mínimo

| Artefacto | Cambio en Fase 1 |
|---|---|
| `tp_domain/comparables.json` | **Ninguno.** El esquema actual basta para cánones. Solo se pasa a consumir `_metadata.version` como `dataset_version` |
| `tp_domain/sources.py` | **Nuevo.** 5 entradas |
| `tp_domain/rules/statistical_rules.py` | **Nuevo.** Enum `RangeRule` + mapa `{"ES": NO_STATUTORY_RULE, "DE": INTERQUARTILE_MEDIAN_ADJUSTMENT}` |
| Base de datos | **Ninguna.** SQLite sigue sin justificarse: no hay multiusuario, ni histórico, ni concurrencia |
| Esquemas de API | **Ninguno.** Sin consumidor distinto de Streamlit, FastAPI es sobreingeniería |

El dataset no se toca. Merece subrayarse: todo lo anterior se consigue sin ampliar los datos, solo estructurando mejor lo que el motor ya calcula y descarta.

---

## 5. Decisiones que necesito de ti

1. **Corredor de la demo.** Sigue abierta desde la revisión anterior: el §1.3a AStG no aplica a Luxemburgo, así que el caso España → Luxemburgo no puede enseñar la comparación jurisdiccional. Recomiendo cambiarlo a **España → Alemania**. Se pierde Luxemburgo como guiño a la estructuración de intangibles; se gana que la pantalla que vende el proyecto funcione.
2. **`Decimal` en importes y tipos.** Correcto para algo que se imprime, pero contamina las comparaciones con el dataset y con numpy, que trabaja en `float`. Alternativa más barata: mantener `float` en el dominio y redondear en la capa de presentación. Recomiendo `Decimal` solo en `amount_eur` y `rate_percent`, dejando los percentiles en `float` — la frontera de conversión queda en un único sitio.
3. **Bloqueo de tipos no soportados.** Confirmo que `transaction_type != ROYALTY` debe lanzar error de validación en el modelo, no solo desaparecer del desplegable de la UI. Es más ruidoso y es lo correcto: impide que un test o un script futuro use una rama que sabemos incorrecta.
