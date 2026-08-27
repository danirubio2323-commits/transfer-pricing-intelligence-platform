---
clase: legislation
confianza_verificacion: primary_source_verified
enlaces:
- jurisdictions/spain/art18-lis-operaciones-vinculadas
- jurisdictions/spain/ris-documentacion-masterfile-localfile
- frameworks/ocde-directrices-2022-cap3-rango-plena-competencia
- jurisdictions/germany/astg-rango-intercuartilico-ajuste-mediana
fecha_creacion: 2026-08-27
fuente_primaria: Real Decreto 634/2015, Reglamento del Impuesto sobre Sociedades, art.
  17
id_fuente: es-ris-art17
localizador: BOE-A-2015-7771
origen: Lectura directa del texto consolidado del BOE, 2026-08-27
pinpoint: Art. 17.2 (circunstancias de comparabilidad); art. 17.6 (método más adecuado);
  art. 17.7 (medidas estadísticas sobre el rango de valores)
rango_normativo: Reglamento
tipo: Desarrollo reglamentario del art. 18 LIS
tipo_localizador: boe_id
titulo: 'España — art. 17 RIS: comparabilidad y medidas estadísticas'
usar_en: tp_domain/rules/statistical_rules.py, tp_domain/calculations/arm_length_range.py
verificada_el: 2026-08-27
---

# España — art. 17 RIS: comparabilidad y medidas estadísticas

**Fuente primaria:** Real Decreto 634/2015, de 10 de julio, Reglamento del Impuesto sobre Sociedades,
art. 17. Texto consolidado, `BOE-A-2015-7771`.
**Alcance:** el art. 17 completo, siete apartados.
**Usar en:** `tp_domain/rules/statistical_rules.py`, `tp_domain/calculations/arm_length_range.py`

Esta ficha corrige una afirmación que el corpus daba por buena.

## Lo que el corpus decía, y por qué era incompleto

La ficha del art. 18 LIS afirma que **«el Art. 18.4 LIS no contiene ninguna regla estadística»**. Eso
es cierto y sigue siéndolo: la Ley no la contiene.

Pero el motor tradujo esa ausencia a `NO_STATUTORY_RULE` y redacta el veredicto español diciendo que
**«el Art. 18.4 LIS no impone regla estadística; la posición es defendible con la documentación del
método»**. Y eso, dicho sin más, induce a error, porque **el Reglamento sí habilita el uso de medidas
estadísticas**.

## El apartado 7, que es el que faltaba

> 7. Cuando, a pesar de no existir datos suficientes, se haya podido determinar **un rango de valores**
> que cumpla razonablemente el principio de libre competencia, teniendo en cuenta el proceso de
> selección de comparables y las limitaciones de la información disponible, **se podrán utilizar
> medidas estadísticas para minimizar el riesgo de error provocado por defectos en la
> comparabilidad**.

Léase junto al párrafo 3.57 de las Directrices OCDE y se ve que es su trasposición casi literal.
Coinciden los tres elementos:

| Elemento | OCDE, párr. 3.57 y 3.62 | RIS, art. 17.7 |
|---|---|---|
| Presupuesto | Quedan defectos de comparabilidad no identificables ni cuantificables | «a pesar de no existir datos suficientes» y «las limitaciones de la información disponible» |
| Herramienta | *Statistical tools that take account of central tendency* | «medidas estadísticas» |
| Finalidad | *Minimise the risk of error due to (…) remaining comparability defects* | «minimizar el riesgo de error provocado por defectos en la comparabilidad» |
| Fuerza | *Might help* / *may be appropriate* | «**se podrán** utilizar» |

**Tres cosas que el precepto dice, y tres que no.**

Dice: que existe un rango de valores como concepto normativo español; que caben medidas estadísticas
sobre él; y que su función es corregir defectos de comparabilidad, no afinar por gusto.

No dice: **cuál** medida estadística. No nombra el rango intercuartílico. No nombra la mediana. Y no
la impone: el verbo es potestativo.

## Lo que esto significa para el veredicto español

España queda en una posición intermedia que el motor no sabe expresar hoy:

| | Base normativa del rango | Punto de ajuste |
|---|---|---|
| **España** | **Sí**, art. 17.7 RIS, potestativa e inespecífica | **No fijado** |
| Alemania | Sí, §1.3a AStG | **Mediana**, por defecto |
| Italia | Sí, art. 6 DM 2018 | **Interior del intervalo** |

Ya no es «España no tiene regla estadística». Es **«España tiene habilitación para usarlas y no dice
cuál ni obliga a ninguna»**. La diferencia con Alemania sigue siendo real y grande, pero es de otra
naturaleza: no es ausencia frente a presencia, es habilitación abierta frente a mandato cerrado.

### ⚠️ Conflicto Doctrinal / Evolución de Criterio

Y aquí encaja lo que encontró la revisión adversarial del corpus. La práctica de la Inspección de
aplicar el rango intercuartílico y tender a la mediana **no es una costumbre sin apoyo normativo**:
tiene el anclaje del art. 17.7 RIS.

Lo que el art. 17.7 no da es cobertura al **automatismo**. Habilita medidas estadísticas para
minimizar el error; no dice que fuera del rango proceda la mediana. Esa es exactamente la tensión que
recoge la doctrina dividida sobre si la AEAT puede ajustar de oficio a la mediana o debería ir al
cuartil inferior.

**Pendiente:** la resolución del TEAC de 23 de enero de 2023 (00/07503/2020), que aborda la
persistencia de defectos de comparabilidad tras aplicar el rango intercuartílico. No leída.

## El resto del artículo

**Apartado 2 — las circunstancias de comparabilidad.** Cinco, y coinciden con las del art. 42 de la
Norma Foral alavesa y con las del Capítulo III de las Directrices: características del bien o
servicio, funciones con identificación de riesgos y ponderación de activos, términos contractuales,
circunstancias económicas y del mercado, y estrategias empresariales.

Con una adición que las otras dos no tienen expresamente:

> también deberá tenerse en cuenta cualquier otra circunstancia que sea relevante (…) como entre
> otras, la existencia de **pérdidas**, la incidencia de las **decisiones de los poderes públicos**,
> la existencia de **ahorros de localización**, de **grupos integrados de trabajadores** o de
> **sinergias**.

Ahorros de localización, plantilla ensamblada y sinergias son vocabulario del Capítulo I de las
Directrices post-BEPS. Que estén en el Reglamento español es un dato que este corpus no tenía.

**Apartado 3 — agregación.** Cuando las operaciones estén estrechamente ligadas, sean continuas o
afecten a productos muy similares y su valoración independiente no resulte adecuada, el análisis se
hace **sobre el conjunto**. Es el equivalente del art. 5 del decreto italiano.

**Apartado 4 — cuándo dos operaciones son equiparables.** Cuando no hay diferencias significativas
que afecten al precio o al margen, o cuando habiéndolas pueden eliminarse con ajustes de
comparabilidad.

**Apartado 6 — el método más adecuado.** El grado de comparabilidad, la naturaleza de la operación y
la información sobre operaciones equiparables son los factores que determinan el método, en los
términos del art. 18.4 LIS. Confirma la regla del método más adecuado, sin jerarquía.

## Aplicación en TPIP

1. **El veredicto español necesita reescritura.** Decir que la Ley no impone regla estadística es
   verdad a medias mientras se calle que el Reglamento habilita usarlas.
2. **El aviso de muestra pequeña gana fundamento español.** El motor ya avisa cuando hay pocos
   comparables; el art. 17.7 condiciona el uso de medidas estadísticas precisamente a que no existan
   datos suficientes. Deja de ser cautela de ingeniería y pasa a ser presupuesto normativo.
3. La agregación del apartado 3 es una condición que el motor **no comprueba**: analiza operación a
   operación sin preguntar si deberían agregarse.
4. `NO_STATUTORY_RULE` como nombre del valor del enum **es engañoso para España**. Describe la Ley y
   oculta el Reglamento. Conviene renombrarlo cuando se abra `tp_domain`.

## Límites de esta ficha

- No se ha leído el art. 16 RIS completo, solo la referencia que hace al 17.
- TEAC 00/07503/2020 **sin leer**, y es la que diría cómo se aplica el 17.7 en la práctica.
- No se ha comprobado si las Normas Forales tienen un equivalente del art. 17.7 en su desarrollo
  reglamentario. La ficha foral leyó la Norma Foral alavesa, **no su Reglamento** (Decreto Foral).
  Ese hueco es ahora más relevante que antes de leer este artículo.
