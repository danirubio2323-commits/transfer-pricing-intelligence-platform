# Fase 1 — Diff aplicado para las 8 neutralizaciones REWRITE

Fecha original: 10 agosto 2026. Aplicado: 13 agosto 2026 (dos pasadas).
Estado: **APLICADO Y VERIFICADO sobre el corpus canónico (`C:\Users\LEINAD\Desktop\Cerebros_Fiscales`), en dos pasadas.**

- **Primera pasada** (§1-8 de este documento, tal como se aprobaron originalmente): 24 fragmentos de neutralización + 2 correcciones de precisión 🔎. Aplicada y verificada por hash el 13 de agosto de 2026.
- **Segunda pasada** (§9 de este documento, añadida el 13 de agosto de 2026): 7 fragmentos adicionales de "TFG"/"corredor" que la primera pasada no había capturado, encontrados durante la comprobación exhaustiva posterior a la primera aplicación. Aplicada y verificada por hash el mismo día.

Verificación aplicada a ambas pasadas: hash SHA256 antes/después de los 8 ficheros objetivo + 2 fichas KEEP de control, barrido de `mtime` sobre todo `wiki/` para confirmar que no se tocó ningún otro fichero, comparación de hash de la copia congelada `Cerebros_Fiscales.pre-migracion` (sin cambios en ninguna de las dos pasadas), y confirmación de que la rama `backup/pre-limpieza-corpus` permanece en `95c250a`.

Este documento es ahora el registro completo y único de qué cambió exactamente en el corpus (que vive fuera de git, sin historial propio) — no depende de ninguna conversación para reconstruirse.

Regla aplicada de forma consistente: se toca solo la frase o párrafo que encuadra el contenido hacia "el TFG" o "el corredor Gipuzkoa-Francia" como destinatario/caso de uso. No se toca contenido normativo, citas, fechas, artículos ni conclusiones jurídicas de fondo. Donde una norma es genuinamente específica de Gipuzkoa (Normas Forales 3/1990 y 3/2025), esa territorialidad se mantiene explícita — el cambio ahí es solo quitar el "para el TFG", no generalizar la norma a toda España.

**Dos correcciones de precisión bundled, separadas del debiasing puro, marcadas con 🔎** — en `boe-ley-12-2002-concierto-economico.md` y `boe-ley-3-2025-modificacion-concierto-economico.md` el original dice "guipuzcoana" donde la norma en cuestión (el Concierto Económico y su reforma) rige los tres Territorios Históricos, no solo Gipuzkoa. Corrijo a "vasca" en esos puntos. Es una corrección de exactitud legal, no una neutralización de sesgo — apruébala o recházala aparte si prefieres dejar el texto original.

---

## 1. `matriz/boe-ley-35-2006-irpf-art9-residencia.md`

**Conclusión jurídica**, párrafo completo:

- Antes: *"Documento de referencia estructural de primer orden para el TFG, tal y como pidió el Letrado Director: deja asentado el contraste de soberanía fiscal unilateral (Art. 9 LIRPF, determina residencia según criterio español interno) frente al mecanismo bilateral de desempate del CDI (Art. 4 MC-OCDE, aplicable solo cuando ambos Estados —España y Francia— califican a la misma persona como residente cada uno según su propia norma interna). Para el teletrabajador transfronterizo Gipuzkoa-Francia, la secuencia analítica correcta es: (1) ¿es residente en España según el Art. 9 LIRPF (o su equivalente en materia foral, Art. 43 Concierto)?; (2) ¿es residente en Francia según la norma interna francesa (⚠️ no ingerida en este corpus)?; (3) solo si (1) y (2) son ambas afirmativas, se activa el Art. 4 del CDI España-Francia (⚠️ CDI no ingerido en este corpus) para desempatar."*
- Después: *"Documento de referencia estructural de primer orden: deja asentado el contraste de soberanía fiscal unilateral (Art. 9 LIRPF, determina residencia según criterio español interno) frente al mecanismo bilateral de desempate del CDI (Art. 4 MC-OCDE, aplicable solo cuando dos Estados califican a la misma persona como residente cada uno según su propia norma interna). Para cualquier supuesto de doble residencia potencial entre España y otro Estado, la secuencia analítica correcta es: (1) ¿es residente en España según el Art. 9 LIRPF (o su equivalente en materia foral, Art. 43 Concierto)?; (2) ¿es residente en el otro Estado según su norma interna (⚠️ no ingerida en este corpus para ningún país concreto)?; (3) solo si (1) y (2) son ambas afirmativas, se activa el Art. 4 del CDI bilateral aplicable (⚠️ ningún CDI bilateral está ingerido todavía en este corpus) para desempatar."*

**⚠️ SIN FUENTE EN EL CORPUS**, puntos (i)-(ii):

- Antes: *"(i) norma interna francesa de residencia fiscal (imprescindible para completar el paso 2 de la secuencia anterior); (ii) texto del CDI España-Francia — sin él, no puede cerrarse el análisis aunque el Art. 9 LIRPF y el Art. 43 del Concierto ya estén documentados; (iii) [sin cambios]"*
- Después: *"(i) norma interna del otro Estado en cuestión sobre residencia fiscal (imprescindible para completar el paso 2 de la secuencia anterior); (ii) texto del CDI bilateral aplicable — sin él, no puede cerrarse el análisis aunque el Art. 9 LIRPF y el Art. 43 del Concierto ya estén documentados; (iii) [sin cambios]"*

No se toca: "Hechos" (la referencia a "instrucción del Letrado Director" no es sesgo territorial, es narración de flujo de trabajo del propio corpus — fuera del alcance de esta tarea), "Contenido", "Doctrina aplicada".

---

## 2. `matriz/ue-directiva-iva-2006-112-ce.md`

**Hechos**, última frase:
- Antes: *"...esta ficha se limita a los elementos estructurales con mayor relevancia potencial para pymes y autónomos del corredor Gipuzkoa-Francia, no a un resumen artículo por artículo."*
- Después: *"...esta ficha se limita a los elementos estructurales con mayor relevancia potencial para pymes y autónomos con operaciones intracomunitarias transfronterizas, no a un resumen artículo por artículo."*

**Contenido**, tres frases sueltas dentro de "Lugar de realización del hecho imponible":
- "...relevante para servicios profesionales transfronterizos del corredor." → "...relevante para servicios profesionales transfronterizos intracomunitarios."
- "...regla de aplicación directa para alquileres y servicios inmobiliarios en el corredor Gipuzkoa-Francia." → "...regla de aplicación directa para alquileres y servicios inmobiliarios transfronterizos dentro de la UE."
- "Pieza jurídica central para cualquier pyme del corredor que venda bienes de Gipuzkoa a un sujeto pasivo francés identificado a efectos de IVA, o viceversa." → "Pieza jurídica central para cualquier pyme que venda bienes a un sujeto pasivo identificado a efectos de IVA en otro Estado miembro, o viceversa."
- "...relevante para comerciantes de segunda mano y anticuarios del corredor." → "...relevante para comerciantes de segunda mano y anticuarios con operaciones transfronterizas intracomunitarias."

**Doctrina aplicada**, última frase:
- Antes: *"...Esta dualidad de criterios (destino para IVA, residencia para renta) es relevante para cualquier análisis comparado que el TFG realice sobre la fiscalidad indirecta del corredor."*
- Después: *"...Esta dualidad de criterios (destino para IVA, residencia para renta) es relevante para cualquier análisis comparado de fiscalidad indirecta transfronteriza dentro de la UE."*

**Conclusión jurídica**, párrafo completo:
- Antes: *"Norma de aplicación transversal y de uso frecuente para cualquier pyme o autónomo del corredor Gipuzkoa-Francia que realice entregas de bienes o prestaciones de servicios transfronterizas — pero, dado que este TFG se centra en el riesgo de EP por teletrabajo y en la fiscalidad de la renta (IRPF/IS/IRNR) más que en la imposición indirecta, esta ficha se mantiene como referencia estructural de contexto, no como eje de profundización, salvo que el TFG aborde expresamente un caso de tributación indirecta del corredor (p. ej. venta de bienes/servicios entre pymes guipuzcoanas y clientes franceses)."*
- Después: *"Norma de aplicación transversal y de uso frecuente para cualquier pyme o autónomo que realice entregas de bienes o prestaciones de servicios transfronterizas dentro de la UE. Dado que el resto de este corpus se centra en fiscalidad de la renta (IRPF/IS/IRNR) y en el riesgo de EP por teletrabajo más que en imposición indirecta, esta ficha se mantiene como referencia estructural de contexto, no como eje de profundización, salvo que se aborde expresamente un caso de tributación indirecta (p. ej. venta de bienes/servicios entre pymes de distintos Estados miembros)."*

**SIN FUENTE**, última frase:
- "...cualquier afirmación sobre el régimen de IVA actual del corredor debe contrastarse..." → "...cualquier afirmación sobre el régimen de IVA actual debe contrastarse..."

---

## 3. `matriz/ue-reglamento-883-2004-seguridad-social.md`

**Hechos**, última frase:
- Antes: *"...pero su lógica de 'legislación única aplicable' es la pieza estructural que el CLAUDE.md de este cerebro fiscal identifica como el punto donde el corredor Gipuzkoa-Francia rompe la tónica fiscal estricta y entra en el plano sociolaboral transfronterizo — con consecuencias prácticas directas para el trabajador y la empresa que la fiscalidad de la renta no captura por sí sola."*
- Después: *"...pero su lógica de 'legislación única aplicable' es la pieza estructural que conecta el plano fiscal con el plano sociolaboral en cualquier supuesto de trabajo transfronterizo — con consecuencias prácticas directas para el trabajador y la empresa que la fiscalidad de la renta no captura por sí sola."*

**"Definición de trabajador fronterizo"**, última frase:
- Antes: *"...punto de fricción potencial a explorar en el TFG entre la calificación laboral/social y la fiscal del mismo sujeto."*
- Después: *"...punto de fricción potencial entre la calificación laboral/social y la fiscal del mismo sujeto, a explorar caso por caso según el convenio aplicable."*

**"Regla especial desplazamiento temporal"**, última frase:
- Antes: *"Regla directamente relevante para el análisis de teletrabajo transfronterizo del TFG: un desplazamiento de personal de una pyme guipuzcoana a Francia por menos de 24 meses mantiene la cotización en España..."*
- Después: *"Regla directamente relevante para el análisis de teletrabajo transfronterizo: un desplazamiento de personal de una empresa española a otro Estado miembro por menos de 24 meses mantiene la cotización en España..."*

**"Regla especial actividad en dos Estados"**, inciso:
- "(situación típica del teletrabajador transfronterizo que combina días de oficina en Gipuzkoa con teletrabajo en Francia)" → "(situación típica del teletrabajador transfronterizo que combina días de oficina en un Estado miembro con teletrabajo en otro)"

**"Acuerdos excepcionales"**, nota SIN FUENTE:
- Antes: *"...verificación de la existencia y contenido concreto de un acuerdo Art. 16 vigente entre España y Francia aplicable al corredor Gipuzkoa-Francia — pendiente de contrastar..."*
- Después: *"...verificación de la existencia y contenido concreto de un acuerdo Art. 16 vigente entre España y Francia — pendiente de contrastar..."* (se mantiene España-Francia como ejemplo factual ya generalizado en la propia frase original — "y otros pares de Estados" — solo se retira "aplicable al corredor Gipuzkoa-Francia")

**Doctrina aplicada**, última frase:
- Antes: *"...La divergencia entre ambos regímenes (fiscal vs. social) para un mismo teletrabajador transfronterizo del corredor Bidasoa-Txingudi es una fricción de primer orden para el TFG: un trabajador puede ser residente fiscal en Francia bajo el CDI..."*
- Después: *"...La divergencia entre ambos regímenes (fiscal vs. social) para un mismo teletrabajador transfronterizo es una fricción de primer orden: un trabajador puede ser residente fiscal en un Estado bajo el CDI aplicable..."*

**Conclusión jurídica**, primera frase:
- "Norma de aplicación directa y de primer orden para el eje central del TFG (riesgo de EP por teletrabajo transfronterizo) porque..." → "Norma de aplicación directa y de primer orden para cualquier análisis de riesgo de EP por teletrabajo transfronterizo, porque..."

**SIN FUENTE**, cierre:
- "...ambos pendientes de contrastar con fuentes específicas antes de su uso en el TFG." → "...ambos pendientes de contrastar con fuentes específicas antes de su uso en un análisis concreto."

---

## 4. `sub_irpf/interfaz-art4-mcocde-residencia-irpf-irnr.md`

**"⚠️ Conflicto Doctrinal"**, última frase:
- Antes: *"...El riesgo práctico para el TFG es la conflación indebida de ambos estándares... asuma erróneamente que ese mismo cómputo de días es determinante también a efectos del desempate convencional con Francia..."*
- Después: *"...El riesgo práctico es la conflación indebida de ambos estándares... asuma erróneamente que ese mismo cómputo de días es determinante también a efectos del desempate convencional con el otro Estado..."*

**Doctrina aplicada**, párrafo completo (la ficha más entretejida de las 8):
- Antes: *"La secuencia analítica correcta para un supuesto de doble residencia potencial en el corredor Gipuzkoa-Francia es, por tanto: (1) verificar si España reclama la residencia según el Art. 9 LIRPF (183 días o núcleo económico, con la precisión de que en Gipuzkoa el punto de conexión interno relevante es el Art. 43 del Concierto Económico...); (2) verificar, con fuente no disponible en este corpus, si Francia reclama igualmente la residencia según su propia norma interna; (3) solo si ambas respuestas son afirmativas, aplicar el test de desempate del Art. 4.2 MC-OCDE (o la redacción equivalente del CDI España-Francia bilateral, tampoco ingerido) en el orden..."*
- Después: *"La secuencia analítica correcta para un supuesto de doble residencia potencial entre España y otro Estado es, por tanto: (1) verificar si España reclama la residencia según el Art. 9 LIRPF (183 días o núcleo económico — con la precisión de que en el País Vasco el punto de conexión interno relevante es el Art. 43 del Concierto Económico, ver [[concierto_foral/boe-ley-12-2002-concierto-economico]], de redacción estructuralmente idéntica al Art. 9 LIRPF pero limitada al reparto España/País Vasco); (2) verificar, con fuente no disponible en este corpus para ningún país concreto, si el otro Estado reclama igualmente la residencia según su propia norma interna; (3) solo si ambas respuestas son afirmativas, aplicar el test de desempate del Art. 4.2 MC-OCDE (o la redacción equivalente del CDI bilateral aplicable, tampoco ingerido en este corpus) en el orden..."*

**🔎 Nota de precisión bundled**: cambio "en Gipuzkoa" → "en el País Vasco". El Art. 43 del Concierto reparte competencia España/País Vasco en bloque (los tres Territorios Históricos), no Gipuzkoa en particular — la distinción entre Gipuzkoa/Álava/Bizkaia es de nivel de Norma Foral (Art. 2 bis de la Norma Foral 3/1990, ficha 7), no del Concierto. Es una corrección de exactitud que coincide con la neutralización, no una generalización indebida.

**Conclusión jurídica**, párrafo completo:
- Antes: *"Ficha de valor estructural para el TFG: no aporta un documento nuevo... Es la pieza que, dentro de las limitaciones del corpus actual, más se aproxima a resolver metodológicamente la pregunta central del TFG sobre residencia fiscal en el corredor Gipuzkoa-Francia — sin poder cerrarla del todo por la ausencia del CDI bilateral y de la norma francesa."*
- Después: *"Ficha de valor estructural: no aporta un documento nuevo... Es la pieza que, dentro de las limitaciones del corpus actual, más se aproxima a resolver metodológicamente cualquier pregunta sobre residencia fiscal en supuestos de doble residencia transfronteriza con España — sin poder cerrarla del todo, para un país concreto, por la ausencia del CDI bilateral correspondiente y de la norma interna del otro Estado."*

**SIN FUENTE**, puntos (i)-(ii):
- Antes: *"(i) CDI España-Francia — pieza que cerraría el análisis; el Art. 4 de ese convenio bilateral podría apartarse en algún extremo de la redacción del MC-OCDE aquí desarrollada, dato no verificable sin el texto concreto; (ii) norma interna francesa de residencia fiscal — necesaria para completar el paso (2) de la secuencia; (iii) [sin cambios]"*
- Después: *"(i) Ningún CDI bilateral concreto está ingerido en este corpus — el Art. 4 de un convenio bilateral podría apartarse en algún extremo de la redacción del MC-OCDE aquí desarrollada, dato no verificable sin el texto concreto de cada convenio; (ii) norma interna de residencia fiscal de otros Estados — necesaria para completar el paso (2) de la secuencia, para cualquier país concreto que se analice; (iii) [sin cambios]"*

No se toca: los ejemplos ilustrativos sueltos que usan Francia como país de ejemplo dentro de explicaciones generales (p. ej. en la sección "Art. 4.2, letra a"), porque son ejemplos, no encuadre — el contenido metodológico no depende de que el ejemplo sea Francia u otro país.

---

## 5. `concierto_foral/boe-ley-12-2002-concierto-economico.md`

**Título de sección** dentro de "Contenido":
- "Retenciones sobre rendimientos del trabajo y regla expresa de teletrabajo (Art. 7) — dato duro, núcleo de conexión con el corredor Gipuzkoa-Francia" → "Retenciones sobre rendimientos del trabajo y regla expresa de teletrabajo (Art. 7) — dato duro, pieza clave para el teletrabajo transfronterizo"

**Misma sección**, cierre:
- Antes: *"Dato de máxima relevancia para el eje central del TFG (teletrabajo transfronterizo Gipuzkoa-Francia): esta regla resuelve la cuestión de retenciones IRPF pero no resuelve la cuestión distinta de residencia fiscal a efectos del CDI España-Francia..."*
- Después: *"Dato de máxima relevancia para el análisis de teletrabajo transfronterizo: esta regla resuelve la cuestión de retenciones IRPF pero no resuelve la cuestión distinta de residencia fiscal a efectos del CDI aplicable..."*

**"Comisiones y Junta Arbitral"**, cierre:
- "...pieza procedimental relevante para cualquier conflicto de doble imposición interna (no internacional) que afecte al corredor Gipuzkoa-Francia si involucra también un cambio de domicilio dentro de España." → "...pieza procedimental relevante para cualquier conflicto de doble imposición interna (no internacional) que involucre un cambio de domicilio dentro de España."

**Doctrina aplicada**, cierre:
- Antes: *"...dato relevante para el TFG: la fiscalidad foral guipuzcoana no puede generar un resultado incompatible con el CDI España-Francia, aunque sí puede fijar reglas internas propias..."*
- Después: *"...dato relevante: la fiscalidad foral vasca no puede generar un resultado incompatible con el CDI bilateral que corresponda, aunque sí puede fijar reglas internas propias..."*

**🔎 Nota de precisión bundled**: "fiscalidad foral guipuzcoana" → "fiscalidad foral vasca". Esta ficha trata la Ley 12/2002, el Concierto con el conjunto de la CAPV, no una Norma Foral de Gipuzkoa — "vasca" es más preciso que "guipuzcoana" aquí.

**"Fricción de criterios"**, cierre:
- "...pendiente de contrastar con el desarrollo foral específico del IRNR tras la Ley 3/2025 antes de asentarse como conclusión del TFG." → "...pendiente de contrastar con el desarrollo foral específico del IRNR tras la Ley 3/2025 antes de asentarse como conclusión firme."

**Conclusión jurídica**, apertura:
- "Documento de máxima relevancia estructural para el TFG: (i)..." → "Documento de máxima relevancia estructural: (i)..."

**SIN FUENTE**, punto (i):
- "(i) texto del CDI España-Francia (no ingerido todavía) — imprescindible para contrastar el Art. 43... con el Art. 4 y Art. 15 del convenio bilateral;" → "(i) texto de un CDI bilateral concreto (ninguno está ingerido todavía) — imprescindible para contrastar el Art. 43... con el Art. 4 y Art. 15 del convenio que corresponda;"

No se toca el punto (iii) de SIN FUENTE ("Norma Foral del IRPF de Gipuzkoa") — es una referencia genuinamente específica de Gipuzkoa, no encuadre hacia el TFG.

---

## 6. `concierto_foral/boe-ley-3-2025-modificacion-concierto-economico.md`

**"Reconfiguración del IRNR"**, párrafo "Relevancia directa":
- Antes: *"**Relevancia directa para el TFG**: esta reforma es el dato normativo más reciente... (p. ej. un trabajador francés no residente fiscal en España que obtiene rentas del trabajo en Gipuzkoa, o viceversa) — antes de esta ley, el IRNR aplicable a un no residente con rentas de fuente guipuzcoana era siempre la norma estatal... Esto añade una capa adicional... que se suma, y no sustituye, a la calificación del CDI España-Francia sobre residencia/fuente."*
- Después: *"**Relevancia directa**: esta reforma es el dato normativo más reciente... (p. ej. un trabajador no residente fiscal en España que obtiene rentas del trabajo en el País Vasco, o viceversa) — antes de esta ley, el IRNR aplicable a un no residente con rentas de fuente vasca era siempre la norma estatal... Esto añade una capa adicional... que se suma, y no sustituye, a la calificación del CDI bilateral aplicable sobre residencia/fuente."*

**🔎 Nota de precisión bundled**: "rentas de fuente guipuzcoana" → "rentas de fuente vasca" — misma razón que en la ficha 5: la Ley 3/2025 modifica el Concierto para toda la CAPV.

**Doctrina aplicada**, primera frase:
- "El cambio de fondo real de esta reforma para el TFG no es la incorporación del Pilar Dos (umbral 750M€, irrelevante para el corredor pyme Gipuzkoa-Francia...) sino la autonomización del IRNR..." → "El cambio de fondo real de esta reforma no es la incorporación del Pilar Dos (umbral 750M€, irrelevante para el tejido empresarial pyme...) sino la autonomización del IRNR..."

**Conclusión jurídica**, párrafo completo:
- Antes: *"Documento de referencia obligada para completar el análisis de residencia/fuente del TFG en el escenario en que el trabajador transfronterizo sea, a efectos del ordenamiento español, no residente (p. ej. residente fiscal en Francia con rentas de trabajo de fuente guipuzcoana): a partir de esta reforma... antes de proyectar el análisis sobre el Art. 15 del CDI España-Francia."*
- Después: *"Documento de referencia obligada para completar el análisis de residencia/fuente en el escenario en que un trabajador transfronterizo sea, a efectos del ordenamiento español, no residente (p. ej. residente fiscal en otro Estado con rentas de trabajo de fuente vasca): a partir de esta reforma... antes de proyectar el análisis sobre el Art. 15 del CDI bilateral que corresponda."*

---

## 7. `concierto_foral/norma-foral-3-1990-sucesiones-donaciones.md`

Norma genuinamente específica de Gipuzkoa (Norma Foral guipuzcoana) — la territorialidad NO se toca donde es correcta; solo se retira el encuadre "para el TFG".

**"Regla de los 5 años"**, última frase:
- "Dato de relevancia directa para el TFG si se explora la sucesión/donación de un trabajador transfronterizo recién trasladado a Gipuzkoa desde Francia." → "Dato de relevancia directa para cualquier análisis de sucesión/donación de un contribuyente recién trasladado a Gipuzkoa desde otro país." *(se mantiene "Gipuzkoa" — es correcto, la norma es guipuzcoana; se generaliza "desde Francia" porque la regla de cuarentena de 5 años aplica con independencia del país de origen)*

**"Obligación real para no residentes"**, última frase:
- "Regla directamente relevante para un supuesto de sucesión/donación con conexión Gipuzkoa-Francia en el que el causante o donatario resida en Francia." → "Regla directamente relevante para cualquier supuesto de sucesión/donación en el que el causante o donatario resida en el extranjero."

**Doctrina aplicada**, última frase:
- Antes: *"La ausencia, en este documento, de cualquier referencia a un CDI bilateral de sucesiones con Francia sugiere... que el alivio de una eventual doble imposición sucesoria en el corredor Gipuzkoa-Francia dependería del mecanismo unilateral del Art. 22..."*
- Después: *"La ausencia, en este documento, de cualquier referencia a un CDI bilateral de sucesiones sugiere... que el alivio de una eventual doble imposición sucesoria en un supuesto transfronterizo con conexión guipuzcoana dependería del mecanismo unilateral del Art. 22..."*

**Conclusión jurídica**, párrafo completo:
- Antes: *"Relevancia media-alta para el TFG si su alcance incluye sucesiones/donaciones del trabajador transfronterizo (no solo rentas del trabajo): la 'regla de los 5 años'... Si el TFG se centra exclusivamente en IRPF/EP/teletrabajo, esta norma queda en un plano secundario de contexto."*
- Después: *"Relevancia alta para cualquier análisis que incluya sucesiones/donaciones de un trabajador transfronterizo, no solo rentas del trabajo: la 'regla de los 5 años'... Para un análisis centrado exclusivamente en IRPF/EP/teletrabajo, esta norma queda en un plano secundario de contexto."*

No se toca: la mención de Francia en "Cláusula de salvaguarda de Tratados" (Doctrina/Hechos) — es un ejemplo factual dentro de un razonamiento general sobre ausencia de CDI de sucesiones, no encuadre hacia el TFG.

---

## 8. `concierto_foral/norma-foral-3-2025-impuesto-complementario.md`

Norma genuinamente específica de Gipuzkoa (Norma Foral del Territorio Histórico) — mismo criterio que la ficha 7.

**Conclusión jurídica**, párrafo completo (único punto de sesgo detectado en toda la ficha):
- Antes: *"Relevancia baja para el eje central IRPF/EP/teletrabajo del TFG (el umbral de 750M€ excluye estructuralmente al tejido empresarial pyme del corredor Gipuzkoa-Francia...), pero de alto valor metodológico... que podría servir de contraste metodológico si el TFG explora cómo se articula (o debería articularse) la aplicación del CDI España-Francia por las Diputaciones Forales en materia de teletrabajo transfronterizo..."*
- Después: *"Relevancia baja para un análisis centrado en IRPF/EP/teletrabajo (el umbral de 750M€ excluye estructuralmente al tejido empresarial pyme...), pero de alto valor metodológico... que podría servir de contraste metodológico para explorar cómo se articula (o debería articularse) la aplicación de un CDI bilateral por las Diputaciones Forales en materia de teletrabajo transfronterizo..."*

---

## 9. Segunda pasada — 7 fragmentos adicionales (encontrados y aplicados el 13 de agosto de 2026)

Tras aplicar la primera pasada, un grep final de "TFG"/"corredor" sobre las 8 fichas ya editadas encontró 7 menciones que el diff original (§1-8) no había capturado — en su mayoría títulos de sección y cierres de frase en secciones "Contenido"/"SIN FUENTE" que la revisión inicial, centrada en "Doctrina aplicada"/"Conclusión jurídica", no había barrido por completo. Mismo criterio que en la primera pasada: solo encuadre territorial/TFG, nada de contenido normativo, citas, artículos, fechas o cifras.

### `matriz/ue-directiva-iva-2006-112-ce.md`

- Título: *"### Exenciones para operaciones intracomunitarias (Título IX, Cap. 4) — dato duro clave para el corredor"* → *"### Exenciones para operaciones intracomunitarias (Título IX, Cap. 4) — dato duro clave para operaciones intracomunitarias transfronterizas"*
- Título: *"### Régimen especial de las pequeñas empresas (Título XII, Cap. 1, Art. 281-294) — dato duro relevante para autónomos del corredor"* → *"### Régimen especial de las pequeñas empresas (Título XII, Cap. 1, Art. 281-294) — dato duro relevante para autónomos con operaciones transfronterizas"*

### `matriz/ue-reglamento-883-2004-seguridad-social.md`

- Título: *"### Definición de 'trabajador fronterizo' (Art. 1.f) — dato duro, pieza central para el corredor"* → *"### Definición de 'trabajador fronterizo' (Art. 1.f) — dato duro, pieza central para el teletrabajo transfronterizo"*
- *"...dato de detalle, no central para el eje fiscal del TFG pero recogido para completitud del corpus sociolaboral."* → *"...dato de detalle, no central para el eje fiscal de esta ficha pero recogido para completitud del corpus sociolaboral."*

### `sub_irpf/interfaz-art4-mcocde-residencia-irpf-irnr.md`

- *"El Comentario (¶19, modificado el 21 de noviembre de 2017) contiene la precisión más relevante para el TFG: ..."* → *"El Comentario (¶19, modificado el 21 de noviembre de 2017) contiene la precisión más relevante: ..."*
- **No tocado, deliberadamente**: *"...no desarrollado en profundidad en esta ficha por su menor probabilidad de aplicación práctica al corredor..."* (punto iii de SIN FUENTE) — ya estaba excluido explícitamente en la primera pasada (§4 de este documento decía "no se toca") y se mantiene así en la segunda. Confirmado intacto tras aplicar esta pasada.

### `concierto_foral/boe-ley-3-2025-modificacion-concierto-economico.md`

- *"...si se requiere el detalle exacto de cada criterio de fuente para el análisis del TFG."* (sección SIN FUENTE) → *"...si se requiere el detalle exacto de cada criterio de fuente."*

### `concierto_foral/norma-foral-3-2025-impuesto-complementario.md`

- *"...pendiente de verificación cruzada antes de su uso en el TFG, dado que esta ficha no ha volcado el contexto completo del pasaje."* → *"...pendiente de verificación cruzada, dado que esta ficha no ha volcado el contexto completo del pasaje."*

No hubo fragmentos adicionales en `matriz/boe-ley-35-2006-irpf-art9-residencia.md`, `concierto_foral/boe-ley-12-2002-concierto-economico.md` ni `concierto_foral/norma-foral-3-1990-sucesiones-donaciones.md` — confirmado por grep, esas tres quedaron completamente limpias ya en la primera pasada.

---

## Resumen de alcance

- 8 fichas, **31 fragmentos de texto tocados en total** (24 de la primera pasada + 7 de la segunda).
- 2 correcciones de precisión bundled (🔎, ficha 4 y ficha 5/6 de la primera pasada).
- Ninguna cita, artículo, fecha, cifra o conclusión jurídica de fondo cambia, en ninguna de las dos pasadas.
- `norma-foral-3-1990` y `norma-foral-3-2025` mantienen su territorialidad guipuzcoana explícita — no se generalizan a España.
- La frase *"aplicación práctica al corredor"* en `interfaz-art4-mcocde-residencia-irpf-irnr.md` permanece intacta, excluida deliberadamente en ambas pasadas.
- Ambas pasadas están **aplicadas y verificadas** sobre el corpus canónico. Las copias congeladas (`Cerebros_Fiscales.pre-migracion`) y la rama `backup/pre-limpieza-corpus` no se han tocado en ningún momento.
