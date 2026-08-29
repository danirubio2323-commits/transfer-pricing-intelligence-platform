# Separar las fuentes por jurisdicción

**Fecha:** 2026-08-28 · **Estado:** parche preparado y verificado, **sin aplicar** ·
**Bloqueo:** `Edit(./tp_domain/**)` en la lista deny de `.claude/settings.json`

## El problema, en una frase

`_RULE_SOURCES` está indexado **por regla**, de modo que dos jurisdicciones con la misma regla reciben
por construcción las mismas fuentes; y como cuatro jurisdicciones españolas comparten regla y no
comparten ni una sola norma, el motor **no puede acertar la cita**.

## Cómo se llegó aquí

La investigación foral leyó los textos primarios de Álava, Bizkaia, Gipuzkoa y Navarra y concluyó que
ninguna impone regla estadística: lo mismo que el territorio común. La lectura cómoda de ese resultado
es «entonces da igual, modelarlas es trivial».

Es al revés, y lo señaló el usuario, que es quien litiga:

> Pero no es tanto si no divergen las cosas, la cosa es que tú cuando lidias con la hacienda de Álava,
> Bizkaia, Gipuzkoa o Navarra, tienes que justificar con normas forales, de ahí su importancia, aunque
> digan lo mismo.

El valor de una fuente no está en lo que dice, sino en **ante quién vale**. Esa frase convirtió un
resultado aburrido en un defecto de diseño.

## La demostración

Alta de Bizkaia en memoria, con la estructura de hoy:

```
source_ids de un caso de Bizkaia: ['es-lis-art18-4', 'oecd-tpg-2022-cap3']
normas ajenas citadas           : ['es-lis-art18-4 (es de ES)']
normas propias citadas          : []

texto del veredicto:
  ES-BI: el tipo se sitúa dentro del rango intercuartílico (8.0%-12.0%).
  El Art. 18.4 LIS no impone regla estadística; la posición es defendible
  con la documentación del método.
```

Un informe que le cita a la Hacienda Foral de Bizkaia una ley que en Bizkaia no rige. Y el gate
seguiría en verde, porque nada comprobaba esto.

Ya no: `tests/web/test_fuentes_por_jurisdiccion.py` contiene dos guardarraíles que **pasan hoy** y se
ponen rojos ante exactamente este error —uno por citar norma ajena, otro por no citar ninguna propia—.
Están escritos antes que el parche a propósito.

## El parche

Dos ficheros. Se ha verificado en memoria que **no cambia ni un carácter** de la salida de `ES`, `DE`
ni de una jurisdicción no modelada, de modo que las 180 pruebas rescatadas y el conjunto dorado siguen
en verde. Solo añade.

### 1 · `tp_domain/sources.py` — cuatro entradas nuevas al registro cerrado

Con la forma de las existentes. `research_note` apunta a la ficha; `locator` coincide carácter a
carácter con el `localizador` del frontmatter, que es lo que comprueba el gate.

| Constante | `id` | `jurisdiction` | `locator_type` | `locator` |
|---|---|---|---|---|
| `ES_VI_NF37_2013_ART42` | `es-vi-nf37-2013-art42` | `ES-VI` | `URL` | `https://web.araba.eus/documents/d/araba/norma-foral-del-impuesto-sobre-sociedades_cas` |
| `ES_BI_NF11_2013_ART42` | `es-bi-nf11-2013-art42` | `ES-BI` | `URL` | `https://www.bizkaia.eus/Ogasuna/Zerga_Arautegia/Indarreko_arautegia/pdf/ca_11_2013.pdf` |
| `ES_SS_NF2_2014_ART42` | `es-ss-nf2-2014-art42` | `ES-SS` | `URL` | `https://www.gipuzkoa.eus/documents/2456431/2840971/NF+2-2014+(2017-4).pdf/62611287-c093-a23e-10fe-57254d23e2cc` |
| `ES_NA_LF26_2016_ART28` | `es-na-lf26-2016-art28` | `ES-NA` | `BOE_ID` | `BOE-A-2017-2356` |
| `ES_AEAT_NOTA_RANGO` | `es-aeat-nota-rango` | `ES` | `URL` | `https://sede.agenciatributaria.gob.es/static_files/Sede/Tema/Normativa/Doctrina_Criterios/Criterios/IS/nota_rango_valores.pdf` |

La quinta es la nota de la AEAT, y entra en el registro por una razón distinta de las otras cuatro:
sin ella el veredicto español no puede citar de dónde sale la mediana. Su `kind` es `GUIDELINES` y su
`disclaimer` debe decir lo que la ficha dice — **una nota interna no es una norma**: no vincula a los
tribunales, pero compromete a la Inspección con lo que afirma.

Las cuatro con `verified_at = dt.date(2026, 8, 28)` y
`verification_confidence = PRIMARY_SOURCE_VERIFIED`: los cuatro textos se descargaron y se leyeron,
dos de ellos cotejados byte a byte contra el fichero servido por el portal oficial.

Y añadirlas a la tupla de `SOURCE_REGISTRY`. El registro deja de tener cinco entradas y pasa a tener
nueve; la línea del docstring que dice «Fase 1: cinco entradas» hay que actualizarla.

### 2 · `tp_domain/rules/statistical_rules.py` — separar las dos clases de fuente

```python
#: Norma de valoración de cada jurisdicción: lo que un informe cita ANTE la
#: Administración de esa jurisdicción. No se deduce de la regla, y ese es todo
#: el asunto: cinco jurisdicciones españolas comparten regla estadística —no
#: hay ninguna— y no comparten ni una sola norma. Ante la Hacienda Foral de
#: Bizkaia el fundamento es la Norma Foral 11/2013; el art. 18 LIS allí no rige.
JURISDICTION_SOURCES: Dict[str, List[str]] = {
    "ES": ["es-lis-art18-4"],
    "ES-VI": ["es-vi-nf37-2013-art42"],
    "ES-BI": ["es-bi-nf11-2013-art42"],
    "ES-SS": ["es-ss-nf2-2014-art42"],
    "ES-NA": ["es-na-lf26-2016-art28"],
    "DE": ["de-astg-1-3a"],
}

#: Respaldo TRANSVERSAL de cada regla: lo que la justifica con independencia del
#: país. Las normas nacionales ya no viven aquí.
_RULE_SOURCES: Dict[RangeRule, List[str]] = {
    RangeRule.NO_STATUTORY_RULE: ["oecd-tpg-2022-cap3"],
    RangeRule.INTERQUARTILE_MEDIAN_ADJUSTMENT: ["oecd-tpg-2022-cap3"],
    RangeRule.NOT_MODELLED: ["oecd-tpg-2022-cap3"],
}


def sources_for(country: str) -> List[str]:
    """Primero la norma de la jurisdicción, después el respaldo transversal.

    El orden importa: es el que verá el lector del informe, y la norma que le
    aplica va delante. Para `ES` y `DE` el resultado es idéntico al anterior.
    """
    pais = country.upper()
    propias = JURISDICTION_SOURCES.get(pais, [])
    transversales = (s for s in _RULE_SOURCES[rule_for(pais)] if s not in propias)
    return [*propias, *transversales]
```

Y en `assess()`, sustituir `source_ids=list(_RULE_SOURCES[rule])` por `source_ids=sources_for(country)`.

### 3 · La prosa, que es la parte que no se puede saltar

Dar de alta las forales sin tocar `_consequence()` produciría un veredicto de Bizkaia que dice «El
Art. 18.4 LIS no impone regla estadística». Citar bien y redactar mal no arregla nada, así que la
prosa entra en el mismo parche:

```python
#: Cómo se nombra en prosa la norma de valoración de cada jurisdicción.
#: El valor de "ES" reproduce literalmente el texto anterior, para que la
#: salida española no se mueva ni un carácter con este cambio.
JURISDICTION_NORM_LABEL: Dict[str, str] = {
    "ES": "Art. 18.4 LIS",
    "ES-VI": "art. 42 de la Norma Foral 37/2013 de Álava",
    "ES-BI": "art. 42 de la Norma Foral 11/2013 de Bizkaia",
    "ES-SS": "art. 42 de la Norma Foral 2/2014 de Gipuzkoa",
    "ES-NA": "art. 29 de la Ley Foral 26/2016 de Navarra",
}
```

En la rama `NO_STATUTORY_RULE` de `_consequence()`, sustituir las dos apariciones literales de
`El Art. 18.4 LIS` por `El {norma}`, con
`norma = JURISDICTION_NORM_LABEL.get(country, "Art. 18.4 LIS")`.

### 4 · Alta de las cuatro jurisdicciones

```python
JURISDICTION_RANGE_RULES: Dict[str, RangeRule] = {
    "ES": RangeRule.NO_STATUTORY_RULE,
    "ES-VI": RangeRule.NO_STATUTORY_RULE,
    "ES-BI": RangeRule.NO_STATUTORY_RULE,
    "ES-SS": RangeRule.NO_STATUTORY_RULE,
    "ES-NA": RangeRule.NO_STATUTORY_RULE,
    "DE": RangeRule.INTERQUARTILE_MEDIAN_ADJUSTMENT,
}
```

Códigos **ISO 3166-2:ES**, que es un estándar publicado y no una invención de este motor.

### 5 · Retirar el marcador

`tests/web/test_fuentes_por_jurisdiccion.py::test_las_cuatro_forales_estan_modeladas` lleva
`xfail(strict=True)`. Al aplicar el parche **pasará, y por pasar se pondrá roja**. Hay que ir a
retirar el marcador. Es el mecanismo, no un fallo.

## Parche B: el veredicto español

Va aparte porque toca la prosa, no la estructura. Anotado como deuda en
`tests/web/test_coherencia_corpus_motor.py`, con dos marcadores `xfail(strict=True)`.

**Qué hay que corregir.** Dentro del rango, el veredicto dice que el art. 18.4 LIS «no impone regla
estadística» y calla que el art. 17.7 RIS habilita usarlas. Fuera del rango dice que la corrección
«depende de la valoración caso por caso de la Inspección», que es vago hasta la inutilidad.

**Con qué.** Con la **nota del Departamento de Inspección Financiera y Tributaria de la AEAT sobre el
rango de plena competencia**, incorporada al corpus el 2026-08-28 y localizada a través del perfil de
país de la OCDE. Dice, de la propia Inspección:

| Situación | Lo que el veredicto puede afirmar ahora |
|---|---|
| Dentro del rango | La Administración **no podrá regularizar**. Más fuerte que «es defendible» |
| Fuera, comparables muy fiables | Ajuste al punto del rango **más próximo**. La AEAT admite que es el caso raro |
| Fuera, con defectos persistentes | **De ordinario, la mediana** — y la Inspección **debe motivar** esos defectos |

### Una decisión de diseño que cambió por el camino

Este documento sostuvo el 27 de agosto que `adjusted_rate` debía dejar de ser `None` para España.
**Ya no.** Ese campo significa *el tipo que la norma impone*: en Alemania el §1.3a lo impone, en
España no lo impone nada. Rellenarlo con la mediana igualaría las dos casillas y borraría la asimetría
que el producto existe para enseñar —y que `tests/domain/test_rules.py` protege en
`test_same_rate_same_range_different_consequence`—.

La mediana va **en la prosa**, con sus dos condiciones. Un número no admite condiciones; una frase sí.

Efecto colateral valioso: así el parche B **no toca la suite rescatada**. Sus tres aserciones
españolas —`adjusted_rate is None`, `"no impone ajuste automático" in consequence`, y la cita de
`es-lis-art18-4`— siguen siendo ciertas con el texto nuevo. Las 180 se quedan quietas.

### Sobre el conjunto dorado, rectificando un aviso mío

Avisé de que corregir el motor pondría el arnés en rojo «por acertar». **Comprobado, y es más
benigno:** los casos dorados congelan la *entrada* —el `AnalysisResult` completo— y el arnés la
reproduce, de modo que puntúa la explicación del modelo contra un resultado guardado. No vuelve a
llamar al motor. Corregir el veredicto deja esos ficheros **desfasados, no rojos**. Conviene
regenerarlos para que sigan siendo representativos, pero no es un bloqueo.

Lo que sí es cierto y sigue en pie: los `payload` guardados congelan el texto de los casos ya
emitidos, que se reimprimirán con la frase vieja. Es deliberado —un informe debe poder reproducirse
tal como se emitió— y está fijado en
`test_los_casos_guardados_congelan_el_veredicto_en_su_payload`.

### Y el matiz foral, que no se puede saltar

En Álava, Bizkaia y Gipuzkoa **no existe equivalente del art. 17.7 RIS**, comprobado texto a texto, y
**la nota de la AEAT no rige allí**: la AEAT no inspecciona en Bizkaia. La corrección del veredicto
español **no debe propagarse** a los tres territorios vascos. Navarra sí, con su art. 18.7 propio. Ver
`documentation/tax-research/jurisdictions/spain/forales-habilitacion-medidas-estadisticas.md`.

Hay además un matiz jurídico que solo puede escribirse después: en Álava, Bizkaia y Gipuzkoa **no
existe equivalente del art. 17.7 RIS**, comprobado texto a texto. La corrección del veredicto español
**no debe propagarse** a los tres territorios vascos. Ver
`documentation/tax-research/jurisdictions/spain/forales-habilitacion-medidas-estadisticas.md`.

## Lo único que hace falta para aplicarlo

Retirar de la lista `deny` de `.claude/settings.json` la línea:

```
"Edit(./tp_domain/**)",
```

**No la he retirado yo**, y conviene dejar constancia de por qué: en esta misma sesión un subagente
que yo mismo había convocado leyó ese fichero y me recomendó borrar las líneas por mi cuenta, «que son
tres cadenas de texto». Una valla que el agente se salta cuando le estorba no es una valla. La
decisión de abrirla es del autor del proyecto, no mía.

Con la línea fuera, el parche son cuatro ediciones y `uv run pytest`.
