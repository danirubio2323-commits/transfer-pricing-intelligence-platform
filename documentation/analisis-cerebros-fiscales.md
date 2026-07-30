# Análisis de Cerebros Fiscales para integración en TPIP

Fecha: 30 julio 2026
Fuente analizada: `C:\Users\LEINAD\Desktop\Cerebros_Fiscales`

---

## Conclusión previa (lo que condiciona todo lo demás)

El corpus **no contiene ni un solo comparable numérico**. Ni un rango de royalty por industria, ni un margen sectorial, ni una base de datos de operaciones no controladas.

Lo verifiqué con búsqueda dirigida sobre las 114 fichas: los términos `intercuartil`, `percentil`, `mediana` y `benchmark` aparecen 7 veces en total, y las 7 son **enunciados de la regla estadística**, no datos. Los 11 ficheros JSON son configuración de Obsidian y de Claude, cero bytes de datos.

Esto no invalida el corpus. Cambia dónde encaja. El corpus alimenta la **capa de reglas** de TPIP (validadores, selección de método, scoring de riesgo, obligaciones documentales), no la capa de datos. Los comparables de la Fase 1 siguen teniendo que ser sintéticos, tal como ya anticipaban las instrucciones del proyecto.

Y ahí está lo interesante: la capa de reglas es lo que separa a TPIP de una hoja de Excel con percentiles. Cualquiera calcula un P25. Muy pocos conectan el resultado con el §1.3a AStG o con el régimen sancionador del Art. 18.13 LIS.

---

## 1. Estructura actual

253 archivos, 193 MB, tres capas bien separadas siguiendo el patrón Karpathy que documenta el `CLAUDE.md` del propio repositorio.

| Capa | Contenido | Volumen |
|---|---|---|
| `raw/` | Fuentes inmutables en PDF, 7 carpetas temáticas | 117 PDF |
| `wiki/` | Fichas técnico-jurídicas en Markdown | 114 fichas |
| Config | Obsidian y Claude | 11 JSON |

Reparto de fichas por sub-cerebro:

| Sub-cerebro | Fichas | Relevancia para TPIP |
|---|---|---|
| `matriz/` | 56 | Media (10 CDI España, retenciones en fuente) |
| `sub_is/` | 33 | Alta (Pilar Dos, EP, híbridos) |
| `concierto_foral/` | 14 | Baja para MVP |
| `sub_tp/` | 9 | Máxima (núcleo del motor) |
| `sub_irpf/` | 2 | Nula |

### Calidad estructural: excelente

Esto es lo que hace el corpus explotable por software, y es mérito del diseño previo:

- **100% del frontmatter YAML parsea sin errores.** 114 de 114. No hay que limpiar nada.
- **501 enlaces cruzados** declarados en frontmatter, 4,4 por ficha de media. Es un grafo de dependencias ya construido.
- **Campos estables**: `titulo` (114/114), `enlaces` (113), `fuente_raw` (111), `origen` (109), `fecha` (104).
- **Headings normalizados**: `## Hechos` (100), `## Doctrina aplicada` (102), `## Conclusión jurídica` (110), `### ⚠️ Conflicto Doctrinal / Evolución de Criterio` (16).

Traducción práctica: un parser de 40 líneas con `pyyaml` extrae todo el corpus a JSON estructurado. No hay fase de limpieza.

### Lo que sí hay que vigilar

Tres fichas sin `fuente_raw`, diez sin `fecha`. Y hay contaminación de alcance: varias fichas de `sub_is` y `concierto_foral` orientan la conclusión hacia "el corredor pyme Gipuzkoa-Francia", un caso de estudio territorial. El propio `CLAUDE.md` marca eso como desviación detectada en la auditoría de julio de 2026. Para TPIP, que es de propósito general, esas conclusiones hay que leerlas con filtro.

---

## 2. Contenido identificado y aprovechable

### Tipo 1: reglas estadísticas del rango de plena competencia (3 fuentes, alto valor)

Lo más directamente convertible en código, porque son reglas deterministas.

- **§1.3a AStG (Alemania)**: si tras los ajustes persisten diferencias de comparabilidad, el rango se estrecha eliminando el cuartil inferior y el superior. Si el valor declarado cae fuera, se aplica **la mediana**, salvo prueba en contrario del contribuyente. Es obligatorio y está vigente.
- **Art. 12 COM(2023) 529 (UE)**: habría impuesto rango intercuartílico (P25-P75) y ajuste obligatorio a mediana. **Retirada el 21 octubre 2025.** Sin vigencia.
- **Art. 18.4 LIS (España)**: no contiene regla estadística alguna. Solo exige aplicar uno de los 5 métodos y elegir "el más adecuado".

Esa divergencia es explotable como funcionalidad. Un mismo rate del 12% con benchmark 4,5-8,2% produce consecuencias distintas según jurisdicción: en Alemania el ajuste a mediana es automático, en España depende de la valoración caso por caso de la Inspección. Un motor que modele esa diferencia enseña criterio, no aritmética.

### Tipo 2: umbrales y datos duros (directamente parametrizables)

| Dato | Valor | Fuente en el corpus |
|---|---|---|
| Perímetro de vinculación | ≥25% participación, 8 supuestos | Art. 18.2 LIS |
| Documentación simplificada | 45 M€ cifra de negocios | Art. 18 LIS |
| CbCR / Pilar Dos | 750 M€ en 2 de 4 ejercicios | DAC4, Ley 7/2024 |
| Tipo mínimo global | 15% | Pilar Dos / GloBE |
| De minimis GloBE | 10 M€ ingresos / 1 M€ beneficio | Reglas modelo |
| Sanción por dato omitido | 1.000 € / 10.000 € por conjunto | Art. 18.13 LIS |
| Sanción por corrección valorativa | 15% sobre el importe corregido | Art. 18.13 LIS |

### Tipo 3: marcos metodológicos OCDE (convertibles en cuestionario)

De la ficha de Directrices 2022, que cubre los capítulos I, VI y VII:

- Marco de 6 pasos sobre riesgo (cap. I, párr. 1.71-1.103), base técnica de la doctrina *cash box*
- Marco DEMPE de 6 pasos para intangibles (cap. VI, párr. 6.34) y las "funciones importantes" del párr. 6.56
- *Benefits test* de servicios intragrupo (cap. VII, párr. 7.6) y exclusión de *shareholder activities* (párr. 7.9-7.10)

Los capítulos II-V y VIII-X están sin fichar. Para el MVP no hace falta más.

### Tipo 4: los 5 métodos TP sin jerarquía legal

Precio libre comparable, coste incrementado, precio de reventa, distribución del resultado, margen neto operacional. La elección atiende a naturaleza de la operación, disponibilidad de información fiable y grado de comparabilidad (*best method rule*, no jerarquía formal).

Coincide exactamente con el enum `TPMethod` que ya existe en `tp_domain/models.py`.

### Tipo 5: doctrina TEAC (3 resoluciones)

Bilateralidad y simultaneidad de procedimientos (RG 5109/2016), ajustes y enriquecimiento injusto (RG 5972/2021), servicios intragrupo con doble vinculación (RG 7833/2023). Son criterio administrativo español aplicable, útil como factor de riesgo cualitativo.

### Tipo 6: red de CDI (10 convenios)

Alemania, Brasil, China, EE.UU., Francia, Luxemburgo, México, Países Bajos, Reino Unido, Suiza. Contienen tipos de retención en fuente sobre cánones, que es materia prima directa de la Fase 2 (Tax Impact Modeler). No los he extraído todavía: requieren lectura ficha por ficha.

### Lo que NO hay

- Comparables numéricos por industria: **cero**
- Casos reales anonimizados con cifras: **cero**
- Lógica GloBE computable (cálculo de ETR, top-up tax): solo descriptiva, no algorítmica

---

## 3. Propuesta de integración en TPIP

Cuatro archivos nuevos, en orden de valor por hora invertida.

### `tp_domain/rules/statistical_rules.py`

Formato: Python con enums, no JSON. La regla del rango es lógica ejecutable con ramas por jurisdicción, no una tabla.

```python
class RangeRule(str, Enum):
    INTERQUARTILE_MEDIAN_ADJUSTMENT = "iqr_median"   # §1.3a AStG (DE)
    BEST_METHOD_NO_STATISTICAL_RULE = "best_method"  # Art. 18.4 LIS (ES)

JURISDICTION_RANGE_RULES = {
    "DE": RangeRule.INTERQUARTILE_MEDIAN_ADJUSTMENT,
    "ES": RangeRule.BEST_METHOD_NO_STATISTICAL_RULE,
}
```

Uso en `calculate_arm_length_range()`: si la jurisdicción impone ajuste a mediana y el rate cae fuera del rango, el motor devuelve el valor de ajuste además del veredicto.

### `tp_domain/rules/thresholds.py`

Formato: constantes Python con la fuente legal en el docstring. Son siete valores, no justifica base de datos.

Uso en `calculate_defensibility_score()`: la exposición sancionadora entra como factor. Un rate fuera de rango con documentación incompleta expone a 15% sobre la corrección más multas fijas, y eso debería mover el score, no solo aparecer en el texto.

### `infrastructure/wiki_parser.py`

Formato: script de extracción. Lee las 114 fichas, parsea frontmatter y headings normalizados, vuelca a `infrastructure/data/corpus_index.json`.

Es lo más barato de todo el paquete, porque el corpus ya está limpio. Sirve para citar fuente legal en los informes: cada conclusión del PDF final puede llevar su referencia a ficha y a `fuente_raw`.

### `ai/prompts/explain_analysis_v1.md`

El corpus es el contexto documental que la IA usa para explicar, respetando la regla de gobernanza del proyecto: la IA explica un resultado ya calculado, nunca lo calcula. El prompt recibe el resultado del motor más los extractos de ficha relevantes.

### Conexión con la app

En `ui/app.py`, donde hoy hay un resultado hardcodeado, el flujo pasaría a ser:

1. `tp_domain/calculations/` calcula rango y score con comparables sintéticos
2. `tp_domain/rules/` aplica la regla estadística de la jurisdicción de destino
3. Se añade un bloque "Base legal" con las fichas citadas
4. La IA redacta la explicación sobre ese resultado

---

## 4. Transformaciones necesarias

**Automático** (script, sin intervención):

1. Parseo del frontmatter y headings de las 114 fichas. Sin limpieza previa: 100% parsea.
2. Construcción del grafo de 501 enlaces cruzados.
3. Extracción de datos duros por regex sobre patrones ya localizados (`750M€`, `45M€`, `15%`, `25%`).

**Manual** (criterio profesional, no automatizable):

4. Codificar las reglas estadísticas por jurisdicción. Son 3 fuentes leídas y decididas a mano, incluida la decisión de excluir la propuesta UE retirada.
5. Extraer tipos de retención sobre cánones de los 10 CDI. Requiere leer artículo por artículo.
6. Filtrar la contaminación "corredor Gipuzkoa-Francia" en las fichas afectadas.

**No hace falta**:

7. Parsear los 117 PDF de `raw/`. Ya están fichados en Markdown estructurado. Volver al PDF es trabajo duplicado.

---

## 5. Siguiente paso

Antes de escribir nada, hay una decisión que tomar y no es técnica: **el corpus no resuelve el cuello de botella del MVP**, que son los comparables. Eso sigue exigiendo 50-100 registros sintéticos con rangos realistas por industria.

Dos caminos posibles:

**Camino A, comparables primero.** Construir `tp_domain/comparables/` con datos sintéticos y `calculate_arm_length_range()`. Sustituye el mock de `app.py` por cálculo real. La demo pasa de maqueta a herramienta. El corpus entra después.

**Camino B, reglas primero.** Empezar por `statistical_rules.py` y `thresholds.py`. Más rápido (un día contra tres) y es donde está el conocimiento diferencial, pero las reglas operan sobre un rango que todavía no se calcula de verdad.

Mi recomendación es A. La regla del ajuste a mediana no se puede demostrar sin un rango real sobre el que aplicarla, y en una demo de 5 minutos el evaluador quiere ver el número moverse antes que la cita legal. El corpus multiplica el valor de un motor que funciona; no sustituye al motor.
