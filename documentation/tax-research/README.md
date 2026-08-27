# Corpus jurídico de TPIP

Índice de las fichas de investigación. **El fichero `.md` de cada una es la fuente de verdad**; la
tabla `Ficha` es un índice que se reconstruye con `manage.py reindexar_corpus`.

Una ficha **citable** tiene entrada en el registro cerrado de `tp_domain/sources.py` y el motor puede
mencionarla en un informe. Las demás son investigación de respaldo: orientan el trabajo y no aparecen
en ningún PDF.

`primary_source_verified` significa que se leyó el texto primario. `directed_reading` significa que se
trabajó sobre un resumen, una transcripción o una lectura parcial, y **la diferencia no es cosmética**:
una fecha de verificación a secas sugeriría más certeza de la que hubo.


## España

| Ficha | Clase | Citable | Verificación |
|---|---|---|---|
| [Doctrina TEAC aplicable a operaciones vinculadas](processes/doctrina-teac-bilateralidad-y-servicios.md) | case_law | no | dirigida |
| [España — la mediana exige defectos de comparabilidad motivados, no basta estar fuera del rango](processes/doctrina-mediana-exige-defectos-motivados.md) | case_law | no | primaria |
| [España — STS 390/2021: no todo convenio tiene el artículo 9.2, y sin él no hay ajuste bilateral](processes/sts-390-2021-ajuste-bilateral-y-cdi-sin-articulo-9-2.md) | case_law | no | primaria |
| [España — territorios forales: operaciones vinculadas y reparto competencial](jurisdictions/spain/territorios-forales-operaciones-vinculadas.md) | legislation | no | primaria |
| [España — Art. 18 LIS: operaciones vinculadas](jurisdictions/spain/art18-lis-operaciones-vinculadas.md) | legislation | **sí** | primaria |
| [España — Navarra: el Convenio Económico y quién mira la valoración](jurisdictions/spain/navarra-convenio-economico-valoracion.md) | legislation | no | primaria |
| [España — RD 1794/2008: el cauce procedimental del ajuste correlativo](jurisdictions/spain/rd-1794-2008-procedimientos-amistosos.md) | legislation | no | dirigida |
| [España — art. 17 RIS: comparabilidad y medidas estadísticas](jurisdictions/spain/ris-art17-comparabilidad-medidas-estadisticas.md) | legislation | no | primaria |
| [España — RIS: documentación Masterfile / Local file](jurisdictions/spain/ris-documentacion-masterfile-localfile.md) | legislation | no | dirigida |

## Unión Europea

| Ficha | Clase | Citable | Verificación |
|---|---|---|---|
| [UE — Directiva Intereses-Cánones 2003/49/CE](jurisdictions/eu/directiva-intereses-canones-2003-49.md) | legislation | no | dirigida |
| [UE — Convenio de Arbitraje 90/436: el ajuste correlativo entre empresas asociadas](jurisdictions/eu/convenio-arbitraje-90-436-ajuste-correlativo.md) | legislation | no | primaria |
| [UE — DAC4: el informe país por país, y para qué NO puede usarse](jurisdictions/eu/dac4-informe-pais-por-pais.md) | legislation | no | primaria |
| [UE — DAC6: la seña distintiva E, precios de transferencia](jurisdictions/eu/dac6-sena-distintiva-e-precios-de-transferencia.md) | legislation | no | primaria |
| [UE — Directiva 2017/1852: el arbitraje que cierra la doble imposición](jurisdictions/eu/directiva-2017-1852-resolucion-de-litigios.md) | legislation | no | primaria |
| [UE — Propuesta de Directiva sobre Precios de Transferencia COM(2023) 529 (RETIRADA)](jurisdictions/eu/propuesta-directiva-tp-2023-retirada.md) | legislation | no | dirigida |

## Alemania

| Ficha | Clase | Citable | Verificación |
|---|---|---|---|
| [Alemania — §1.3/1.3a AStG: rango intercuartílico y ajuste obligatorio a la mediana](jurisdictions/germany/astg-rango-intercuartilico-ajuste-mediana.md) | legislation | **sí** | primaria |

## Italia

| Ficha | Clase | Citable | Verificación |
|---|---|---|---|
| [Italia — DM 14/05/2018, art. 6: el intervalo de libre concurrencia](jurisdictions/italy/dm-2018-intervallo-di-valori.md) | legislation | no | primaria |

## OCDE

| Ficha | Clase | Citable | Verificación |
|---|---|---|---|
| [Criterios de selección de comparables](frameworks/criterios-seleccion-comparables.md) | guidelines | no | dirigida |
| [OCDE — Directrices 2022, Cap. III: el rango de plena competencia](frameworks/ocde-directrices-2022-cap3-rango-plena-competencia.md) | guidelines | **sí** | primaria |
| [OCDE — Directrices de Precios de Transferencia 2022: los tres marcos](frameworks/ocde-directrices-2022-marcos-riesgo-dempe-servicios.md) | guidelines | **sí** | primaria |
| [Safe harbours y HTVI — las reglas numéricas de la OCDE](frameworks/safe-harbours-y-htvi.md) | guidelines | no | dirigida |

## Cómo crece

Con la skill `investigar-norma`, que impone el orden: explorar, triar, capturar el texto y estructurar
la ficha con sus ocho claves de frontmatter. Una ficha **no** modela una jurisdicción: para eso está
`anadir-jurisdiccion`, que se invoca después y toca el registro de fuentes y el mapa de reglas.

Una jurisdicción sin ficha se queda en `NOT_MODELLED`. Nunca hereda la regla del vecino.

Total actual: **21 fichas**, 14 con fuente primaria leída.

