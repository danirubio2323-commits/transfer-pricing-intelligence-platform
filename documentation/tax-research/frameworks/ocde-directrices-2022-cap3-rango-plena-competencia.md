---
clase: guidelines
confianza_verificacion: primary_source_verified
enlaces:
- frameworks/ocde-directrices-2022-marcos-riesgo-dempe-servicios
- frameworks/criterios-seleccion-comparables
- jurisdictions/spain/art18-lis-operaciones-vinculadas
- jurisdictions/germany/astg-1-3a-ajuste-mediana
fecha_creacion: 2026-08-20
fuente_primaria: OECD Transfer Pricing Guidelines 2022, Cap. III, apdo. A.7
id_fuente: oecd-tpg-2022-cap3
localizador: raw/Normativa_Internacional/OCDE_BEPS/OCDE, Transfer Pricing Guidelines
  (ene 2022) Directrices Precios de Transferencia.pdf — pp. 165-167 impresas (índice
  PDF 167-169), párr. 3.55-3.66
origen: Lectura directa del PDF del corpus local, 2026-08-20
pinpoint: Rango de plena competencia (párr. 3.55-3.59); punto del rango (3.60-3.62);
  resultados extremos (3.63-3.66)
rango_normativo: Directrices OCDE
tipo: Marco internacional, Directrices OCDE 2022
tipo_localizador: offline
titulo: 'OCDE — Directrices 2022, Cap. III: el rango de plena competencia'
usar_en: tp_domain/calculations/arm_length_range.py, tp_domain/rules/statistical_rules.py
verificada_el: 2026-08-20
---

# OCDE — Directrices 2022, Cap. III: el rango de plena competencia

**Fuente primaria:** OECD Transfer Pricing Guidelines 2022, Cap. III, apdo. A.7
**Alcance de esta ficha:** el apartado A.7 completo, párrafos 3.55 a 3.66. El resto del
Capítulo III —factores de comparabilidad, búsqueda de comparables, ajustes— queda sin desarrollar.
**Usar en:** `tp_domain/calculations/arm_length_range.py`, `tp_domain/rules/statistical_rules.py`

Esta ficha existe porque el motor de TPIP cita `oecd-tpg-2022-cap3` en **todos** los análisis y no
tenía ficha detrás. La entrada del registro cerrado apuntaba su nota de investigación al fichero de
los marcos de riesgo, DEMPE y servicios, que cubre los Capítulos I, VI y VII y **no menciona el
Capítulo III**.

## Por qué existe un rango y no una cifra

**3.55.** El principio de plena competencia a veces permite llegar a una cifra única. Pero los precios
de transferencia no son una ciencia exacta, y con frecuencia el método más apropiado produce un
**abanico de cifras igual de fiables entre sí**. La razón es doble: aplicar el principio solo produce
una aproximación de lo que habrían pactado partes independientes, y partes independientes en
circunstancias comparables tampoco fijarían exactamente el mismo precio.

Esto es lo que legitima que TPIP devuelva un rango y una posición dentro de él, y no un número.

**3.56.** Cuando puede determinarse que algunas operaciones no vinculadas son **menos comparables**
que otras, deben eliminarse. No es una opción: el verbo es *should be eliminated*.

**3.59.** Una desviación sustancial entre puntos del rango puede indicar que los datos de algunos
puntos son menos fiables, o que hay diferencias que exigen ajuste. Esos puntos requieren análisis
adicional antes de aceptarlos en el rango.

## El párrafo que sostiene el rango intercuartílico

**3.57.** Este es el que importa para el motor, y se cita literalmente:

> 3.57. It may also be the case that, while every effort has been made to exclude points that have a
> lesser degree of comparability, what is arrived at is a range of figures for which it is considered,
> given the process used for selecting comparables and limitations in information available on
> comparables, that some comparability defects remain that cannot be identified and/or quantified,
> and are therefore not adjusted. **In such cases, if the range includes a sizeable number of
> observations, statistical tools that take account of central tendency to narrow the range (e.g. the
> interquartile range or other percentiles) might help to enhance the reliability of the analysis.**

Tres cosas que dice, y que conviene no estirar:

1. La herramienta estadística es un **remedio a defectos residuales de comparabilidad**, no un paso
   rutinario del método. Se acude a ella cuando quedan defectos que no se han podido identificar ni
   cuantificar.
2. Está condicionada a que haya **un número apreciable de observaciones** (*a sizeable number*). Las
   Directrices no dicen cuántas.
3. El verbo es ***might help***. No impone el rango intercuartílico, ni ningún otro percentil, ni un
   método de cálculo de percentiles. Quien lo imponga, lo impone su Derecho interno, no la OCDE.

### Consecuencia para TPIP

El aviso que el motor ya emite cuando la muestra es pequeña no es una cautela de ingeniería: es el
requisito de *sizeable number*. Y la convención de cálculo de percentiles se declara en el propio
informe precisamente porque las Directrices no fijan ninguna.

## Qué pasa cuando el tipo cae dentro o fuera

**3.60.** Si la condición analizada está **dentro** del rango de plena competencia, **no procede
ajuste alguno**. Sin matices y sin condiciones.

**3.61.** Si cae **fuera** del rango sostenido por la Administración, el contribuyente tiene derecho a
alegar que su operación sí satisface el principio de plena competencia y que el rango correcto es
otro. Solo si no lo acredita, la Administración determina el punto al que ajustará.

El orden importa y suele contarse mal: primero la carga de alegar del contribuyente, después el ajuste.
El ajuste no es automático por el mero hecho de estar fuera.

**3.62.** Y aquí está la bisagra doctrinal de todo lo que TPIP modela:

> 3.62. In determining this point, where the range comprises results of relatively equal and high
> reliability, **it could be argued that any point in the range satisfies the arm's length principle**.
> Where comparability defects remain as discussed in paragraph 3.57, **it may be appropriate to use
> measures of central tendency** to determine this point (for instance the median, the mean or
> weighted averages, etc., depending on the specific characteristics of the data set), in order to
> minimise the risk of error due to unknown or unquantifiable remaining comparability defects.

Dos regímenes, no uno:

| Situación | Qué dice la OCDE |
|---|---|
| Resultados de fiabilidad alta y pareja | **Cualquier punto** del rango satisface el principio |
| Quedan defectos de comparabilidad (3.57) | **Puede ser apropiado** acudir a la tendencia central — mediana, media, medias ponderadas |

La mediana no es la regla por defecto de las Directrices. Es una de varias medidas de tendencia
central, disponible solo en el segundo supuesto, y en potencial.

## Por qué España y Alemania divergen sobre la misma base

Esta ficha explica la asimetría que el motor reporta y que hasta ahora estaba sin fundamentar:

- **España** no traspone ninguna regla estadística. El art. 18.4 LIS no impone ajuste automático a la
  mediana, y la corrección valorativa depende de la valoración caso por caso de la Inspección. Se
  queda, por tanto, en el terreno abierto de 3.62: cabe sostener cualquier punto del rango.
- **Alemania** convierte en obligatorio lo que 3.62 deja en potencial. El §1.3a AStG impone el ajuste
  a la mediana como consecuencia por defecto salvo prueba en contrario del contribuyente.

Es Derecho interno construido **sobre** un texto que no obligaba a construirlo así. Por eso una
jurisdicción sin ficha se queda en `NOT_MODELLED`: la base común de 3.62 no permite deducir qué hizo
con ella un tercer Estado.

### ⚠️ Conflicto Doctrinal / Evolución de Criterio

No hay conflicto entre 3.62 y el §1.3a AStG: el segundo ejerce una opción que el primero permite. Lo
que sí hay es una **tensión de expectativas**: un asesor acostumbrado al ajuste alemán tiende a leer
la mediana como la consecuencia natural de estar fuera del rango, y en el texto de la OCDE no lo es.
La lectura inversa —española— tiende a olvidar que fuera de las fronteras la mediana sí puede ser
automática.

## Resultados extremos

**3.63-3.66.** Un resultado extremo —pérdidas o beneficios anormalmente altos— exige entender **por
qué** lo es. Y la regla de exclusión es estricta:

> An extreme result may be excluded on the basis that a previously overlooked significant
> comparability defect has been brought to light, **not on the sole basis that the results arising from
> the proposed "comparable" merely appear to be very different** from the results observed in other
> proposed "comparables".

- **3.64.** Una empresa independiente no mantendría actividades en pérdidas sin expectativa razonable
  de beneficios futuros, y las funciones simples o de bajo riesgo no deberían generar pérdidas
  prolongadas. Pero eso **no convierte en no comparable** a toda operación en pérdidas: no hay regla
  general de inclusión o exclusión, y lo que decide son los hechos y circunstancias, no el resultado
  financiero.
- **3.66.** El mismo escrutinio se aplica a beneficios anormalmente altos, no solo a las pérdidas.

### Consecuencia para TPIP

Los motivos de rechazo del motor son de comparabilidad —industria distinta, ejercicio fuera de plazo,
sin tipo informado—, nunca «el tipo se aleja mucho de los demás». Eso es exactamente lo que 3.63
prohíbe, y conviene que siga siendo así si algún día se añade un filtro nuevo.

## Nota sobre el localizador

La entrada `oecd-tpg-2022-cap3` del registro cerrado sitúa el párrafo 3.55 en la **página 165
impresa**, y eso es exacto. El índice de PDF que da entre paréntesis —166— está desplazado en una
página: la 165 impresa es la **167** del PDF. La página impresa, que es la que se cita, está bien.

## Aplicación en TPIP

| Párrafo | Dónde se nota |
|---|---|
| 3.55 | El motor devuelve un rango y una posición, no una cifra |
| 3.56, 3.63-3.66 | Los motivos de rechazo son de comparabilidad, nunca de lejanía del resultado |
| 3.57 | El rango intercuartílico, y el aviso cuando la muestra es corta |
| 3.60 | Posición dentro del rango → sin ajuste |
| 3.62 | La divergencia entre `NO_STATUTORY_RULE` y `INTERQUARTILE_MEDIAN_ADJUSTMENT` |
