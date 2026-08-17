---
clase: legislation
confianza_verificacion: primary_source_verified
enlaces:
- sub_is/ris-rd634-2015-reglamento-impuesto-sociedades
- sub_tp/ocde-directrices-precios-transferencia-2022
- sub_tp/beps-acciones-8-10-precios-transferencia
- sub_is/establecimiento-permanente
fecha_creacion: 2026-07-30
fuente_primaria: Ley 27/2014, del Impuesto sobre Sociedades, Art. 18
localizador: BOE-A-2014-12328
origen: Cerebros_Fiscales/wiki/sub_tp/lis-art18-operaciones-vinculadas-precios-transferencia.md
rango_normativo: Ley ordinaria
tipo: Normativa estatal, ficha de cabecera de la Capa España
tipo_localizador: boe_id
titulo: 'España — Art. 18 LIS: operaciones vinculadas'
usar_en: tp_domain/rules/spanish_rules.py (Fase 2A)
verificada_el: 2026-08-10
---

# España — Art. 18 LIS: operaciones vinculadas

**Origen:** `Cerebros_Fiscales/wiki/sub_tp/lis-art18-operaciones-vinculadas-precios-transferencia.md`
**Fuente primaria:** Ley 27/2014, del Impuesto sobre Sociedades, Art. 18
**Tipo:** Normativa estatal, ficha de cabecera de la Capa España
**Usar en:** `tp_domain/rules/spanish_rules.py` (Fase 2A)

## El dato que define la regla española

**El Art. 18.4 LIS no contiene ninguna regla estadística.** No impone el rango intercuartílico, no impone el ajuste a la mediana, no fija jerarquía entre métodos. Exige aplicar uno de los cinco métodos y elegir "el más adecuado".

Esto es lo que hace interesante el comparador de jurisdicciones: es la ausencia de regla, no su presencia.

## Perímetro de vinculación (Art. 18.2)

Ocho supuestos. **Umbral general de participación: 25%** cuando la vinculación se define por relación socio-entidad. Incluye entidad y sus administradores, entidades del mismo grupo, participación indirecta ≥25%, y dos entidades con los mismos socios o parientes participando ≥25% en ambas.

## Los cinco métodos (Art. 18.4)

1. Precio libre comparable (CUP)
2. Coste incrementado
3. Precio de reventa
4. Distribución del resultado
5. Margen neto operacional

Más "otros métodos y técnicas de valoración generalmente aceptados" cuando los cinco no resulten aplicables.

**Sin jerarquía legal.** La elección atiende a "la naturaleza de la operación vinculada, la disponibilidad de información fiable y el grado de comparabilidad" (Art. 18.4, párr. 6). Es *best method rule*, no jerarquía formal, coherente con las Directrices OCDE post-2010.

## Servicios intragrupo (Art. 18.5)

Test legal adicional al valor de mercado: los servicios deben "producir o poder producir una ventaja o utilidad a su destinatario". Es la traducción española del *benefits test* del Cap. VII, párr. 7.6 de las Directrices OCDE.

Para servicios prestados conjuntamente sin individualización posible, se admite reparto mediante "reglas de reparto que atiendan a criterios de racionalidad".

## Documentación (Art. 18.3)

**Umbral de 45 M€** de cifra de negocios para contenido simplificado. Cinco excepciones impiden el contenido simplificado con independencia de la cifra de negocios, entre ellas operaciones con entidades en estimación objetiva de IRPF con participación ≥25%, transmisión de negocios y transmisión de valores.

## Régimen sancionador (Art. 18.13) — parametrizable

| Supuesto | Sanción |
|---|---|
| Documentación omitida, incompleta o falsa, sin corrección administrativa | 1.000 € por dato, 10.000 € por conjunto de datos |
| Límite máximo del anterior | El menor entre el 10% de las operaciones y el 1% del INCN |
| Valor de mercado documentado ≠ valor declarado | 15% sobre el importe de las correcciones |

Las dos últimas son incompatibles entre sí.

## Aplicación en TPIP

- `spanish_rules()` → `RangeRule.BEST_METHOD_NO_STATISTICAL_RULE`
- El umbral del 25% alimenta una validación de perímetro previa al análisis
- Los 45 M€ determinan qué documentación exige el informe generado
- El régimen sancionador puede entrar como factor cuantificado en `calculate_defensibility_score()`: un rate fuera de rango con documentación incompleta expone a 15% sobre la corrección más multas fijas

## Enlaces en el corpus original

`[[sub_is/ris-rd634-2015-reglamento-impuesto-sociedades]]`, `[[sub_tp/ocde-directrices-precios-transferencia-2022]]`, `[[sub_tp/beps-acciones-8-10-precios-transferencia]]`, `[[sub_is/establecimiento-permanente]]`
