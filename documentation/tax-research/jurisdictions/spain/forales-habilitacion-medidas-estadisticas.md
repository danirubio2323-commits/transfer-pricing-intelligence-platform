---
clase: legislation
confianza_verificacion: primary_source_verified
enlaces:
- jurisdictions/spain/alava-nf-37-2013-vinculadas
- jurisdictions/spain/bizkaia-nf-11-2013-vinculadas
- jurisdictions/spain/gipuzkoa-nf-2-2014-vinculadas
- jurisdictions/spain/navarra-lf-26-2016-vinculadas
- jurisdictions/spain/ris-art17-comparabilidad-medidas-estadisticas
- jurisdictions/spain/territorios-forales-operaciones-vinculadas
- processes/doctrina-mediana-exige-defectos-motivados
fecha_creacion: 2026-08-28
fuente_primaria: Decreto Foral 41/2014 (Álava), Decreto Foral de la Diputación Foral
  de Bizkaia 203/2013, Decreto Foral 17/2015 (Gipuzkoa), Decreto Foral 114/2017 (Navarra)
  y Real Decreto 634/2015 (territorio común), en lo relativo al análisis de comparabilidad
id_fuente: es-forales-mapa-estadistico
jurisdiccion: ES
localizador: https://www.navarra.es/documents/48192/6699806/Reglamento%20IS.pdf/ea37edba-eb1b-22d7-a04b-9f9d8fbba4e6
origen: Descarga y búsqueda literal sobre el texto íntegro de los cinco reglamentos,
  2026-08-28
pinpoint: Art. 18.7 del DF 114/2017 de Navarra y art. 17.7 del RD 634/2015; ausencia
  comprobada del precepto equivalente en los reglamentos de Álava, Bizkaia y Gipuzkoa
rango_normativo: Reglamentos forales y estatal
tipo: Análisis comparado de las cinco jurisdicciones españolas
tipo_localizador: url
titulo: España — el mapa estadístico de las cinco jurisdicciones españolas
usar_en: tp_domain/rules/statistical_rules.py, informe de análisis
verificada_el: 2026-08-28
---

# España — el mapa estadístico de las cinco jurisdicciones

En territorio español conviven **cinco jurisdicciones** a efectos del Impuesto sobre Sociedades:
territorio común, los tres Territorios Históricos del País Vasco y la Comunidad Foral de Navarra. Una
operación vinculada entre una sociedad de Bilbao y una de Madrid es, jurídicamente, un caso entre dos
jurisdicciones. Esta ficha responde a la pregunta que el motor necesita: **¿dicen lo mismo?**

La respuesta corta es que en la ley sí y en el reglamento no, y que la diferencia cae exactamente
sobre lo que este motor calcula.

## El resultado

Búsqueda literal de «medidas estadísticas», «rango de valores», «mediana» y «cuartil» sobre el texto
íntegro de las cinco normas de valoración y sus cinco reglamentos. Ninguna aparición de «mediana» en
sentido estadístico en ninguna: las 25 de Bizkaia, 25 de Álava, 22 de Gipuzkoa y 0 de Navarra son
todas «pequeñas y **medianas** empresas».

| Jurisdicción | Norma de valoración | ¿Regla estadística en la ley? | Reglamento | ¿Habilitación estadística? |
|---|---|---|---|---|
| Territorio común | LIS 27/2014, art. 18 | No | RD 634/2015, **art. 17.7** | **Sí** |
| Navarra `ES-NA` | LF 26/2016, arts. 28-29 | No | DF 114/2017, **art. 18.7** | **Sí**, texto idéntico |
| Álava `ES-VI` | NF 37/2013, art. 42 | No | DF 41/2014 | **No aparece** |
| Bizkaia `ES-BI` | NF 11/2013, art. 42 | No | DF 203/2013 | **No aparece** |
| Gipuzkoa `ES-SS` | NF 2/2014, art. 42 | No | DF 17/2015 | **No aparece** |

**El cotejo Navarra-Estado se ha hecho carácter a carácter.** Los dos apartados 7 son el mismo texto,
325 caracteres, letra por letra, y hasta comparten número de apartado.

## Por qué el silencio vasco no es un descuido

Sería fácil leer la tabla como «a los vascos se les olvidó». No es eso, y la razón importa porque
convierte una ausencia en un argumento.

Los tres reglamentos vascos **no tienen artículo de análisis de comparabilidad**. Ni uno. Solo regulan
la documentación (art. 16 en los tres) y el procedimiento de comprobación (art. 22 en Álava y Bizkaia,
art. 21 en Gipuzkoa). El análisis de comparabilidad está donde el legislador vasco decidió ponerlo:
**en la propia Norma Foral, art. 42.1**, con sus cinco circunstancias enumeradas.

De modo que la arquitectura es la siguiente:

| | Dónde está la comparabilidad | Quién podía habilitar lo estadístico | Lo hizo |
|---|---|---|---|
| Común y Navarra | En el reglamento | El reglamento | **Sí** |
| Los tres vascos | **En la Norma Foral** | El legislador foral, en la Norma | **No** |

El legislador vasco tuvo la cuestión en la mano —redactó él mismo el análisis de comparabilidad— y no
introdujo la habilitación. No delegó y no reguló. El silencio es de quien tenía la competencia y la
ejerció.

## Lo que de esto se sigue, y lo que no

**Se sigue** que ante la Hacienda Foral de Álava, Bizkaia o Gipuzkoa falta el asidero normativo interno
que en territorio común y en Navarra ampara el uso de medidas estadísticas. Un contribuyente vizcaíno
al que se le ajuste a la mediana puede preguntar, con fundamento, en qué precepto de su ordenamiento
se apoya esa medida.

**No se sigue** que la Inspección foral vasca no pueda usarlas. Dos vías quedan abiertas y esta ficha
no las cierra:

1. **Las Directrices de la OCDE.** El párrafo 3.57 admite herramientas estadísticas, y el art. 42.1 de
   las Normas Forales recoge el principio de libre competencia. Un inspector puede sostener que las
   Directrices son criterio interpretativo sin necesidad de habilitación reglamentaria propia.
2. **La armonización del Concierto.** El art. 3 de la Ley 12/2002 obliga a los Territorios Históricos a
   atenerse a la Ley General Tributaria en terminología y conceptos. Si de ahí se derivara un deber de
   equivalencia sustancial en esta materia es **cuestión no resuelta y no investigada aquí**.

La distinción es la de siempre y hay que decirla entera: **esto es un mapa de la ley, no de la
práctica inspectora**. No se ha buscado ni una resolución de las Haciendas Forales vascas.

### ⚠️ Conflicto Doctrinal / Evolución de Criterio

Ninguno localizado, porque **no se ha buscado doctrina sobre este punto concreto**. La afirmación de
esta ficha es textual y negativa —tal precepto no está en tal reglamento—, y ese tipo de afirmación es
verificable pero frágil: basta una modificación posterior no consolidada para desmentirla.

## Aplicación en TPIP

1. **Cinco jurisdicciones, no una.** `ES`, `ES-VI`, `ES-BI`, `ES-SS`, `ES-NA`, con los códigos ISO
   3166-2:ES. Un caso entre Bilbao y Madrid es transfronterizo a efectos de este análisis.
2. **Cuatro de las cinco comparten hoy la misma consecuencia de rango**, ausencia de regla estadística
   legal. Modelarlas es, por tanto, barato: no hay cálculo nuevo.
3. **Y sin embargo cada una debe citar su propia norma.** Aquí está el cambio de diseño. El motor
   guarda hoy las fuentes en `_RULE_SOURCES`, un diccionario **indexado por regla**, no por
   jurisdicción. Cuatro jurisdicciones con la misma regla recibirían por construcción las mismas
   fuentes, de modo que un informe de Bizkaia citaría el **art. 18 LIS a la Hacienda Foral de
   Bizkaia**: una norma que allí no rige. La estructura de datos hace imposible acertar. Hay que
   separar la fuente por jurisdicción **antes** de dar de alta ninguno de los cuatro territorios.

   No salió de leer las normas, sino de preguntarse para qué se citan.
4. Cuando el veredicto español se corrija para reflejar el art. 17.7 RIS y la doctrina de la SAN
   1072/2019, **esa corrección no debe propagarse a los tres territorios vascos**: allí no hay art.
   17.7 que invocar. El texto del veredicto tiene que poder diferir aunque la regla coincida.

## Límites de esta ficha

- **Afirmaciones negativas sobre textos de fecha distinta.** Bizkaia consolidado a 27/04/2022,
  Gipuzkoa a 2017, **Álava en su redacción original de 2014 sin consolidar**. La de Álava es la más
  débil de las tres y así se declara en su propia ficha.
- **No se ha buscado doctrina ni jurisprudencia** de ninguna de las cuatro Haciendas Forales.
- **La vía de las Directrices OCDE queda abierta y sin resolver.** Es el contraargumento evidente y la
  ficha no lo despacha: lo señala.
- **El art. 3 de la Ley 12/2002 no se ha analizado** en clave de si impone equivalencia sustancial.
- No se ha comprobado si existen **órdenes forales o instrucciones internas** que suplan el silencio
  reglamentario. Sería el primer sitio donde mirar para desmentir esta ficha.
