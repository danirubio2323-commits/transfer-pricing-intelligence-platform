# Fase 1 — Clasificación de las fichas con sesgo territorial (corredor Gipuzkoa-Francia)

Fecha: 10 agosto 2026
Estado: **inventario para aprobación. No se ha modificado, reescrito, movido ni borrado ninguna ficha del corpus ni de las copias de respaldo.**
Corpus verificado: `C:\Users\LEINAD\Desktop\Cerebros_Fiscales\wiki\` (ubicación canónica tras la migración de Fase 1). Copia congelada intacta en `tp_domain\knowledge\Cerebros_Fiscales.pre-migracion\`.

---

## 0. Corrección del recuento: son 43 fichas, no 41

La lista de partida que se usó para encargar esta clasificación tenía, contada literalmente, **42 rutas**, no 41. Además, la lectura completa (no solo grep) encontró **una ficha adicional** con el mismo patrón que no estaba en esa lista: `concierto_foral/norma-foral-2-2005-lgt-gipuzkoa.md`, que cierra su "Conclusión jurídica" con "sin relevancia sustantiva directa para el análisis... del corredor Gipuzkoa-Francia" — mismo patrón, sesgo leve, contenido general aprovechable.

**Total verificado por lectura completa de las 43 fichas: 43.** No se ha forzado ningún número — la discrepancia con el "41" original no tiene una explicación verificada (pudo deberse a un patrón de grep más estricto o a no revisar dos fichas que expresan el sesgo sin usar literalmente la palabra "corredor").

De las 43, **cero son falsos positivos** — todas confirmadas por lectura de sus secciones "Hechos", "Doctrina aplicada" y "Conclusión jurídica".

---

## 1. Recuento final

| Categoría | Nº fichas |
|---|---|
| **KEEP** | 35 |
| **REWRITE** | 8 |
| **ARCHIVE** | 0 confirmadas (2 con duda razonable, ver §4) |
| **REMOVE** | 0 |
| **Total** | **43** |

Ninguna ficha calificó para REMOVE: en ningún caso el contenido jurídico depende tan por completo del marco "corredor Gipuzkoa-Francia" que, al retirarlo, no quede nada reutilizable. Ninguna calificó para ARCHIVE con confianza alta tampoco — las dos candidatas más cercanas se detallan en §4 para que decidas tú con el matiz sobre la mesa.

---

## 2. KEEP — 35 fichas, cambio mínimo (neutralizar una frase de cierre)

En todas estas, el contenido de fondo es de propósito general y correcto; el sesgo vive en una sola frase o párrafo final de "Conclusión jurídica" (en algún caso también en "Doctrina aplicada"), nunca en el razonamiento sustantivo.

| Ruta | Frase a neutralizar |
|---|---|
| `matriz/boe-cdi-espana-alemania-2011-2012.md` | "Relevante para cualquier operador del corredor Gipuzkoa-Francia..." |
| `matriz/boe-cdi-espana-china-2018-2021.md` | "...en el corredor Bidasoa-Txingudi" |
| `matriz/boe-cdi-espana-francia-1995.md` | "Relevante para el corredor Gipuzkoa-Francia por ser el CDI aplicable..." |
| `matriz/ley-58-2003-general-tributaria.md` | "...al trabajador transfronterizo del corredor Gipuzkoa-Francia" |
| `matriz/nl-vpb1969-impuesto-sociedades.md` | "...para una pyme del corredor Gipuzkoa-Francia si algún día operase..." |
| `matriz/ocde-coe-convencion-asistencia-mutua-mac.md` | "Para el corredor Gipuzkoa-Francia es relevante como fundamento alternativo..." |
| `matriz/ocde-convenio-multilateral-mli-2016.md` | "...antes de dar por aplicable cualquier disposición del MLI al caso Gipuzkoa-Francia..." |
| `matriz/ocde-lista-miembros-marco-inclusivo-2025.md` | "...relevante al analizar la posición de terceros países en operaciones del corredor Gipuzkoa-Francia..." |
| `matriz/onu-modelo-convenio-2021.md` | "...no de aplicación directa al corredor Gipuzkoa-Francia..." |
| `matriz/tjue-c-196-04-cadbury-schweppes.md` | "...si este explora el riesgo de recalificación de estructuras del corredor Gipuzkoa-Francia..." |
| `matriz/tjue-casos-daneses-beneficiario-efectivo.md` | "Su aplicación al corredor Gipuzkoa-Francia no sería directa..." |
| `matriz/ue-directiva-cesop-2020-284-ue.md` | "Norma de aplicación potencial para pymes... del corredor Gipuzkoa-Francia..." |
| `matriz/ue-directiva-dac1-2011-16-ue.md` | "Norma marco de aplicación directa para cualquier operador del corredor Gipuzkoa-Francia..." |
| `matriz/ue-directiva-dac2-2014-107-ue.md` | "...eje Bidasoa-Txingudi" |
| `matriz/ue-directiva-dac3-2015-2376-ue.md` | "...para una empresa del corredor Gipuzkoa-Francia..." |
| `matriz/ue-directiva-dac4-2016-881-ue.md` | Dos frases: cierre de "Doctrina aplicada" y párrafo de "Conclusión" |
| `matriz/ue-directiva-dac5-2016-2258-ue.md` | "...del corredor con cuentas financieras a ambos lados de la frontera..." |
| `matriz/ue-directiva-dac6-2018-822-ue.md` | "...para pymes y autónomos del corredor Gipuzkoa-Francia..." |
| `matriz/ue-directiva-dac7-2021-514-ue.md` | "...entre la Hacienda Foral de Gipuzkoa y la administración francesa..." |
| `matriz/ue-directiva-dac8-2023-2226-ue.md` | "...corredor Gipuzkoa-Francia con activos en cripto-monedas..." |
| `matriz/ue-directiva-fusiones-2009-133-ce.md` | "...dentro del corredor Gipuzkoa-Francia..." |
| `matriz/ue-directiva-intereses-canones-2003-49-ce.md` | "...entre una entidad del corredor Gipuzkoa-Francia..." |
| `matriz/ue-directiva-matriz-filial-2011-96-ue.md` | "...relevante para cualquier estructura societaria del corredor Gipuzkoa-Francia..." |
| `sub_is/boe-ley-27-2014-is-base-imponible-ep.md` | "...en el corredor Gipuzkoa-Francia..." |
| `sub_is/boe-ley-7-2024-impuesto-complementario.md` | "...excluye al tejido pyme del corredor Gipuzkoa-Francia..." |
| `sub_is/boe-orden-hac-1198-2025-modelos-impuesto-complementario.md` | "...ajeno al tejido pyme del corredor Gipuzkoa-Francia..." |
| `sub_is/garrigues-2024-pilar-2-espana.md` | "...umbral 750M€ ajeno al tejido pyme del corredor..." |
| `sub_is/pilar-dos-globe-administrative-guidance-2023.md` | "...excluye a los operadores típicos del corredor Gipuzkoa-Francia..." |
| `sub_is/pilar-dos-globe-consolidated-commentary-2025.md` | "...excluye a la práctica totalidad de pymes y autónomos del corredor Gipuzkoa-Francia..." |
| `sub_is/pilar-dos-globe-manual-implementacion.md` | Encabezado "...pieza clave para el corredor Gipuzkoa-Francia" + cierre de Conclusión |
| `sub_is/ue-directiva-atad-i-2016-1164.md` | "...para cualquier pyme o empresa del corredor Gipuzkoa-Francia..." |
| `sub_is/ue-directiva-atad-ii-2017-952.md` | "Relevante para cualquier estructura del corredor Gipuzkoa-Francia..." |
| `sub_is/ue-directiva-pilar-dos-2022-2523-ue.md` | "...objeto principal de este TFG" |
| `sub_is/ue-directiva-public-cbcr-2021-2101-ue.md` | "...no de aplicación directa a la pyme/autónomo del corredor Gipuzkoa-Francia..." |
| `concierto_foral/norma-foral-2-2005-lgt-gipuzkoa.md` | "...sin relevancia sustantiva directa... del corredor Gipuzkoa-Francia..." (ficha ausente de la lista original) |

---

## 3. REWRITE — 8 fichas, sesgo entretejido en el razonamiento

| Ruta | Motivo | Cita |
|---|---|---|
| `matriz/boe-ley-35-2006-irpf-art9-residencia.md` | Todo el párrafo de "Conclusión jurídica" construye la secuencia analítica (1)-(2)-(3) alrededor del "teletrabajador transfronterizo Gipuzkoa-Francia" como sujeto central, no como apéndice | "Para el teletrabajador transfronterizo Gipuzkoa-Francia, la secuencia analítica correcta es: (1) ¿es residente en España según el Art. 9 LIRPF...?..." |
| `matriz/ue-directiva-iva-2006-112-ce.md` | El sesgo aparece ya en "Hechos" (delimita el alcance de la ficha al corredor), se repite en varios bullets de "Contenido" y en "Doctrina aplicada" | "esta ficha se limita a los elementos estructurales con mayor relevancia potencial para pymes y autónomos del corredor Gipuzkoa-Francia..." (sección Hechos) |
| `matriz/ue-reglamento-883-2004-seguridad-social.md` | Sesgo entretejido en Hechos, Contenido (ejemplos construidos sobre "una pyme guipuzcoana... a Francia"), Doctrina y Conclusión | "...su lógica de 'legislación única aplicable' es la pieza estructural que el CLAUDE.md de este cerebro fiscal identifica como el punto donde el corredor Gipuzkoa-Francia rompe la tónica fiscal estricta..." |
| `sub_irpf/interfaz-art4-mcocde-residencia-irpf-irnr.md` | La más entretejida de las 43: la propia secuencia metodológica del test de residencia (pasos 1-2-3) está redactada como aplicación al corredor, no como metodología general con ejemplo | "La secuencia analítica correcta para un supuesto de doble residencia potencial en el corredor Gipuzkoa-Francia es, por tanto: (1) verificar si España reclama la residencia..." |
| `concierto_foral/boe-ley-12-2002-concierto-economico.md` | Sesgo en título de un epígrafe de Contenido, en Doctrina y en Conclusión; ficha matriz del bloque foral, con valor general más allá del caso de estudio | "Retenciones sobre rendimientos del trabajo y regla expresa de teletrabajo (Art. 7) — dato duro, núcleo de conexión con el corredor Gipuzkoa-Francia" (título de sección) |
| `concierto_foral/boe-ley-3-2025-modificacion-concierto-economico.md` | Sesgo en un párrafo completo de Contenido, en Doctrina y en Conclusión | "El cambio de fondo real de esta reforma para el TFG no es la incorporación del Pilar Dos... sino la autonomización del IRNR..." |
| `concierto_foral/norma-foral-3-1990-sucesiones-donaciones.md` | Sesgo repartido en Contenido, Doctrina y Conclusión — **ver duda en §4**, defendible también como ARCHIVE | "Dato de relevancia directa para el TFG si se explora la sucesión/donación de un trabajador transfronterizo recién trasladado a Gipuzkoa desde Francia" |
| `concierto_foral/norma-foral-3-2025-impuesto-complementario.md` | Sesgo en Doctrina y sobre todo en Conclusión, atado explícitamente a que el TFG "explore" el Concierto en materia de teletrabajo | "...podría servir de contraste metodológico si el TFG explora cómo se articula... la aplicación del CDI España-Francia por las Diputaciones Forales..." |

---

## 4. Las dos fichas con duda genuina (tu decisión: REWRITE o ARCHIVE)

- **`concierto_foral/norma-foral-3-1990-sucesiones-donaciones.md`** (ISD guipuzcoano) — aporta datos sin equivalente en el resto del corpus (regla de cuarentena de 5 años, mecanismo unilateral de deducción del Art. 22), pero es mecánica interna de un único Territorio Histórico. Clasificada REWRITE por precaución, defendible como ARCHIVE.
- **`concierto_foral/norma-foral-3-2025-impuesto-complementario.md`** (Impuesto Complementario foral) — mismo dilema: doctrina de interés general sobre cómo el derecho blando internacional se recibe en sistemas fiscales descentralizados, pero de alcance territorial estrecho.

---

## 5. Patrones por sub-bloque

**Serie DAC1-DAC8 (8 fichas):** las ocho son KEEP. Contenido normativo neutro y correcto en las ocho; el sesgo vive en el párrafo final de "Conclusión jurídica" — en siete de las ocho, en una sola frase. `DAC4` es la única con el sesgo repetido dos veces (cierre de Doctrina + Conclusión), pero sigue siendo KEEP, no REWRITE.

**Bloque Pilar Dos/GloBE (6 fichas):** las seis son KEEP. Contenido genuinamente útil para un corpus de propósito general de Impuesto sobre Sociedades — la relevancia está mal enmarcada en la frase de cierre, no en el fondo. Hay solapamiento parcial (no duplicación) entre `pilar-dos-globe-administrative-guidance-2023` y `pilar-dos-globe-consolidated-commentary-2025`: cada una documenta datos duros distintos y no repetidos en la otra. Fusionarlas sería una decisión editorial de eficiencia, no una corrección de sesgo — no se recomienda en esta fase.

**Bloque `concierto_foral/` (5 fichas, no 4 — se añade `norma-foral-2-2005-lgt-gipuzkoa.md`):** el bloque con más matiz. `boe-ley-12-2002` (Concierto Económico, norma matriz) y `boe-ley-3-2025` (su reforma) tienen valor general defendible — documentan el funcionamiento del sistema de concierto vasco, de interés para cualquier análisis de fiscalidad foral, no solo para el corredor. `norma-foral-2-2005-lgt-gipuzkoa` es la más neutra de las cinco (KEEP). Las dos restantes son las de duda genuina de §4.

---

## 6. Nota de método

Clasificación por lectura completa (Hechos + Contenido + Doctrina aplicada + Conclusión jurídica) de las 43 fichas, no por grep. Nada se ha modificado, borrado ni sobrescrito — ni en el corpus canónico (`Desktop\Cerebros_Fiscales`) ni en la copia congelada (`Cerebros_Fiscales.pre-migracion`) ni en `backup/pre-limpieza-corpus`.
