---
clase: guidelines
confianza_verificacion: primary_source_verified
enlaces:
- jurisdictions/spain/ris-art17-comparabilidad-medidas-estadisticas
- jurisdictions/spain/art18-lis-operaciones-vinculadas
- processes/doctrina-mediana-exige-defectos-motivados
- jurisdictions/eu/jtpf-2017-uso-de-comparables
- jurisdictions/spain/oecd-perfil-pais-espana-2025
- frameworks/ocde-directrices-2022-cap3-rango-plena-competencia
fecha_creacion: 2026-08-28
fuente_primaria: Agencia Estatal de Administración Tributaria, Departamento de Inspección
  Financiera y Tributaria, «Nota sobre diversas cuestiones relativas al rango de plena
  competencia en materia de precios de transferencia»
id_fuente: es-aeat-nota-rango
jurisdiccion: ES
localizador: https://sede.agenciatributaria.gob.es/static_files/Sede/Tema/Normativa/Doctrina_Criterios/Criterios/IS/nota_rango_valores.pdf
origen: Descarga y lectura íntegra del PDF de la sede electrónica de la AEAT, 13 páginas,
  2026-08-28. Localizada a través del enlace del perfil de país de la OCDE
pinpoint: Apartado 5 (selección del punto más apropiado del rango) y apartado 6 (conclusiones);
  anexo con caso práctico sobre 23 comparables
rango_normativo: Criterio administrativo del Departamento de Inspección
tipo: Práctica inspectora sobre el rango y el punto de ajuste
tipo_localizador: url
titulo: España — la nota de la AEAT sobre el rango de plena competencia
usar_en: tp_domain/rules/statistical_rules.py, redacción del veredicto español
verificada_el: 2026-08-28
---

# España — la nota de la AEAT sobre el rango de plena competencia

**Fuente primaria:** Agencia Tributaria, **Departamento de Inspección Financiera y Tributaria**,
«Nota sobre diversas cuestiones relativas al rango de plena competencia en materia de precios de
transferencia». PDF de 13 páginas publicado en la sede electrónica, descargado y leído íntegro.

## Por qué esta ficha importa más que ninguna otra del corpus

La revisión adversarial de este proyecto dejó un reproche concreto y bien fundado: **el motor modela
la ley e ignora la práctica inspectora**, de modo que puede estar dando falsa tranquilidad a un
usuario español. Se dio por hecho que esa práctica no estaba escrita en ningún sitio citable.

Sí lo está. La AEAT la publicó, y el propio perfil de país de la OCDE remite a ella:

> The Spanish Tax Administration has published in its website **a note addressed to tax auditors**
> with further elaboration on this topic.

Es la nota que los inspectores usan. Deja de ser «lo que suele hacer Hacienda» para ser una fuente
con localizador oficial.

## Lo que la nota reconoce de entrada

Empieza admitiendo el punto de partida, sin rodeos:

> La Ley 27/2014 (…) **no contiene ningún precepto que se refiera expresamente al rango de valores**
> en materia de precios de transferencia.

Y a continuación transcribe el art. 17.7 RIS como la única base reglamentaria. Es decir: la AEAT
comparte el diagnóstico del que partía este corpus. Lo que añade es qué hace con él.

## La regla, en dos escalones que no hay que mezclar

### Dentro del rango: no se regulariza

> la Administración **no podrá regularizar** si el valor declarado por el contribuyente se encuentra
> dentro de ese rango.

Dicho por la propia Inspección. Es una afirmación fuerte y utilizable.

### Fuera del rango: se ajusta, y el punto depende de la calidad del rango

La nota separa dos escenarios del párrafo 3.62 de las Directrices:

| Escenario | Punto de ajuste |
|---|---|
| El rango comprende «resultados **muy fiables y relativamente iguales**» | El punto del rango **más próximo** al valor declarado |
| Persisten **defectos de comparabilidad** no identificables ni cuantificables | Medidas de tendencia central: **la mediana** |

Y entonces dice cuál de los dos es el habitual, que es el dato que cambia el panorama:

> Como ya se ha apuntado, **en la práctica es muy infrecuente** disponer de un rango de valores que
> comprenda resultados muy fiables y relativamente iguales (…). **Lo usual será** que el rango no
> comprenda resultados muy fiables y relativamente iguales.

De modo que el escenario por defecto en la práctica española es el segundo:

> si dicho valor declarado está fuera del rango intercuartil (…) **de ordinario, procederá ajustar al
> valor de la mediana**.

## El límite que la propia AEAT se pone

Y aquí está lo que convierte la nota en material defensivo, no solo en aviso:

> debe tenerse presente que, **para ajustar al valor de la mediana**, aun cuando no se puedan
> identificar y cuantificar los defectos de comparabilidad, **será necesario que la Administración
> haga referencia, atendiendo a las circunstancias del caso, a la existencia de dichos defectos** de
> comparabilidad.

La Inspección se autoimpone la carga de motivar. Es exactamente lo que la Audiencia Nacional exigió en
la SAN 1072/2019 (caso IKEA Ibérica) y lo que el TSJ de Madrid confirmó en 2026. **Doctrina judicial y
criterio administrativo coinciden**, y eso deja poco margen: un ajuste a la mediana sin referencia
motivada a defectos de comparabilidad contradice a la vez a los tribunales y a la nota interna de
quien lo practica.

## El estrechamiento del rango, y que los tribunales lo aceptan

> Es **práctica generalizada, que ha sido aceptada por los tribunales**, la utilización de los
> resultados incluidos dentro del 1er y 3er cuartil, excluyendo los que se encuentran fuera de dichos
> límites.

El rango intercuartílico, que la Ley española no nombra, es la práctica normal y validada. Este motor
calcula precisamente sobre P25-P75: la nota confirma que la convención es la correcta para España.

## La vía de escape del contribuyente

La nota recoge la recomendación d) del informe del Foro Conjunto de Precios de Transferencia de la UE
y añade cómo se usa:

> si de la verificación del análisis funcional se desprende que la entidad vinculada realiza **más
> funciones o de mayor valor** (…) o asume mayores riesgos o dispone de más activos o más valiosos,
> que los comparables utilizados, **podría llevar a elegir un punto en la parte alta del rango** en
> vez de acudir directamente a la mediana. O un punto en la parte baja en la situación opuesta.

Es decir: la mediana es el punto de referencia, no un destino forzoso, y lo que la desplaza es
**prueba funcional**. La misma clave que decidió los dos casos de la ficha de doctrina.

## Aplicación en TPIP, y es un cambio de calibración

1. **El veredicto español estaba mal en las dos direcciones, y ahora se puede escribir bien.** Decía
   que fuera del rango «la corrección valorativa depende de la valoración caso por caso de la
   Inspección». Es vago hasta la inutilidad. Lo correcto: **de ordinario se ajusta a la mediana**, y
   el contribuyente tiene dos argumentos concretos contra ese ajuste —falta de motivación de los
   defectos, y análisis funcional que desplace el punto—.
2. **`adjusted_rate` para España se queda en `None`, a propósito.** La tentación era ponerle la
   mediana: es lo que de ordinario ocurrirá. Pero ese campo significa *el tipo que la norma impone*, y
   en España no lo impone ninguna. Rellenarlo igualaría la casilla española con la alemana, donde el
   §1.3a sí lo impone, y el informe perdería la única distinción que de verdad importa. **La mediana
   se dice en la prosa**, con sus dos condiciones —que persistan defectos de comparabilidad y que la
   Inspección los motive—, porque un número no admite condiciones y una frase sí.
3. **Dentro del rango, el veredicto puede afirmar más de lo que afirmaba.** No solo «es defendible»:
   la propia Inspección declara que **no podrá regularizar**.
4. **Se cierra el reproche del pase adversarial.** El motor ya no ignora la práctica: la cita.
5. **Nada de esto se traslada a los territorios forales vascos.** Esta nota es de la AEAT, y la AEAT
   no inspecciona en Bizkaia. Ver `jurisdictions/spain/forales-habilitacion-medidas-estadisticas`.

### ⚠️ Conflicto Doctrinal / Evolución de Criterio

No hay conflicto entre esta nota y la doctrina judicial: **convergen** en exigir motivación de los
defectos. La tensión, si acaso, es de grado: la nota presume que el escenario ordinario es el de
defectos persistentes —y por tanto la mediana—, mientras la SAN 1072/2019 anuló un ajuste a la mediana
por no estar motivados. Ambas cosas caben juntas si se lee que la motivación es exigible **aunque el
escenario sea el ordinario**, que es justamente lo que la nota dice.

## Límites de esta ficha

- **La nota no lleva fecha visible en el documento.** No se ha podido determinar cuándo se publicó ni
  si ha sido revisada. El perfil de país de la OCDE de julio de 2025 la enlaza como vigente, y esa es
  toda la datación disponible. Es el límite más serio.
- **Una nota interna no es una norma.** No vincula a los tribunales y no crea derecho. Su valor es
  doble y distinto del de una ley: describe qué hará la Inspección, y compromete a la Inspección con
  lo que dice.
- **El anexo con el caso práctico de 23 comparables no se ha analizado en detalle.** Puede contener
  criterios de cálculo relevantes para el motor.
- No se ha comprobado si existe **nota equivalente en las Haciendas Forales**. Sería la pieza que
  faltaría para cerrar el mapa foral, y es lo primero que habría que buscar.
