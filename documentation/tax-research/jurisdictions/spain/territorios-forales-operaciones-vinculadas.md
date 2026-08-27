---
clase: legislation
confianza_verificacion: primary_source_verified
enlaces:
- jurisdictions/spain/art18-lis-operaciones-vinculadas
- jurisdictions/spain/ris-documentacion-masterfile-localfile
- frameworks/ocde-directrices-2022-cap3-rango-plena-competencia
fecha_creacion: 2026-08-27
fuente_primaria: Norma Foral 37/2013, de 13 de diciembre, del Impuesto sobre Sociedades
  del Territorio Histórico de Álava, art. 42; Ley 12/2002, del Concierto Económico,
  arts. 3, 14 a 16 y 66
id_fuente: es-foral-vinculadas
localizador: https://web.araba.eus/documents/d/araba/norma-foral-del-impuesto-sobre-sociedades_cas
origen: Lectura directa del PDF oficial de araba.eus y del texto consolidado del BOE,
  2026-08-27
pinpoint: Art. 42 NF 37/2013 (reglas generales de operaciones vinculadas); arts. 3,
  14 y 66 de la Ley 12/2002 (armonización, competencia sobre el IS, Junta Arbitral)
rango_normativo: Norma Foral y Ley estatal
tipo: Régimen foral, reparto competencial subestatal
tipo_localizador: url
titulo: 'España — territorios forales: operaciones vinculadas y reparto competencial'
usar_en: tp_domain/rules/statistical_rules.py, validación de perímetro previa al análisis
verificada_el: 2026-08-27
---

# España — territorios forales: operaciones vinculadas y reparto competencial

**Fuentes primarias leídas:**
Norma Foral 37/2013, de 13 de diciembre, del Impuesto sobre Sociedades de Álava, art. 42.
Ley 12/2002, de 23 de mayo, del Concierto Económico con la Comunidad Autónoma del País Vasco,
arts. 3, 14 a 16 y 66 (`BOE-A-2002-9969`, texto consolidado).

**Alcance de esta ficha.** Cubre Álava con texto primario y el marco competencial del Concierto.
**No cubre** Bizkaia, Gipuzkoa ni Navarra, cuyas normas no se han leído. Ver el apartado de límites
al final, que no es una coletilla: es lo que separa esta ficha de una afirmación de Derecho comparado
por analogía.

## Por qué el problema existe

El Impuesto sobre Sociedades es **tributo concertado de normativa autónoma** (art. 14.Uno de la Ley
12/2002). Las Diputaciones Forales no aplican la LIS: regulan su propio Impuesto sobre Sociedades.
Una operación vinculada entre una sociedad alavesa y una de territorio común tiene, por tanto, **dos
administraciones competentes aplicando dos cuerpos normativos distintos** a la misma operación.

Esa es, estructuralmente, la misma asimetría que TPIP modela entre Estados. Con una diferencia que
importa: aquí no hay convenio de doble imposición ni procedimiento amistoso.

### El reparto de competencia (arts. 14 a 16)

| Situación | Quién exige |
|---|---|
| Domicilio fiscal en País Vasco y volumen de operaciones del ejercicio anterior **por debajo de 12 M€** | Solo la Diputación Foral (art. 15.Uno) |
| Domicilio fiscal en País Vasco, **más de 12 M€** y **75 % o más** del volumen en territorio común | Normativa **común**, pese al domicilio foral (art. 14.Uno) |
| Regla simétrica inversa | Normativa foral, pese al domicilio común |
| Por encima de 12 M€ sin alcanzar el 75 % | **Tributación a ambas Administraciones**, en proporción al volumen de operaciones en cada territorio (art. 15.Dos) |

El «lugar de realización de las operaciones» que determina esa proporción se fija en el art. 16.

## Lo que la armonización obliga, y lo que no

El art. 3 es el precepto que decide si la divergencia es siquiera posible. Los Territorios Históricos,
al elaborar su normativa tributaria:

> a) Se adecuarán a la Ley General Tributaria en cuanto a terminología y conceptos, sin perjuicio de
> las peculiaridades establecidas en el presente Concierto Económico.
> b) Mantendrán una presión fiscal efectiva global equivalente a la existente en el resto del Estado.
> c) Respetarán y garantizarán la libertad de circulación y establecimiento (…) sin que se produzcan
> efectos discriminatorios, ni menoscabo de las posibilidades de competencia empresarial ni distorsión
> en la asignación de recursos.

**La armonización alcanza a la terminología, a la presión fiscal global y a la no distorsión. No obliga
a reproducir la LIS.** Un Territorio Histórico podría, en abstracto, regular las operaciones
vinculadas de otra manera. La pregunta de si lo hace es empírica, no dogmática, y por eso hubo que ir
al texto.

## Lo que dice el art. 42 de la Norma Foral alavesa

Leído entero. Y el resultado es que **Álava sigue a la LIS en todo lo que el motor de TPIP mira**.

### Regla de valoración (apartado 1)

> Las operaciones efectuadas entre personas o entidades vinculadas se valorarán por su **valor normal
> de mercado**. Se entenderá por valor normal de mercado aquél que se habría acordado por personas o
> entidades independientes en condiciones de libre competencia.

Nota terminológica: la norma foral dice **valor normal de mercado** donde el art. 18.1 LIS dice valor
de mercado. Es diferencia de rótulo, no de contenido: la definición es la misma.

Los factores de comparabilidad son cinco, y coinciden en sustancia con los del Capítulo III de las
Directrices OCDE: características del bien o servicio, funciones asumidas con identificación de
riesgos y ponderación de activos, términos contractuales, características del mercado, y cualquier
otra circunstancia relevante como las estrategias comerciales.

### Los métodos (apartado 4)

Cinco, en el mismo orden que el art. 18.4 LIS: precio libre comparable, coste incrementado, precio de
reventa, distribución del resultado y margen neto del conjunto de operaciones. Más la válvula de
«otros métodos y técnicas de valoración generalmente aceptados» cuando los anteriores no resulten
aplicables.

Y la misma regla de elección, sin jerarquía:

> El análisis de comparabilidad (…) y la información sobre las operaciones equiparables constituyen
> factores que permitirán, en cada caso (…) la elección del **método de valoración más adecuado**.

### El perímetro de vinculación (apartado 3)

**Umbral del 25 %**, igual que el art. 18.2 LIS, cuando la vinculación se define por la relación
socio-entidad. El parentesco alcanza hasta el tercer grado y la norma menciona expresamente a las
parejas de hecho. El concepto de grupo remite al art. 42 del Código de Comercio.

### Ninguna regla estadística

Este es el dato que buscaba el motor, y es negativo: **el texto no contiene ni una sola mención a
cuartiles, percentiles, rango intercuartílico ni mediana.** Se comprobó sobre las 245 páginas del
PDF oficial. Las 25 apariciones de la palabra «mediana» son todas de «pequeñas y medianas empresas».

Álava está, por tanto, en la misma casilla que el territorio común: sin regla estadística, corrección
valorativa caso por caso.

## El hueco: qué pasa si las dos Administraciones valoran distinto

Aquí está lo que esta ficha aporta al producto, y conviene leerlo despacio.

El art. 42.2 de la Norma Foral establece el efecto vinculante de la valoración administrativa:

> La Administración tributaria quedará vinculada por dicho valor **en relación con el resto de
> personas o entidades vinculadas**. La valoración administrativa no determinará la tributación (…)
> de una renta superior a la efectivamente derivada de la operación **para el conjunto** de las
> personas o entidades que la hubieran realizado.

Es la regla que evita la sobreimposición del grupo. Pero vincula **a esa Administración**. No dice qué
ocurre cuando la que valora es la Diputación Foral y la otra parte tributa ante la Agencia Estatal.

Y la Junta Arbitral, que sería el candidato natural a resolverlo, tiene las funciones del art. 66 y
**ninguna de las tres es la valoración**:

> a) Resolver los conflictos (…) en relación con la aplicación de los **puntos de conexión** de los
> tributos concertados y la determinación de la **proporción** correspondiente a cada Administración
> en los supuestos de tributación conjunta por el Impuesto sobre Sociedades (…).
> b) Conocer de los conflictos que surjan (…) como consecuencia de la **interpretación y aplicación
> del presente Concierto Económico** a casos concretos concernientes a relaciones tributarias
> individuales.
> c) Resolver las discrepancias que puedan producirse respecto a la **domiciliación** de los
> contribuyentes.

La letra a) es competencia y proporción, no precio. La letra c) es domicilio. La letra b) es la única
puerta posible, y exige que el conflicto se plantee como interpretación del Concierto, no como
discrepancia de valoración.

### ⚠️ Conflicto Doctrinal / Evolución de Criterio

**Hipótesis detectada por contraste de fuentes, no resuelta.** Si la Diputación Foral corrige al alza
el canon que cobra una sociedad alavesa a su matriz de Madrid, y la Agencia Estatal no practica el
ajuste correlativo en sede de la pagadora, el grupo soporta doble imposición interna. El art. 42.2
protege «al conjunto» frente a una Administración, pero el conjunto está aquí repartido entre dos.

No afirmo que ese hueco exista en la práctica. Afirmo que **el texto del Concierto no lo cierra
expresamente y que la competencia de la Junta Arbitral, tal como está redactada, no lo cubre de forma
evidente**. Falta consultar la doctrina de la Junta Arbitral y el Reglamento aprobado por Real Decreto
1760/2007 (`BOE-A-2008-747`), no leído.

## Aplicación en TPIP

**Conclusión operativa: `ES` puede seguir siendo una sola casilla en el motor, y eso ahora está
fundamentado en vez de supuesto.** Álava aplica la misma regla que el territorio común en lo único
que el motor evalúa, que es la consecuencia de caer fuera del rango.

Lo que sí cambia:

1. El perímetro de vinculación es el mismo 25 %, así que la validación previa no necesita rama foral.
2. **La doble imposición interna foral/común es un riesgo que el informe no menciona**, del mismo
   género que el ajuste correlativo internacional que tampoco modela.
3. Si algún día un Territorio Histórico introdujera regla estadística propia, `ES` dejaría de ser una
   casilla única. Hoy no es el caso en Álava.

## Límites de esta ficha

Se dicen porque callarlos sería justo el error que el corpus existe para impedir:

- **Bizkaia (NF 11/2013) y Gipuzkoa (NF 2/2014) no se han leído.** Los tres Territorios Históricos
  suelen coordinar su normativa, pero suponerlo es exactamente lo que aquí no se hace. Quedan
  pendientes.
- **Navarra no se ha tocado.** Su marco es el Convenio Económico (Ley 28/1990), no el Concierto, y su
  Impuesto sobre Sociedades es Ley Foral. Es un régimen distinto, no una variante del vasco.
- **No se ha buscado doctrina de la Junta Arbitral** sobre valoración de operaciones vinculadas. Es
  donde estaría la respuesta real al hueco descrito arriba.
- El Reglamento de la Junta Arbitral (`BOE-A-2008-747`) está localizado pero sin leer.
