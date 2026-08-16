---
titulo: "Alemania — §1.3/1.3a AStG: rango intercuartílico y ajuste obligatorio a la mediana"
fecha_creacion: 2026-07-30
origen: "Cerebros_Fiscales/wiki/matriz/de-astg-transparencia-precios.md"
fuente_primaria: "Außensteuergesetz (AStG), §1.3 y §1.3a"
tipo: "Derecho comparado, normativa vigente"
usar_en: "tp_domain/rules/german_rules.py (Fase 2A)"
enlaces: ["sub_tp/lis-art18-operaciones-vinculadas-precios-transferencia", "sub_tp/ocde-directrices-precios-transferencia-2022"]
---

# Alemania — §1.3/1.3a AStG: rango intercuartílico y ajuste obligatorio a la mediana

**Origen:** `Cerebros_Fiscales/wiki/matriz/de-astg-transparencia-precios.md`
**Fuente primaria:** Außensteuergesetz (AStG), §1.3 y §1.3a
**Tipo:** Derecho comparado, normativa vigente
**Usar en:** `tp_domain/rules/german_rules.py` (Fase 2A)

## La regla, que es la contraria a la española

El principio de plena competencia da lugar generalmente a un **rango de valores** (*Bandbreite*). Y aquí viene lo que España no tiene:

1. Si tras los ajustes **persisten diferencias de comparabilidad**, el rango debe **estrecharse eliminando el cuartil inferior y el cuartil superior** (rango intercuartílico, P25-P75).
2. Si el valor declarado por el contribuyente **queda fuera** del rango (o del rango estrechado), **se aplica la mediana** (P50).
3. Salvo que el contribuyente **acredite de forma verosímil** que otro valor del rango se ajusta mejor al principio de plena competencia.

Fuente: §1.3a AStG, cita pinpoint.

## Metodología previa

Exige análisis funcional y de riesgos (*Funktions- und Risikoanalyse*): qué funciones ejerce cada parte, qué riesgos asume, qué activos emplea. El método se elige como el mejor adaptado según comparabilidad y disponibilidad de datos.

## Por qué esto es el corazón del comparador

Misma transacción, mismo rate, mismos comparables. Dos consecuencias:

| | España (Art. 18.4 LIS) | Alemania (§1.3a AStG) |
|---|---|---|
| Regla estadística | Ninguna en la ley | Rango intercuartílico obligatorio |
| Rate fuera de rango | Valoración caso por caso de la Inspección | **Ajuste automático a la mediana** |
| Carga de la prueba | General | Invertida: el contribuyente debe acreditar otro punto |
| Predictibilidad | Baja | Alta |

Un royalty de software al 12% con benchmark P25-P75 de 8,35-11,2%: en Alemania el ajuste a 10,1% (mediana) es la consecuencia por defecto; en España no hay regla legal que lo imponga.

## Aplicación en TPIP

- `german_rules()` → `RangeRule.INTERQUARTILE_MEDIAN_ADJUSTMENT`
- El motor debe devolver, además del veredicto, el **valor de ajuste** cuando la jurisdicción lo imponga: `adjusted_rate = p50`
- La UI muestra las dos columnas en paralelo. Esa pantalla es la demo

## Nota de alcance

La ficha original documenta §1.3 con cita pinpoint parcial. Antes de presentar esto como asesoramiento, conviene verificar el texto vigente del AStG: el corpus lo marca como lectura dirigida, no exhaustiva.

## Enlaces en el corpus original

`[[sub_tp/lis-art18-operaciones-vinculadas-precios-transferencia]]`, `[[sub_tp/ocde-directrices-precios-transferencia-2022]]`
