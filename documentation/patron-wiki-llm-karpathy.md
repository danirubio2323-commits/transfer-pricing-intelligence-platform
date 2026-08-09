# Sistema de gestión del conocimiento: patrón LLM Wiki (Karpathy)

**Origen:** `Cerebros_Fiscales/CLAUDE.md` y `PAQUETE_MIGRACION_CLAUDE_PROJECT.md`
**Tipo:** arquitectura de datos, no contenido fiscal
**Usar en:** `infrastructure/wiki_parser.py`, trazabilidad de citas en informes

## Qué es

El corpus fiscal no es un montón de PDFs con búsqueda encima. Es una wiki compilada incrementalmente: cada fuente se lee una vez, se destila en una ficha markdown, y a partir de ahí **la ficha es la referencia, no el PDF**.

Tres capas:

1. `raw/` — fuentes inmutables (117 PDF, 6 HTML). Nunca se modifican.
2. `wiki/` — 114 fichas markdown generadas, con wikilinks `[[slug]]`
3. `CLAUDE.md` — el esquema: convenciones, protocolo de ingesta, reglas de infalibilidad

Más dos ficheros de navegación: `index.md` (catálogo por categoría) y `log.md` (cronológico, append-only).

## Por qué es explotable por software

Medido sobre las 114 fichas:

| Métrica | Valor |
|---|---|
| Frontmatter YAML que parsea sin error | **114 / 114 (100%)** |
| Enlaces cruzados declarados | 501 |
| Media de enlaces por ficha | 4,4 |
| Fichas con `fuente_raw` | 111 / 114 |
| Fichas con `titulo` | 114 / 114 |

Campos del frontmatter: `titulo`, `fecha`, `origen`, `fuente_raw`, `idioma_fuente`, `enlaces`, y `estado` en 33 fichas.

Headings normalizados: `## Hechos` (100), `## Doctrina aplicada` (102), `## Conclusión jurídica` (110), `## Contenido` (82).

**No hay fase de limpieza.** Un parser con `pyyaml` extrae el corpus entero a JSON estructurado.

## Convenciones que TPIP debería heredar

**Cabecera estandarizada de conflicto normativo.** El corpus usa exactamente `### ⚠️ Conflicto Doctrinal / Evolución de Criterio` (16 apariciones), prohibiendo variantes ad hoc. Cuando una norma nueva contradice un criterio previo, no se borra lo antiguo: se documenta la línea temporal.

Aplicado a TPIP: cuando una regla jurisdiccional cambie, `tp_domain/rules/` debería versionar, no sobrescribir. Un análisis emitido en 2025 debe poder reproducirse en 2027.

**Prohibición de suposiciones.** El corpus prohíbe calificar jurídicamente un hecho o rellenar lagunas por cuenta propia; ante ambigüedad, se detiene y alerta.

Aplicado a TPIP: es exactamente la regla de gobernanza de IA del proyecto. La IA explica resultados calculados, no los genera. La coherencia entre ambos documentos no es casual.

**Citas pinpoint.** Cada afirmación lleva referencia a artículo, apartado o párrafo. Ese es el estándar que deben cumplir los informes generados por TPIP.

## Aplicación en TPIP

- `infrastructure/wiki_parser.py`: volcar las 114 fichas a `corpus_index.json` para citar fuente legal en los informes
- El grafo de 501 enlaces permite, dada una regla aplicada, mostrar las fichas relacionadas
- Trazabilidad: `regla aplicada → ficha → fuente_raw → PDF original`

## ⚠️ Contaminación de alcance conocida

La auditoría del corpus de julio de 2026 detectó que varias fichas de `sub_is/` y `concierto_foral/` orientan sus conclusiones hacia un caso de estudio territorial concreto (corredor pyme Gipuzkoa-Francia), procedente de un TFG de ADE hermano pero distinto.

TPIP es de propósito general. Esas conclusiones hay que leerlas con filtro, y no deben trasladarse al motor.
