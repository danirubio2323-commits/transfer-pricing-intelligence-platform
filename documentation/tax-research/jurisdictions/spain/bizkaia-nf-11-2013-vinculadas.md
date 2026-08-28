---
clase: legislation
confianza_verificacion: primary_source_verified
enlaces:
- jurisdictions/spain/forales-habilitacion-medidas-estadisticas
- jurisdictions/spain/territorios-forales-operaciones-vinculadas
- jurisdictions/spain/art18-lis-operaciones-vinculadas
- jurisdictions/spain/ris-art17-comparabilidad-medidas-estadisticas
fecha_creacion: 2026-08-28
fuente_primaria: Norma Foral 11/2013, de 5 de diciembre, del Impuesto sobre Sociedades
  del Territorio Histórico de Bizkaia, art. 42; Decreto Foral de la Diputación Foral
  de Bizkaia 203/2013, de 23 de diciembre, por el que se aprueba el Reglamento del
  Impuesto sobre Sociedades
id_fuente: es-bi-nf11-2013-art42
jurisdiccion: ES-BI
localizador: https://www.bizkaia.eus/Ogasuna/Zerga_Arautegia/Indarreko_arautegia/pdf/ca_11_2013.pdf
origen: Descarga y lectura del PDF oficial de bizkaia.eus (texto actualizado a 03/12/2022,
  198 páginas) y del Reglamento DF 203/2013 (actualizado a 27/04/2022, 57 páginas),
  2026-08-27 y 2026-08-28
pinpoint: Art. 42 NF 11/2013, apartados 1 (valor normal de mercado y análisis de comparabilidad),
  3 (perímetro, umbral del 25 por 100) y 4 (los cinco métodos); art. 46 (régimen sancionador);
  DF 203/2013, arts. 16 y 22
rango_normativo: Norma Foral y Decreto Foral
tipo: Regla de valoración de una jurisdicción foral
tipo_localizador: url
titulo: 'Bizkaia — NF 11/2013, art. 42: valor normal de mercado sin regla estadística'
usar_en: tp_domain/rules/statistical_rules.py, informe de análisis
verificada_el: 2026-08-28
---

# Bizkaia — NF 11/2013, art. 42

**Fuente primaria:** Norma Foral 11/2013, de 5 de diciembre, del Impuesto sobre Sociedades del
Territorio Histórico de Bizkaia, art. 42, y su Reglamento, aprobado por Decreto Foral de la
Diputación Foral de Bizkaia 203/2013, de 23 de diciembre. Ambos PDF descargados del portal oficial
`bizkaia.eus` y leídos íntegros.

**Por qué esta ficha existe, y no basta con la del art. 18 LIS.** Ante la Hacienda Foral de Bizkaia
el fundamento de una valoración es esta Norma Foral. El art. 18 LIS **no se aplica** en Bizkaia. Que
digan lo mismo no convierte a uno en cita válida del otro: un informe que fundamente en la Ley
estatal una operación sujeta a normativa vizcaína está citando Derecho que allí no rige.

## La regla de valoración (art. 42.1)

> Las operaciones efectuadas entre personas o entidades vinculadas se valorarán por su **valor normal
> de mercado**. Se entenderá por valor normal de mercado aquél que se habría acordado por personas o
> entidades independientes en condiciones de libre competencia (…)

Dos diferencias de letra con el territorio común, ninguna de fondo pero ambas relevantes al citar:

| | Territorio común, art. 18 LIS | Bizkaia, art. 42 NF |
|---|---|---|
| Nombre del estándar | «valor de mercado» | «valor **normal** de mercado» |
| Dónde vive el análisis de comparabilidad | En el Reglamento, art. 17 RIS | **En la propia Norma Foral**, art. 42.1 |

Esa segunda fila es la que explica todo lo demás, y se desarrolla abajo.

## Los cinco métodos (art. 42.4)

Precio libre comparable, coste incrementado, precio de reventa, distribución del resultado y **margen
neto del conjunto de operaciones**. La letra e) conserva la denominación anterior a 2015: el art. 18.4
LIS la llama hoy «margen neto **operacional**».

Sin jerarquía entre ellos. El criterio de elección es el de la redacción anterior a la reforma
estatal de 2014:

> El análisis de comparabilidad a que se hace referencia en el apartado 1 de este artículo y la
> información sobre las operaciones equiparables constituyen factores que permitirán, en cada caso,
> (…) la elección del **método de valoración más adecuado**.

Y cierra con la misma cláusula abierta que el art. 18.4 LIS: cuando no quepa aplicar los anteriores,
otros métodos y técnicas generalmente aceptados que respeten el principio de libre competencia.

## Perímetro de vinculación

Umbral de participación **igual o superior al 25 por 100** —así, «por 100», no «por ciento»— cuando la
vinculación se define por la relación socio-entidad. Coincide en el porcentaje con el art. 18.2 LIS.

## Ninguna regla estadística, y esta vez el silencio está comprobado en los dos escalones

Búsqueda literal sobre el texto íntegro de ambas normas:

| Término | NF 11/2013 (198 pág) | DF 203/2013 (57 pág) |
|---|---|---|
| «mediana» | 25, **todas** «pequeñas y medianas empresas» | 3, todas «medianas empresas» |
| «cuartil» / «intercuartil» | 0 | 0 |
| «medidas estadísticas» | 0 | **0** |
| «rango de valores» | 0 | **0** |

La fila que importa es la última columna. **El Reglamento vizcaíno no contiene el equivalente del art.
17.7 RIS**, que es la norma que en territorio común habilita expresamente el uso de medidas
estadísticas para minimizar el riesgo de error por defectos de comparabilidad.

No es un olvido, y conviene decir por qué: el Reglamento de Bizkaia **no tiene artículo de análisis de
comparabilidad**. Solo regula la documentación (art. 16) y el procedimiento de comprobación (art. 22).
La comparabilidad está en la Norma Foral, art. 42.1, y allí el legislador **no delegó** la cuestión
estadística en el reglamento ni la resolvió él mismo. La arquitectura es distinta de la estatal, y por
eso el hueco existe.

Lo que de ahí se sigue está en la ficha comparada, `forales-habilitacion-medidas-estadisticas`.

## Aplicación en TPIP

1. **Bizkaia es una jurisdicción propia del motor**, código `ES-BI`. No es «España».
2. Su regla de rango es la misma que la de territorio común —ausencia de regla estadística legal— pero
   **la fuente que el informe debe citar es otra**. Esa es toda la razón de esta ficha.
3. Una operación entre una sociedad vizcaína y una de territorio común es, a efectos de este motor,
   **un caso entre dos jurisdicciones**, aunque ambas estén en España.
4. El régimen sancionador propio está en el art. 46, no en el art. 18.13 LIS.

## Límites de esta ficha

- **No se ha leído el art. 43** (obligaciones de documentación) ni el desarrollo del art. 16 del
  Reglamento. La ficha afirma sobre valoración y rango, no sobre documentación.
- **Sin jurisprudencia del TSJ del País Vasco** sobre el art. 42. No se ha buscado.
- **Sin doctrina de la Hacienda Foral de Bizkaia.** Que el Reglamento calle no significa que la
  Inspección vizcaína no use medidas estadísticas de hecho, apoyándose directamente en las Directrices
  de la OCDE. Es la distinción entre ley y práctica, y aquí solo se ha comprobado la ley.
- El texto leído está actualizado a **03/12/2022**. Modificaciones posteriores no comprobadas.
