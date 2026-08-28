---
clase: legislation
confianza_verificacion: primary_source_verified
enlaces:
- jurisdictions/spain/forales-habilitacion-medidas-estadisticas
- jurisdictions/spain/navarra-convenio-economico-valoracion
- jurisdictions/spain/ris-art17-comparabilidad-medidas-estadisticas
- jurisdictions/spain/art18-lis-operaciones-vinculadas
- processes/doctrina-mediana-exige-defectos-motivados
fecha_creacion: 2026-08-28
fuente_primaria: Ley Foral 26/2016, de 28 de diciembre, del Impuesto sobre Sociedades
  (Navarra), arts. 28 y 29; Decreto Foral 114/2017, de 20 de diciembre, por el que
  se aprueba el Reglamento del Impuesto sobre Sociedades, art. 18
id_fuente: es-na-lf26-2016-art28
jurisdiccion: ES-NA
localizador: BOE-A-2017-2356
origen: Lectura del texto consolidado del BOE (arts. 28 y 29 íntegros) y descarga y
  lectura del Reglamento DF 114/2017 desde navarra.es, 53 páginas, 2026-08-28
pinpoint: Art. 28.1 a 28.4 y art. 29.1 a 29.3 de la LF 26/2016; art. 18.7 del Reglamento
  aprobado por DF 114/2017 (medidas estadísticas)
rango_normativo: Ley Foral y Decreto Foral
tipo: Regla de valoración de una jurisdicción foral
tipo_localizador: boe_id
titulo: 'Navarra — LF 26/2016 y art. 18.7 del Reglamento: la habilitación estadística
  que el País Vasco no tiene'
usar_en: tp_domain/rules/statistical_rules.py, informe de análisis
verificada_el: 2026-08-28
---

# Navarra — LF 26/2016, arts. 28 y 29

**Fuente primaria:** Ley Foral 26/2016, de 28 de diciembre, del Impuesto sobre Sociedades, texto
consolidado del BOE `BOE-A-2017-2356`, arts. 28 y 29 leídos íntegros. Reglamento aprobado por Decreto
Foral 114/2017, de 20 de diciembre, PDF oficial de `navarra.es`, leído íntegro.

Navarra **no es un cuarto territorio vasco**. Su régimen se rige por el Convenio Económico, no por el
Concierto, y su Ley Foral del Impuesto sobre Sociedades sigue una línea de redacción distinta de la de
Álava, Bizkaia y Gipuzkoa. Esta ficha documenta en qué se aparta, porque la diferencia resultó ser la
más importante de toda la investigación foral.

## Estructura, que ya difiere

Donde los tres territorios históricos concentran todo en un art. 42, Navarra separa:

| | Navarra |
|---|---|
| Art. 28 | Concepto de personas o entidades vinculadas **y reglas de valoración** |
| Art. 29 | Métodos, naturaleza de las rentas y procedimiento |

## La regla de valoración (art. 28.2)

> Las operaciones efectuadas entre personas o entidades vinculadas se valorarán por su **valor de
> mercado**.

Nótese: **«valor de mercado»**, como el art. 18.1 LIS, y no «valor **normal** de mercado» como los
tres territorios vascos. Navarra sigue aquí la terminología estatal posterior a 2014.

## Los métodos (art. 29.1)

Los cinco, con la letra e) llamada «margen neto **del conjunto de operaciones**» —como los vascos, no
como el «margen neto operacional» del art. 18.4 LIS—. Pero el criterio de elección es el **estatal
posterior a 2015**, no el foral vasco:

> La elección del método de valoración **tendrá en cuenta, entre otras circunstancias, la naturaleza
> de la operación vinculada, la disponibilidad de información fiable y el grado de comparabilidad**
> entre las operaciones vinculadas y no vinculadas.

Es literalmente el párrafo del art. 18.4 LIS. Navarra es, en este punto, un texto híbrido: métodos con
nombre viejo, criterio de elección nuevo.

Cierra con la misma cláusula abierta.

## Y aquí está el hallazgo

El Reglamento navarro **sí tiene** artículo de análisis de comparabilidad —art. 18, «Determinación del
valor de mercado de las operaciones vinculadas: análisis de comparabilidad»—, espejo del art. 17 RIS.
Y su apartado 7 dice:

> Cuando, a pesar de no existir datos suficientes, se haya podido determinar un **rango de valores**
> que cumpla razonablemente el principio de libre competencia, teniendo en cuenta el proceso de
> selección de comparables y las limitaciones de la información disponible, **se podrán utilizar
> medidas estadísticas para minimizar el riesgo de error provocado por defectos en la
> comparabilidad**.

Es la misma habilitación del **art. 17.7 RIS**, con la misma redacción. Navarra la tiene. Los tres
territorios vascos, comprobado texto a texto, **no**.

Esto parte el territorio español en dos bloques justo en la cuestión que este motor modela. El mapa
completo está en `forales-habilitacion-medidas-estadisticas`.

## El resto del art. 28 y del art. 29

- **Umbral socio-entidad: 25 por 100** (art. 28.1, último párrafo). Coincide con todos los demás.
- **Vinculación administrativa recíproca** (art. 28.4): comprobado el valor, «la Administración
  tributaria quedará vinculada por dicho valor en relación con el resto de personas o entidades
  vinculadas». Es la regla de bilateralidad **interna a Navarra**; no obliga a la AEAT ni a las
  Haciendas Forales vascas.
- **Ajuste secundario** (art. 29.2), con el mismo tratamiento socio-entidad que el art. 18.11 LIS,
  remitiendo al art. 28.c) de la Ley Foral del IRPF en lugar de al art. 25.1.d) de la Ley 35/2006.
- **Tasación pericial contradictoria** (art. 29.3.2.º): Navarra la conserva expresamente como vía
  frente a la corrección valorativa. El art. 18.12.6.º LIS, en cambio, **excluye** los arts. 57.2 y
  135 LGT en la comprobación de valor de operaciones vinculadas. Es una diferencia procedimental real
  y favorable al contribuyente navarro.

## Aplicación en TPIP

1. Jurisdicción propia, código `ES-NA`.
2. **Es la única jurisdicción foral cuya posición jurídica sobre el rango coincide con la de
   territorio común en los dos escalones**, ley y reglamento. Ante la Hacienda Foral de Navarra, la
   doctrina de la SAN 1072/2019 sobre defectos de comparabilidad motivados es argumentable por
   analogía normativa —misma habilitación reglamentaria—, cosa que en Bizkaia no lo es.
3. La cita, aun así, es el art. 18.7 del DF 114/2017, **nunca** el art. 17.7 RIS.
4. La tasación pericial contradictoria es material para la sección de riesgos de un informe navarro.

## Límites de esta ficha

- **Convenio Económico no releído aquí**: está en `navarra-convenio-economico-valoracion`.
- **Arts. 30 a 32** de la Ley Foral (documentación, infracciones, sanciones) **no leídos**.
- **Sin jurisprudencia del TSJ de Navarra** ni doctrina del Organismo Jurídico-Tributario. No se ha
  buscado.
- La identidad entre el art. 18.7 navarro y el art. 17.7 estatal **sí se ha cotejado carácter a
  carácter**: 325 caracteres, coincidencia exacta descontando los espacios espurios que introduce el
  extractor de texto del PDF. Coinciden además en el número de apartado. No es un límite: se anota
  aquí porque el resto de esta sección lo son y la asimetría sería confusa.
