---
clase: legislation
confianza_verificacion: primary_source_verified
enlaces:
- frameworks/ocde-directrices-2022-cap3-rango-plena-competencia
- jurisdictions/spain/art18-lis-operaciones-vinculadas
- jurisdictions/germany/astg-rango-intercuartilico-ajuste-mediana
fecha_creacion: 2026-08-21
fuente_primaria: Decreto del Ministro dell'Economia e delle Finanze de 14 de mayo
  de 2018, art. 6 (linee guida del art. 110, comma 7, TUIR)
id_fuente: it-dm-2018-art6
jurisdiccion: IT
localizador: https://www.gazzettaufficiale.it/eli/id/2018/05/23/18A03544/sg
origen: Lectura directa del texto oficial en la Gazzetta Ufficiale, 2026-08-21
pinpoint: Art. 6 — intervallo di valori conformi al principio di libera concorrenza
  (commi 1 a 3); art. 4, comma 3 — preferencia entre métodos
rango_normativo: Decreto ministerial
tipo: Normativa estatal, desarrollo reglamentario del art. 110.7 TUIR
tipo_localizador: url
titulo: 'Italia — DM 14/05/2018, art. 6: el intervalo de libre concurrencia'
usar_en: tp_domain/rules/statistical_rules.py, comparador de jurisdicciones
verificada_el: 2026-08-21
---

# Italia — DM 14/05/2018, art. 6: el intervalo de libre concurrencia

**Fuente primaria:** Decreto del Ministro dell'Economia e delle Finanze de 14 de mayo de 2018,
publicado en la *Gazzetta Ufficiale* Serie Generale n. 118 de 23 de mayo de 2018 (ref. 18A03544).
**Alcance de esta ficha:** el art. 6 completo, más el art. 4, comma 3, por el contraste que ofrece.
Los arts. 1, 2, 5, 8 y 9 quedan sin desarrollar.
**Usar en:** `tp_domain/rules/statistical_rules.py`

El decreto desarrolla el art. 110, comma 7, del TUIR, tras la reforma del art. 59 del
Decreto-legge 24 aprile 2017, n. 50, convertido por la Legge 21 giugno 2017, n. 96. El último
inciso de ese comma 7 es el que habilita al Ministro a fijar, «sulla base delle migliori pratiche
internazionali», las líneas guía para su aplicación.

## El dato que define la regla italiana

**Italia sí codificó qué pasa con el rango, y no lo resolvió como Alemania.** El art. 6 tiene tres
apartados y cada uno decide una cosa distinta.

### Comma 1 — cuándo el intervalo es el intervalo

> 1. Si considera conforme al principio di libera concorrenza l'intervallo di valori risultante
> dall'indicatore finanziario selezionato in applicazione del metodo più appropriato ai sensi
> dell'art. 4, **qualora gli stessi siano riferibili a un numero di operazioni non controllate,
> ognuna delle quali risulti parimenti comparabile** all'operazione controllata.

La condición es la comparabilidad **igual** de cada observación —*parimenti comparabile*—, no un
número mínimo de comparables ni un umbral de dispersión.

### Comma 2 — dentro del intervalo

> 2. Un'operazione controllata (…) si considera realizzata in conformità al principio di libera
> concorrenza, qualora il relativo indicatore finanziario sia compreso nell'intervallo di cui al
> comma 1.

Coincide con el párrafo 3.60 de las Directrices de la OCDE: dentro, no hay ajuste.

### Comma 3 — fuera del intervalo, y aquí está la diferencia

> 3. Se l'indicatore finanziario (…) non rientra nell'intervallo di libera concorrenza,
> l'amministrazione finanziaria effettua una rettifica **al fine di riportare il predetto indicatore
> all'interno dell'intervallo** di cui al comma 1, fatti salvi il diritto per l'impresa associata di
> presentare elementi che attestino che l'operazione controllata soddisfa il principio di libera
> concorrenza, e la potestà per l'amministrazione finanziaria di non tenere conto di tali elementi
> adducendo idonea motivazione.

El ajuste devuelve el indicador **al interior del intervalo**. No a la mediana. El decreto **no
nombra la mediana en ningún punto**, ni el rango intercuartílico, ni ningún percentil.

Y el derecho de alegación del contribuyente está expresamente reconocido —igual que en el párrafo
3.61 de la OCDE—, con una precisión que la OCDE no hace: la Administración puede **no tener en
cuenta** esos elementos, pero solo *adducendo idonea motivazione*. La motivación es requisito, no
cortesía.

## Tres regímenes sobre la misma base

Esta es la razón por la que Italia merecía entrar en el motor: no repite a nadie.

| | Dentro del rango | Fuera del rango |
|---|---|---|
| **España** (art. 18.4 LIS) | Sin ajuste | **Sin regla estadística.** Corrección valorativa caso por caso de la Inspección |
| **Alemania** (§1.3a AStG) | Sin ajuste | Ajuste **a la mediana** por defecto, salvo prueba en contrario |
| **Italia** (art. 6 DM 2018) | Sin ajuste | Ajuste **al interior del intervalo**, salvo elementos del contribuyente que la Administración solo puede descartar motivadamente |

Los tres se apoyan en el mismo párrafo 3.62 de las Directrices, que deja la tendencia central como
**opción** y no como regla. Alemania ejerce esa opción y la endurece; Italia no la ejerce y se queda
en el borde del intervalo; España no legisla. Es la mejor ilustración de por qué una jurisdicción
sin ficha se queda en `NOT_MODELLED`: de la base común no se deduce qué hizo con ella un tercer
Estado.

## El otro contraste: Italia sí ordena los métodos

El art. 4, comma 1, del decreto adopta la regla del método más apropiado, con cuatro criterios
—fortalezas y debilidades de cada método, adecuación a las características económicamente
relevantes, disponibilidad de información fiable y grado de comparabilidad—.

Pero el **comma 3** añade lo que el art. 18.4 LIS deliberadamente no tiene:

> 3. Se (…) può essere applicato con uguale grado di affidabilità un metodo descritto dalle lettere
> da a) a c) del comma 2, e un metodo descritto dalle successive lettere d) ed e), **il metodo
> descritto dalle citate lettere da a) a c) è preferibile**. In ogni caso, se (…) può essere
> applicato con lo stesso grado di affidabilità il metodo del confronto di prezzo (…) e ogni altro
> metodo (…), **il metodo del confronto di prezzo è da preferire**.

Es decir: **a igual fiabilidad**, los métodos tradicionales (confronto di prezzo, prezzo di
rivendita, costo maggiorato) se prefieren a los transaccionales (margine netto, ripartizione degli
utili); y el *confronto di prezzo* —el CUP— se prefiere sobre todos.

La condición «a igual fiabilidad» hace que no sea una jerarquía formal al viejo estilo, pero es más
de lo que dice la norma española, que no ordena nada. Un mismo caso puede exigir justificar la
elección del método con más fuerza en Italia que en España.

El comma 6 cierra con una garantía notable: si la empresa aplicó un método conforme a los commi 1 a
5, la comprobación de la Administración **debe basarse en el método aplicado por la empresa**.

## Comparabilidad (art. 3)

Una operación no controlada es comparable cuando no hay diferencias significativas que incidan de
manera relevante en el indicador financiero, o cuando, habiéndolas, pueden practicarse ajustes de
comparabilidad precisos que las eliminen o reduzcan significativamente.

Los factores a identificar son cinco: términos contractuales; funciones desempeñadas, con activos
utilizados y riesgos asumidos —incluido cómo se conectan con la generación de valor del grupo—;
características de los bienes y servicios; circunstancias económicas y condiciones de mercado; y
estrategias empresariales.

## Servicios de bajo valor añadido (art. 7)

Italia incorpora el enfoque simplificado con **margen del 5 %** sobre la totalidad de los costes
directos e indirectos, previa documentación. Se consideran de bajo valor añadido los servicios de
naturaleza de apoyo, ajenos a la actividad principal del grupo, que no exigen ni contribuyen a crear
intangibles únicos y valiosos.

## Aplicación en TPIP

**Esta ficha no se puede trasladar al motor con el vocabulario que hoy existe.** `RangeRule` tiene
tres valores —`NO_STATUTORY_RULE`, `INTERQUARTILE_MEDIAN_ADJUSTMENT` y `NOT_MODELLED`— y la regla
italiana no es ninguno de ellos. Añadir Italia exige:

1. Un valor nuevo en `RangeRule`, del tipo «ajuste al interior del intervalo», con su lógica de
   evaluación: el punto de destino es el borde del rango, no la mediana.
2. La entrada `it-dm-2018-art6` en el registro cerrado de `tp_domain/sources.py`, con localizador
   `url` —el permalink de la Gazzetta resuelve por sí solo— y esta fecha de verificación.
3. `IT` en `JURISDICTION_RANGE_RULES`.

En ese orden y no en otro: la ficha primero, el registro después, la regla al final.

### ⚠️ Conflicto Doctrinal / Evolución de Criterio

No hay conflicto entre el art. 6 y el párrafo 3.62 de las Directrices: el decreto ejerce una de las
opciones que aquel deja abiertas. Lo que sí hay es una **divergencia práctica frecuente**: parte de
la práctica italiana emplea el rango intercuartílico por remisión genérica a las Directrices, pese a
que el decreto habla de *intervallo* de observaciones *parimenti comparabili* y **no menciona
percentiles**. Esa distancia entre el texto y el uso conviene tenerla presente antes de dar por
supuesto que en Italia el rango es intercuartílico.
