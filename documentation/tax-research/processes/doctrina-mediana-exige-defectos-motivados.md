---
clase: case_law
confianza_verificacion: primary_source_verified
enlaces:
- jurisdictions/spain/ris-art17-comparabilidad-medidas-estadisticas
- jurisdictions/spain/art18-lis-operaciones-vinculadas
- frameworks/ocde-directrices-2022-cap3-rango-plena-competencia
- jurisdictions/germany/astg-rango-intercuartilico-ajuste-mediana
fecha_creacion: 2026-08-27
fuente_primaria: STSJ Madrid 251/2026, de 6 de mayo de 2026 (ROJ STSJ M 5948/2026),
  que recoge la doctrina de la SAN 1072/2019, de 6 de marzo de 2019, y de la Resolución
  del TEAC 4881/2019, de 23 de noviembre de 2021
id_fuente: es-doctrina-mediana-defectos
jurisdiccion: ES
localizador: https://www.poderjudicial.es/search/AN/openDocument/acfe9f28d810aab6a0a8778d75e36f0d/20260615
origen: Descarga y lectura del texto íntegro desde CENDOJ, 2026-08-27
pinpoint: Fundamentos de Derecho cuarto y quinto; doctrina de la SAN de 6 de marzo
  de 2019, fundamento tercero
rango_normativo: Jurisprudencia y doctrina administrativa
tipo: Doctrina sobre el uso de medidas de tendencia central
tipo_localizador: url
titulo: 'España — la mediana exige defectos de comparabilidad motivados, no basta estar
  fuera del rango'
usar_en: tp_domain/rules/statistical_rules.py, redacción del veredicto español
verificada_el: 2026-08-27
---

# España — la mediana exige defectos de comparabilidad motivados

**Fuente primaria:** STSJ de Madrid, Sección Quinta, sentencia 251/2026 de 6 de mayo de 2026, recurso
1186/2022, ROJ `STSJ M 5948/2026`, ECLI `ES:TSJM:2026:5948`, ponente Sr. Gallego Laguna. Texto
íntegro descargado de CENDOJ y leído.

Dentro de ella, la doctrina que aplica procede de dos resoluciones anteriores que la sentencia
transcribe: **SAN 1072/2019, de 6 de marzo de 2019**, fundamento tercero, y **Resolución del TEAC
4881/2019, de 23 de noviembre de 2021**.

**Aviso de alcance.** Las dos resoluciones citadas se conocen **a través de esta sentencia**, que las
transcribe. No se han leído en su fuente. Lo verificado directamente es el texto del TSJ.

## Por qué esta ficha estaba pendiente

La revisión adversarial del corpus dejó una pregunta abierta: si la Administración española puede
ajustar de oficio a la mediana cuando el tipo cae fuera del rango. El corpus decía que España «no
tiene regla estadística», y luego el art. 17.7 RIS demostró que sí hay habilitación reglamentaria.
Faltaba saber **cómo se aplica**.

Esta es la respuesta, y es más precisa de lo que esperaba.

## La regla

Estar fuera del rango y aplicar la mediana son **dos cosas distintas con dos presupuestos distintos**.
La Audiencia Nacional lo separa así:

> es claro que, si el ROS se encuentra fuera de los límites del rango intercuantil, **debe realizarse
> la correspondiente regularización** (…). Ahora bien, para aplicar **la mediana** es preciso que,
> además, **existan «defectos de comparabilidad»**.

Y lo remacha:

> el hecho de que esto ocurra **no permite, sin más, aplicar la mediana** en los términos previstos en
> la regla 3.62, pues la aplicación de dicha regla **no se justifica en el hecho de estar fuera del
> rango de plena competencia, sino en la existencia de «defectos de la comparabilidad»**.

Dos consecuencias que conviene no mezclar:

| Presupuesto | Consecuencia |
|---|---|
| El indicador cae fuera del rango | Procede regularizar |
| **Además** hay defectos de comparabilidad **motivados** | Cabe ajustar a la mediana |
| Fuera del rango **sin** defectos motivados | Se ajusta **al límite del rango**, no a la mediana |

Ese último punto lo resuelve el caso de 2019 con una cifra: el rango intercuartílico iba del 2,1 % al
7,6 %, la Inspección ajustó al 4,1 % —la mediana— y la Audiencia Nacional corrigió:

> **el ajuste debió haberse efectuado sobre el 2,1 %, no sobre el 4,1 %.**

Es decir, **al cuartil inferior**. Al borde del rango.

## Y aquí está lo que no vi venir

Si el lector ha llegado hasta aquí desde la ficha de Italia, la coincidencia salta sola.

| | Fuera del rango, sin defectos motivados |
|---|---|
| **Italia**, art. 6.3 DM 2018 | Ajuste «al interior del intervalo» |
| **España**, doctrina SAN 2019 | Ajuste al límite del rango, el 2,1 % del caso |
| **Alemania**, §1.3a AStG | Mediana por defecto |

**La solución española por vía judicial coincide en el resultado con la solución italiana por vía
normativa.** Una la escribió el legislador; la otra la construyó un tribunal interpretando el párrafo
3.62 de las Directrices. Y ambas se apartan de la alemana.

Esto corrige de raíz la tabla de tres regímenes que escribió la ficha italiana. No es que España
carezca de criterio: es que su criterio, cuando no hay defectos motivados, **es el mismo que el
italiano**.

## Qué cuenta como defecto de comparabilidad, y qué no

La sentencia da ejemplos de las dos cosas, y son útiles porque son concretos.

**No basta.** El TEAC, transcrito en la sentencia:

> una diferencia en el volumen de ventas **no es razón suficiente** para rechazar la validez del
> informe (…). El hecho de que la entidad comprobada ocupe una posición líder dentro de su sector por
> su volumen de ventas **no provoca de por sí una falta de homogeneidad**.

**Sí basta**, en el caso resuelto en 2026. La Inspección acreditó que la entidad, presentada como
simple distribuidora, realizaba además **funciones de instalación, servicio postventa y formación**, y
que la segmentación de su cuenta de pérdidas y ganancias carecía de sentido económico. Con eso, el
tribunal consideró motivados los defectos y confirmó el ajuste:

> habiendo sido motivada de forma suficiente los defectos de comparabilidad por parte de la Inspección
> de los Tributos no cabe sino desestimar las pretensiones de la parte reclamante.

La diferencia entre los dos casos es de **prueba funcional**, no de estadística. Lo que decidió no fue
el tamaño de la muestra: fue que la empresa hacía más cosas de las que decía hacer.

## La coherencia que exige el TEAC

Hay un argumento en la resolución del TEAC transcrita que merece retenerse por su valor táctico:

> no siendo congruente **que la muestra se utilice como análisis de comparabilidad así como para
> extraer datos en los que se basa la propia regularización, para luego ser rechazada** para el efecto
> que pudiera ser favorable al interesado.

La Administración no puede usar la muestra del contribuyente para construir el ajuste y descartarla
cuando le favorece. Es una exigencia de coherencia probatoria, y es un argumento defensivo directo.

### ⚠️ Conflicto Doctrinal / Evolución de Criterio

No hay conflicto entre estas resoluciones: la de 2026 aplica la doctrina de 2019 y llega a resultado
contrario **porque los hechos eran distintos**, no porque cambiara el criterio. En 2019 los defectos
no estaban motivados y el ajuste a la mediana cayó; en 2026 sí lo estaban y el ajuste se confirmó.

Lo que sí queda por comprobar es si el **Tribunal Supremo** se ha pronunciado. La sentencia de 2026
advierte que es susceptible de recurso de casación. **No se ha buscado jurisprudencia del TS**, y esa
es la pieza que faltaría para dar la doctrina por asentada.

## Aplicación en TPIP

Esto tiene consecuencia directa sobre el motor, y es la más importante que ha salido de toda la
revisión.

1. **El veredicto español está mal calibrado en las dos direcciones.** Hoy dice que fuera del rango
   «la corrección valorativa depende de la valoración caso por caso de la Inspección». Es vago. La
   doctrina permite decir algo mucho más útil: procede regularización, y el punto de ajuste es el
   límite del rango **salvo** que la Inspección motive defectos de comparabilidad, en cuyo caso cabe
   la mediana.
2. **`adjusted_rate` para España deja de ser `None`.** Hoy el motor solo calcula un tipo ajustado para
   Alemania. Con esta doctrina, España tiene un punto de ajuste identificable: el cuartil más próximo.
3. **La distancia entre España e Italia se estrecha**, y la que se ensancha es la de Alemania. La
   tabla comparada del corpus necesita reescribirse.
4. El argumento de coherencia del TEAC es material para la sección de riesgos del informe.

## Límites de esta ficha

- **SAN 1072/2019 y TEAC 4881/2019 leídas solo a través de la transcripción** de esta sentencia. Para
  citarlas en un informe habría que ir a su texto.
- **TEAC 00/07503/2020, de 23 de enero de 2023**, que la revisión adversarial identificó, sigue sin
  leer. Puede matizar o confirmar lo anterior.
- **Sin jurisprudencia del Tribunal Supremo** sobre este punto.
- La sentencia resuelve sobre ejercicios 2014 y 2015, bajo el RIS vigente. No se ha comprobado si el
  criterio se ha aplicado a ejercicios posteriores.
