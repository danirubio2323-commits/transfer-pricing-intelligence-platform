# Fase 0 — Arquitectura de la capa jurídica y de conocimiento de TPIP

Fecha: 10 agosto 2026
Estado: **informe de arquitectura. No se ha modificado, movido ni borrado ningún fichero. No se han creado commits. Nada de lo descrito aquí está implementado.**
Método: lectura completa del código real (`tp_domain/models.py`, `tp_domain/sources.py`, `ai/validators.py`, `ai/schemas.py`), lectura de los 8 documentos previos de `documentation/`, inventario dirigido de `tp_domain/knowledge/Cerebros_Fiscales/` y de su copia externa, verificación de git (`merge-base`, `branch --contains`, `check-ignore`), y tres perspectivas independientes de Council sobre la misma pregunta de arquitectura, orquestadas manualmente vía la herramienta `Agent` (no existe un producto o skill separado llamado "Council" — es una orquestación de esta sesión).

Convención de confianza, heredada de `auditoria-capa-juridica-2026-08-10.md` para mantener continuidad: **[V]** verificado por lectura directa de código/fichero o ejecución de comando, **[I]** inferencia razonada, **[NV]** no verificado en esta fase.

Nota sobre el uso de agentes: el inventario del repositorio, el inventario del corpus y las tres perspectivas del Council se delegaron en subagentes independientes (trabajo exploratorio y de perspectivas paralelas). La síntesis, la resolución de los desacuerdos entre perspectivas y este documento son razonamiento directo de esta sesión. No puedo verificar ni afirmar qué proveedor de modelo atendió cada subagente — ver §7.4.

---

## 1. Executive verdict

El Council coincide, **sin disidencia entre las tres perspectivas**, en rechazar SQLite, base de datos vectorial y RAG para la capa de evidencia jurídica de TPIP en su volumen actual (5 fuentes ejecutables, 2 jurisdicciones modeladas). La recomendación es **Alternativa A: filesystem + Python/YAML + Git, sin base de datos**, evolucionando el patrón que `tp_domain/sources.py` ya usa hoy, no sustituyéndolo por infraestructura nueva.

El desacuerdo real del Council no es A vs. B/C/D — es **cuánta estructura añadir dentro de A**. Una perspectiva propone extender `Source` con 4-5 campos planos, en el mismo fichero. Otra propone un modelo más rico con 13+ campos, tipado por casos (jurisprudencia vinculante vs. doctrina, fuente offline vs. resoluble). La síntesis de este informe (§6) resuelve ese desacuerdo tomando el núcleo mínimo defendible de la segunda propuesta, sin la paquetización (`tp_domain/evidence/` como módulo separado, YAML por país) que la primera perspectiva demuestra que no aporta nada verificable a este volumen.

Dos hallazgos de esta fase no estaban en ningún documento previo y cambian el orden de prioridad de la implementación:

1. **El corpus `Cerebros_Fiscales` existe en dos copias físicas independientes** (194 MB cada una, no symlink). Están hoy verificadas byte a byte idénticas en su contenido jurídico — pero una sigue activa como entorno de trabajo y la otra quedó congelada dentro de un directorio gitignored del repo TPIP. Sin corregirlo, van a divergir, y nada lo detectará cuando ocurra.
2. **El 40% del wiki fuera de `sub_tp/` (46 de 116 fichas) sigue redactado con un sesgo hacia un caso de estudio de otro proyecto** (un TFG de residencia fiscal en el corredor Gipuzkoa-Francia). El propio corpus lo documenta y lo corrigió parcialmente el 21 de julio para `sub_tp/`, pero no para el resto. Es relevante porque las dos fuentes OCDE más citadas por el motor de TPIP derivan, en última instancia, de una ficha (`sub_tp/beps-acciones-8-10...`) cuya razón de inclusión declarada explícitamente en el propio texto es "el interés académico del TFG", no la neutralidad de propósito general que TPIP necesita.

Ninguno de los dos invalida el trabajo ya hecho. Ambos son gaps de higiene documental y de proceso, no de diseño del motor, que sigue siendo — verificado de nuevo en esta fase — sólido: 172 tests en verde, separación motor/evidencia/IA respetada por construcción.

---

## 2. Council debate

Tres perspectivas independientes analizaron la misma pregunta sin verse entre sí. Convergencias y desacuerdos, tal como ocurrieron:

### Donde coinciden las tres, sin matices

- **Alternativa A** (filesystem + Git, sin BD) es la arquitectura correcta al volumen actual (5-60 fuentes previsibles a medio plazo).
- **SQLite no aporta nada verificable** a este volumen: ninguna consulta que TPIP necesite hoy requiere un motor relacional; un `dict`/YAML filtrado en memoria resuelve lo mismo, y Git da un histórico auditable que un fichero binario SQLite no da (`git diff` legible vs. dump binario).
- **Vector DB/RAG es la opción más peligrosa de las cinco**, no solo la más innecesaria: introduce recuperación por similitud semántica exactamente en el punto donde la regla de gobernanza del proyecto exige selección determinista y verificada por humano. Las tres perspectivas coinciden en que esto no es "prematuro", es "no debería construirse aquí" salvo, como mucho, como ayuda de búsqueda para el investigador humano sobre el corpus bruto — nunca como fuente de la que el motor cite en runtime.
- **Los MCP jurídicos son herramienta de investigación, nunca de runtime** — ratifica el "Camino B" del audit del 10 de agosto. El sondeo en vivo ya demostró por qué: búsqueda ciega en BOE devolvió normativa urbanística valenciana, CENDOJ devolvió 7.970 resultados ordenados por fecha con casos de tráfico de drogas mezclados.
- **Cerebros Fiscales permanece fuera del producto**: no se integra, no se indexa, no se parsea con código nuevo. TPIP consume un subconjunto minúsculo, curado a mano.
- **`official_ref` como texto libre sin tipo es el gap más grave del modelo actual**, porque impide distinguir programáticamente una fuente verificable (`BOE-A-2014-12328`) de una que no lo es (`AStG §1 Abs. 3a`, que no es identificador de nada) o de una ausente (las dos fuentes OCDE, las más citadas del sistema, no tienen ninguna).
- **La fuente alemana (`de-astg-1-3a`) es el punto más frágil del producto**: su propio disclaimer admite lectura "dirigida, no exhaustiva", y no existe ningún MCP que permita verificarla contra fuente primaria. Dos perspectivas (trazabilidad jurídica y red-team) llegaron a esto de forma independiente y coinciden en la misma conclusión: un campo `verified_at` uniforme, sin graduar, **sobre-representa la fiabilidad de esta fuente exactamente donde más importa que no lo haga**.

### Donde discrepan, explícitamente

| Punto | Perspectiva minimalista | Perspectiva trazabilidad jurídica | Perspectiva red-team |
|---|---|---|---|
| ¿Módulo `tp_domain/evidence/` separado? | No — ampliar `Source` en `sources.py`, in situ | No se pronuncia sobre paquetización, se centra en campos | No — cuestiona que sea necesidad técnica y no preferencia estética; cita que el propio audit admite que ampliar `Source` es "mecánico, no rediseño" |
| ¿YAML por jurisdicción? | No — seguir con Python hardcoded | No se pronuncia | No — un único fichero/directorio pequeño con Pydantic, no partición prematura |
| Nº de campos nuevos | ~4-5, planos, sobre `Source` | 13, con 3 sub-modelos anidados + 5 campos adicionales no contemplados en la propuesta original (`superseded_by`, `binding_effect`, `evidentiary_tier`, `verification_method`, `ai_assisted`) | No propone un modelo cerrado; se centra en el problema de las dos copias y en la graduación de confianza |
| `review_due` | Derivado (`verified_at` + política fija), no almacenado — un campo guardado puede desincronizarse de la política | Almacenado, con mecanismo de degradación (warning en el informe si vence) | No se pronuncia directamente |
| `retrieved_by` / autoría | Redundante con `git blame`, eliminar | Lo separa de `verified_by` (persona) — necesario en cuanto haya más de un contribuyente | No se pronuncia |
| Confianza graduada | No lo propone | **Sí** — dos niveles mínimos (`primary_source_verified` vs. `directed_reading`) para no confundir Art. 18.4 LIS (verificable) con AStG (no verificable hoy) | **Sí, de forma independiente** — mismo argumento, con el mismo caso (AStG) como ejemplo |
| Problema de las dos copias del corpus | No lo trata | No lo trata | **Sí, con propuesta concreta**: ubicación física única + referencia por variable de entorno + chequeo automatizado que falla si aparece una segunda copia |
| ¿Dónde debería vivir la evidencia verificada a largo plazo? | Dentro de `tp_domain/`, como hoy | Dentro de `tp_domain/`, como hoy | Cuestiona si debería vivir dentro del repo de TPIP en absoluto, dado que el corpus (y potencialmente la evidencia derivada) ya es multi-proyecto — lo marca como decisión a tomar antes de escalar, no ahora |

**Resolución de estos desacuerdos** (síntesis de esta sesión, no de ningún agente): la coincidencia independiente de dos perspectivas en la necesidad de graduar confianza — llegando por caminos distintos al mismo caso concreto (AStG) — pesa más que la ausencia de esa idea en la tercera, que no la contradice, simplemente no la trata. Se incorpora. La paquetización en módulo separado y YAML no tiene ningún argumento a favor que sobreviva al escrutinio de las tres perspectivas — se descarta. El problema de las dos copias, señalado solo por una perspectiva pero con evidencia verificada de forma independiente por esta sesión (§4), se trata como hallazgo confirmado, no como opinión de una sola voz. La pregunta sobre si la evidencia debería vivir fuera del repo de TPIP se traslada a §12 (decisión abierta) — no hay volumen suficiente hoy para forzarla, pero es la pregunta correcta para el día en que exista un segundo proyecto fiscal activo del usuario con necesidad de evidencia compartida.

---

## 3. Arquitectura recomendada

```
RAW jurídico (117 PDF + 6 HTML, ~192 MB)
  vive en UNA ubicación física fuera del repo de TPIP (§5)
      │
      │  lectura humana + investigación asistida por Claude/MCP
      │  (BOE, EUR-Lex, CENDOJ, Zotero — solo en esta fase, nunca en runtime)
      ▼
Cerebros Fiscales / wiki (116 fichas Markdown, frontmatter YAML)
  capa intelectual — doctrina destilada, NO citable directamente por el motor
  permanece fuera del repo de TPIP, referenciada, no copiada
      │
      │  selección humana deliberada de un subconjunto mínimo,
      │  con verificación adicional contra fuente primaria cuando es posible
      ▼
tp_domain/sources.py  (registro CERRADO, ampliado — no un módulo nuevo)
  capa probatoria — Evidence con jurisdicción, locator tipado, quote,
  verified_at + nivel de confianza, review_due derivado
      │
      │  resolve(ids) -> List[Source]  (misma interfaz que hoy)
      ▼
tp_domain/rules/  +  tp_domain/calculations/
  el motor. Determinista, offline, no cambia con esta fase.
      │
      ▼
AnalysisResult  (validator: toda cita ⊆ sources — ya existe, no se toca)
      │
      ├──► infrastructure/report/pdf_report.py   (siempre, sin red)
      └──► ai/  (Claude explica, opcional, aditivo, nunca decide)
```

Lo que cambia respecto a hoy: `sources.py` gana campos, no vecinos. El corpus sale del árbol de TPIP en vez de vivir gitignored dentro de él. Nada más se mueve.

---

## 4. Modelo de conocimiento — cómo conviven RAW, Cerebros Fiscales, Evidence y TPIP

Cuatro capas con una regla de responsabilidad estricta, verificada contra el estado real, no aspiracional:

**RAW** — los 117 PDF y 6 HTML. Inmutables una vez ingeridos. Nadie los lee en runtime, ni siquiera Cerebros Fiscales los relee salvo para verificar o corregir una ficha. **[V]** ningún `.py` del repo TPIP contiene `Cerebros`/`knowledge`/PDF-parsing.

**Cerebros Fiscales (wiki/)** — la doctrina ya destilada. 116 fichas, frontmatter YAML 100% parseable **[V, hasheado y contado en esta fase]**, headings parcialmente normalizados (las fichas anteriores al 21 de julio de 2026 usan una estructura distinta a las posteriores — **[V]**, verificado leyendo la ficha más antigua del sub-cerebro `sub_tp/` frente a las demás). Es material de trabajo del analista. **No es citable directamente por el motor de TPIP** — ni hoy ni en el diseño propuesto. Su función es alimentar, mediante lectura humana, las entradas del registro de evidencia — nunca ser el `locator` de una `Source`.

**Evidence Store (`tp_domain/sources.py`, ampliado)** — el subconjunto mínimo, verificado y congelado que el motor puede citar. Hoy 5 entradas; el diseño de §6 no cambia ese volumen, lo hace defendible. Es la única capa que el motor toca.

**TPIP** — consume Evidence Store por `id`, nunca el corpus, nunca el RAW.

La relación entre capas es de **puntero, no copia**, tal como ya proponía el audit del día 10 — pero el puntero solo funciona si apunta a un sitio que existe de forma estable para cualquiera que clone el repo. Hoy no lo hace (§11, riesgo #1).

---

## 5. Arquitectura de almacenamiento

### RAW y Cerebros Fiscales

Confirmado por el Council y por la evidencia recogida en esta fase: **los PDF no deben vivir dentro de ningún repositorio de código**, ni de TPIP ni, necesariamente, de Cerebros Fiscales — 192 MB de material mayoritariamente de terceros con condiciones de reutilización no verificadas fichero a fichero (`plan-limpieza-corpus.md` ya lo señaló para el commit `95c250a`, que fue correctamente expulsado del historial — §9).

**Hallazgo verificado en esta fase**: existen hoy dos copias físicas completas e independientes (no symlink, confirmado con `Get-Item ... LinkType` vacío):
- `C:\Users\LEINAD\Desktop\transfer-pricing-intelligence-platform\tp_domain\knowledge\Cerebros_Fiscales` (dentro del repo TPIP, gitignored)
- `C:\Users\LEINAD\Desktop\Cerebros_Fiscales` (fuera del repo, activa — recibe cambios de tooling hasta el 9 de agosto)

**[V] Contenido jurídico idéntico hoy**: hasheado byte a byte el 100% de `wiki/` (116/116 ficheros) y el 100% de `raw/` (123/123 ficheros) — cero diferencias. La única divergencia está en artefactos de sesión (`AGENTS.md`, `skills-lock.json`, `.claude/settings.local.json`), no en contenido jurídico. El riesgo no es que hayan divergido — es que la copia de fuera sigue viva y la de dentro está congelada desde finales de julio; sin corrección, divergerán.

**Política recomendada**:
1. Ubicación física única: `C:\Users\LEINAD\Desktop\Cerebros_Fiscales`, ya existente, ya activa, ya usada por al menos un proyecto hermano del usuario (**[V]**, confirmado que existe `Desktop/cerebro-tfg-regimen-transfronterizo` como directorio adyacente).
2. La copia dentro de `tp_domain/knowledge/` se retira del árbol de trabajo de TPIP (fuera del alcance de esta fase — es una acción sobre ficheros, no de diseño; queda para la fase de implementación).
3. Cualquier script futuro de TPIP que necesite el corpus (p. ej. un poblador manual del registro de evidencia) lo referencia por variable de entorno (`CEREBROS_FISCALES_PATH`), nunca por ruta relativa interna al repo.
4. Un chequeo barato y automatizable (no un recordatorio manual, que ya se ha demostrado insostenible en la práctica según el propio historial del corpus) que falle ruidosamente si detecta una segunda copia del corpus dentro del árbol de TPIP.

**Documentos originales, versiones, derogación, duplicados**: no hay comparables numéricos ni normativa derogada activa en el registro actual (5 entradas, ninguna con `in_force_to` conocido). La política mínima defendible: un documento derogado se marca con `in_force_to` + `superseded_by` apuntando al reemplazo (§6); nunca se sobrescribe una entrada existente — se añade una nueva y la antigua queda con su vigencia cerrada, siguiendo la convención que el propio corpus origen ya aplica (`### ⚠️ Conflicto Doctrinal / Evolución de Criterio`, impuesta literalmente por `CLAUDE.md` del corpus).

**Backup**: heredado de Git para la Evidence Store (ver §6); para el corpus, responsabilidad del propio flujo de trabajo del usuario fuera de TPIP — no es competencia de esta plataforma.

---

## 6. Modelo Evidence — campos, tipos, relaciones

Síntesis final tras resolver el desacuerdo de §2. Extiende `tp_domain/models.py` y `tp_domain/sources.py` **en sitio** — no crea `tp_domain/evidence/` como paquete nuevo, no introduce YAML.

```python
class EvidenceKind(str, Enum):          # sustituye a SourceKind, mismos 4 valores + 1
    LEGISLATION = "legislation"
    CASE_LAW = "case_law"
    GUIDELINES = "guidelines"
    ADMINISTRATIVE_DOCTRINE = "administrative_doctrine"   # nuevo: DGT/AEAT, distinto de jurisprudencia
    DATASET = "dataset"

class LocatorType(str, Enum):
    BOE_ID = "boe_id"; CELEX = "celex"; ELI = "eli"; ECLI = "ecli"
    TEAC_RG = "teac_rg"; URL = "url"; OFFLINE = "offline"

class BindingEffect(str, Enum):         # solo relevante para CASE_LAW / ADMINISTRATIVE_DOCTRINE
    BINDING_GENERAL = "binding_general"
    PERSUASIVE_ONLY = "persuasive_only"
    NOT_APPLICABLE = "not_applicable"   # default para legislación/guidelines

class VerificationConfidence(str, Enum):    # el campo que resuelve el caso AStG
    PRIMARY_SOURCE_VERIFIED = "primary_source_verified"   # leído y confirmado contra fuente primaria resoluble
    DIRECTED_READING = "directed_reading"                 # lectura dirigida, no exhaustiva, sin fuente primaria consolidada verificable hoy

class Source(BaseModel):                # ampliación de la clase actual, no reemplazo
    model_config = ConfigDict(frozen=True)

    id: str
    kind: EvidenceKind
    citation: str
    pinpoint: Optional[str] = None

    jurisdiction: str                        # NUEVO. "ES" | "DE" | "EU" | "OECD" — hoy inferido del prefijo del id, pasa a ser explícito
    locator_type: LocatorType                # NUEVO. Sustituye a official_ref sin tipo
    locator: str                             # NUEVO. Obligatorio SIEMPRE, incluso en OFFLINE (ver validador)
    quote: Optional[str] = None              # NUEVO. Extracto literal. Obligatorio si locator_type == OFFLINE (validador)

    verified_at: dt.date                     # NUEVO
    verification_confidence: VerificationConfidence  # NUEVO — evita que verified_at sobre-represente fiabilidad
    binding_effect: BindingEffect = BindingEffect.NOT_APPLICABLE  # NUEVO, obligatorio si kind en {CASE_LAW, ADMINISTRATIVE_DOCTRINE}

    in_force_from: Optional[dt.date] = None  # NUEVO
    in_force_to: Optional[dt.date] = None    # NUEVO
    superseded_by: Optional[str] = None      # NUEVO. id de otra Source

    research_note: Optional[str] = None      # ya existe — apunta a documentation/tax-research/, NUNCA a Cerebros_Fiscales directamente
    disclaimer: Optional[str] = None         # ya existe. Obligatorio si locator_type == OFFLINE o verification_confidence == DIRECTED_READING

    @model_validator(mode="after")
    def _offline_requires_quote_and_disclaimer(self) -> "Source":
        if self.locator_type == LocatorType.OFFLINE:
            if not self.quote:
                raise ValueError(f"{self.id}: locator_type OFFLINE exige 'quote' (extracto literal) — es la única evidencia verificable que queda sin localizador público.")
            if not self.disclaimer:
                raise ValueError(f"{self.id}: locator_type OFFLINE exige 'disclaimer' explicando por qué no es resoluble públicamente.")
        return self

    @model_validator(mode="after")
    def _case_law_requires_binding_effect(self) -> "Source":
        if self.kind in (EvidenceKind.CASE_LAW, EvidenceKind.ADMINISTRATIVE_DOCTRINE) and self.binding_effect == BindingEffect.NOT_APPLICABLE:
            raise ValueError(f"{self.id}: jurisprudencia/doctrina administrativa exige declarar binding_effect explícitamente.")
        return self
```

**Campos de la propuesta original descartados, con motivo**: `Provision`/`Validity`/`Provenance` como sub-modelos anidados (colapsados en campos planos — ninguna perspectiva del Council defendió la indirección a este volumen); `review_due` como campo almacenado (se deriva: `verified_at` + política fija por `kind`/`jurisdiction`, evita que un campo guardado se desincronice de la política — recogiendo el argumento minimalista); `retrieved_by` separado (redundante con autoría de Git, recogiendo el mismo argumento); `evidentiary_tier` como eje independiente de `kind` (se fusiona: `ADMINISTRATIVE_DOCTRINE` como valor de `kind` ya captura la distinción que se necesitaba, sin añadir un quinto eje).

**Mecanismo anti-obsolescencia** (consenso de §2, con la resolución de esta sesión): `in_force_to` vencido → fallo ruidoso en `resolve()`, mismo patrón que el `KeyError` que ya existe. `superseded_by` poblado → el intento de citar el id antiguo falla con mensaje señalando el reemplazo. `review_due` (derivado, no almacenado) vencido → no bloquea, degrada: el generador de informe emite un `RiskFactor` de severidad `WARNING` citando la fuente pendiente de revisión — mismo patrón que el sistema ya usa para dataset sintético o jurisdicción no modelada.

**Aplicación inmediata al registro de 5 entradas** (dirección, no ejecución en esta fase):
- `es-lis-art18-4`: `locator_type=BOE_ID`, `verification_confidence=PRIMARY_SOURCE_VERIFIED` (ya verificado en vivo con MCP-BOE en el audit del día 10).
- `de-astg-1-3a`: `locator_type=OFFLINE` (no hay MCP alemán), `verification_confidence=DIRECTED_READING` — declarado así de forma honesta, no disfrazado con la misma fecha de verificación que la fuente española.
- `oecd-tpg-2022-cap3` y `cap6`: `locator_type=OFFLINE`, `quote` obligatorio (hoy no existe ningún extracto de ninguna de las dos, pese a ser las más citadas — este es el gap #2 del audit anterior, y con el validador propuesto deja de poder pasar desapercibido).
- `tpip-dataset-v1`: `kind=DATASET`, sin cambios sustanciales — ya tiene disclaimer.
- `CASE_LAW` queda vacío todavía en esta fase (no se inventa jurisprudencia); pero el modelo ya soporta incorporar la doctrina TEAC ya investigada (`documentation/tax-research/processes/doctrina-teac-bilateralidad-y-servicios.md`) con `binding_effect=BINDING_GENERAL` solo para RG 7833/2023, y `PERSUASIVE_ONLY` para las otras dos resoluciones — la distinción que hoy se pierde si se cita sin este campo.

---

## 7. IA y MCP — qué entra en cada fase, qué no entra nunca en runtime

**Fase de investigación** (fuera de ejecución de TPIP, con Claude Code/Cowork asistiendo a un humano): MCP-BOE, EUR-Lex, CENDOJ, Zotero. Su función es ayudar a poblar y verificar entradas de `Source`, nunca a responder por el motor. El sondeo en vivo ya demostró sus límites reales (§2) — son herramientas de investigador, con el mismo cuidado con el que se usa cualquier fuente que hay que contrastar, no un servicio de verificación automática infalible.

**Fase de análisis** (runtime de `ui/app.py`): cero llamadas MCP, cero llamadas de red salvo, opcionalmente, a la API de Anthropic para la sección de explicación — y esa llamada nunca decide el resultado jurídico ni los cálculos, tal como ya funciona hoy, verificado.

**Fase de mantenimiento** (fuera de ejecución, periódica): el chequeo de `review_due` vencido (§6) puede apoyarse en MCP-BOE para las fuentes españolas, que es el único con capacidad de vigilancia normativa razonable hoy (`watch_boe_changes` existe como herramienta). No existe equivalente para AStG, TEAC ni doctrina DGT — hay que decirlo así de claro en el propio informe generado, no fingir cobertura donde no la hay.

### 7.4 — Sobre FCC y el enrutamiento de modelos, resuelto de forma operativa

Esta fase generó una discusión larga sobre routing que el usuario cortó explícitamente pidiendo una regla simple, no más diagnóstico. La regla operativa vigente a partir de ahora: cuando el trabajo se ejecute lanzando Claude Code desde terminal, debe pasar por el wrapper `C:\Users\LEINAD\.local\bin\claude.cmd`, que enruta a FCC (`127.0.0.1:8082`). Esta sesión concreta corre en Claude Desktop/Cowork, contexto explícitamente excluido de esa regla. Los subagentes lanzados vía la herramienta `Agent` durante esta fase no tienen garantía verificable de enrutar por FCC — no se afirma que la usaran, siguiendo instrucción explícita del usuario de no dar por sentado lo que no se puede comprobar. Esto no afecta a la validez del contenido producido: es una cuestión de qué cuota se consumió, no de qué se investigó ni de qué concluyó el Council.

---

## 8. Trazabilidad jurídica — la cadena completa

```
afirmación del informe (p. ej. "el rate del 12% cae en riesgo moderado")
    │
    ▼
regla del motor (statistical_rules.assess(), determinista)
    │
    ▼
Evidence ID (p. ej. "de-astg-1-3a")  ── resuelto vía resolve(), fallo ruidoso si no existe
    │
    ▼
disposición concreta (pinpoint: "§1.3a — estrechamiento del rango y ajuste a la mediana")
    │
    ▼
fuente oficial (locator_type + locator: hoy texto libre sin tipo, con esta fase pasa a tipado)
    │
    ▼
documento/versión (in_force_from/to, superseded_by — no existe hoy, nuevo en esta fase)
    │
    ▼
fecha de verificación + nivel de confianza (verified_at + verification_confidence — el segundo
    campo es el que falta en toda propuesta previa, y es el que impide que AStG "parezca" tan
    verificado como el Art. 18.4 LIS cuando no lo está)
    │
    ▼
estado de vigencia (in_force_to vencido → fallo ruidoso; review_due vencido → degradación visible)
```

**Qué elementos son necesarios para defender una afirmación del sistema, por jurisdicción**:

- **España**: eslabón fuerte hoy — `mcp-boe` resuelve `BOE-A-2014-12328` con texto, en vivo, confirmado. El único gap es que el sistema no lo declara con un campo tipado.
- **Alemania**: eslabón débil, admitido por el propio disclaimer de la fuente. No hay MCP para verificarlo. La solución de esta fase no es fingir que se puede verificar — es declarar `DIRECTED_READING` con honestidad y no usar la misma vara que para España.
- **OCDE**: eslabón sin localizador público (publicación de pago, sin CELEX/ELI). La solución no es inventar un identificador — es `locator_type=OFFLINE` + `quote` obligatorio, que hoy no existe para ninguna de las dos fuentes OCDE del registro pese a ser las más citadas.
- **UE**: no hay entradas UE en el registro ejecutable hoy (la Directiva de intereses y cánones y la propuesta retirada de 2023 están solo en `documentation/tax-research/`, no en `sources.py`). `EUR-Lex` resuelve CELEX de forma limpia — el eslabón más fácil de cerrar si se amplía el registro en Fase 2.
- **Jurisprudencia**: hoy inexistente en el registro pese a estar ya investigada (doctrina TEAC). El gap no es de arquitectura — es que `binding_effect` no existía como campo para representar la distinción entre RG 7833/2023 (vinculante) y las otras dos (no vinculantes), y sin ese campo, incorporarla sería mentir por omisión sobre su peso jurídico real.

**Gap de evidencia declarado, no completado con conocimiento general** (regla explícita de esta fase): no se ha verificado en esta sesión ni el texto vigente del §1.3a AStG contra una fuente primaria alemana, ni el contenido íntegro de las Directrices OCDE 2022 más allá de lo que el corpus ya fichó. Ambas quedan como gap de evidencia abierto, no como afirmación jurídica nueva.

---

## 9. Repository cleanup — KEEP / ARCHIVE / REMOVE CANDIDATE / DO NOT TOUCH

Combinación de los dos inventarios (repo + corpus), sin acción ejecutada. Solo se listan aquí las filas con clasificación distinta de "mantener sin más" o con nota relevante; el detalle completo fila-por-fila producido por ambos agentes queda disponible en el historial de esta sesión si se necesita.

### Repositorio TPIP

| Elemento | Clasificación | Motivo |
|---|---|---|
| `documentation/auditoria-capa-juridica-2026-08-10.md` | KEEP | Referencia vigente, verifica en código el estado post-refactor |
| `documentation/analisis-cerebros-fiscales.md` | KEEP | Única fuente sobre contenido del corpus |
| `documentation/patron-wiki-llm-karpathy.md` | KEEP | Nota técnica atemporal |
| `documentation/plan-limpieza-corpus.md` | DO NOT TOUCH | Traza probatoria del expurgo de `95c250a`; su paso 8 sigue pendiente (ver más abajo) |
| `documentation/entrevista-definicion-tpip.md` | KEEP, con nota | Vigente como producto; TNMM vs. CUP desactualizado, ya señalado en otro sitio |
| `documentation/auditoria-estado-2026-08-09.md` | ARCHIVE | Superada técnicamente; conserva el único registro del riesgo de copyright de `95c250a` cuando aún era reversible |
| `documentation/revision-arquitectura-154dd0b.md` | ARCHIVE | Los 5 bloqueantes que describe ya están resueltos, verificado |
| `documentation/spec-modelo-datos-fase1.md` | ARCHIVE | Especificación ya implementada casi literalmente |
| `documentation/tax-research/**` (9 fichas) | KEEP, con nota | Vigente y citada desde código real; ninguna tiene frontmatter YAML — limita automatización futura, no invalida el contenido |
| `AGENTS.md` | KEEP | Principios de gobernanza vigentes; desviación de stack ya registrada como consciente en otro sitio |
| `Catalogo_Herramientas_IA_Daru.md` | DO NOT TOUCH | Correctamente gitignorado; expone superficie de entorno personal, exclusión ya aplicada y correcta |
| `TPIP.bat.txt` | REMOVE CANDIDATE | Duplicado byte a byte de `TPIP.bat`; ninguno versionado, sin impacto en el repo público |
| `requirements.txt` (`pytest-asyncio`) | ARCHIVE / revisar | Declarado, no usado en ningún test |
| `tp_domain/calculations/arm_length_range.py::load_comparables` | REMOVE CANDIDATE | Sin ningún punto de llamada fuera de su propio módulo, verificado por grep exhaustivo |
| `tp_domain/calculations/arm_length_range.py::calculate_defensibility_score` | REMOVE CANDIDATE | Wrapper sin llamadas; la lógica real se usa inline en `statistical_rules.assess()` |
| `api/` (`__init__.py` de 0 bytes) | DO NOT TOUCH | Placeholder deliberado de fase futura, documentado en tres sitios |
| Rama local `backup/pre-limpieza-corpus` (→ `95c250a`) | DO NOT TOUCH, decisión pendiente | Sigue viva; el plan de limpieza llegó a su paso 7, no al 8 (purga). Sin riesgo de exposición pública mientras no se pushee — pero es la razón de que `.git` pese 149 MB localmente |
| `ai/`, `infrastructure/`, `tp_domain/` (código), `ui/app.py`, `tests/` | KEEP | Coherentes entre sí, 172/172 tests en verde, sin código muerto significativo salvo lo indicado |

### Cerebros Fiscales (fuera del repo de TPIP, referenciado)

| Elemento | Clasificación | Motivo |
|---|---|---|
| `wiki/sub_tp/` (9 fichas) | KEEP | Núcleo de TP, sin contaminación de alcance, citación pinpoint verificada en el 100% de la muestra leída |
| `raw/Normativa_Estatal/` (LIS, RIS) | KEEP | Fuente primaria directa del régimen español |
| `raw/Normativa_Internacional/OCDE_BEPS/` (Directrices TP 2022) | KEEP | Fuente primaria citada con pinpoint desde `sub_tp/` |
| `raw/Jurisprudencia/TEAC/` | KEEP | Fuente primaria de las 3 fichas TEAC ya investigadas |
| `wiki/matriz/`, `wiki/sub_is/` (46 de 116 fichas con sesgo hacia el corredor Gipuzkoa-Francia) | KEEP, con descontaminación pendiente | Base jurídica transversal útil, pero no debe citarse como fuente de alcance general hasta pasar la misma corrección que ya se aplicó a `sub_tp/` el 21 de julio |
| Clúster "Pilar Dos" (8 fichas de doctrina de firma, `sub_is/`) | ARCHIVE / REMOVE CANDIDATE | El propio corpus se autocalifica como "valor marginal" y redundante entre sí — candidatas a fusión, señalado por el propio mantenedor, no por este informe |
| `wiki/concierto_foral/`, `raw/Concierto_Economico_Gipuzkoa/` | ARCHIVE | Fuera del alcance societario de TP; origen explícito en el TFG, no en TPIP |
| `raw/Derecho_Comparado/` (10 PDF, hasta 35 MB cada uno) | ARCHIVE | Ningún ficha del wiki los cita con detalle en la muestra revisada; reserva sin digerir |
| Copia de `Cerebros_Fiscales` dentro de `tp_domain/knowledge/` | Decisión pendiente, ver §5 | Redundante con la copia externa activa; hoy idéntica, mañana no necesariamente |

---

## 10. Migration plan

Orden que respeta la regla ya fijada por el audit anterior y que el Council no cuestiona: cada paso deja el sistema demostrable, ninguno toca el motor hasta que la evidencia esté en su sitio.

1. **Resolver la ubicación única del corpus** (§5). Bloqueante para todo lo demás — no se puede construir evidencia trazable sobre una cadena que apunta a dos sitios.
2. **Descontaminar las 46 fichas fuera de `sub_tp/`** que siguen orientadas al corredor Gipuzkoa-Francia, aplicando la misma corrección que el propio corpus ya hizo el 21 de julio para `sub_tp/`. Necesario antes de citar cualquier ficha de `matriz/`/`sub_is/` como evidencia de propósito general.
3. **Ampliar `Source` en sitio** con los campos de §6, migrando las 5 entradas actuales. Ningún test debería requerir más que ajustes mecánicos de construcción de objetos.
4. **Verificar y datar las 5 fuentes existentes** con `verification_confidence` honesto — Art. 18.4 LIS como `PRIMARY_SOURCE_VERIFIED` (ya lo está), AStG y OCDE como `DIRECTED_READING`/`OFFLINE` con `quote` obligatorio.
5. **Imprimir la trazabilidad ampliada en el informe PDF** — jurisdicción, locator tipado, fecha y nivel de confianza de verificación. Máximo rendimiento por esfuerzo: convierte trabajo invisible en pantalla visible.
6. **Incorporar la doctrina TEAC** con `binding_effect` correcto (solo RG 7833/2023 como `BINDING_GENERAL`).
7. **Frontmatter en las 9 fichas de `documentation/tax-research/`** — alinea con el esquema del corpus origen, prerrequisito de cualquier automatización futura.
8. **Chequeo periódico de `review_due` + purga de la rama `backup/pre-limpieza-corpus`** — fuera del runtime del producto, higiene de repositorio.

Fuera de esta fase, deliberadamente, sin cambios respecto al criterio ya fijado por el audit anterior: validación semántica de contradicción prosa/veredicto, inyección de texto normativo en el prompt de IA, capa API, ampliación de jurisdicciones.

---

## 11. Risks

1. **Las dos copias del corpus divergen antes de que se ejecute el paso 1 del plan de migración.** Es el riesgo más alto de esta fase porque ya está activo — no es hipotético, es una cuenta atrás sin fecha.
2. **La descontaminación del 40% del wiki (paso 2) se pospone indefinidamente** por no ser bloqueante para el motor — y una cita de `matriz/` o `sub_is/` sesgada hacia el TFG termina en un informe de TPIP sin que nadie lo note, porque el sesgo es de tono, no de sintaxis, y ningún validador automático lo detecta.
3. **`verification_confidence=DIRECTED_READING` se trata como un detalle técnico en vez de como la admisión que es** — si el campo existe pero nadie lo lee al construir el informe, es tan decorativo como no tenerlo. Debe consumirse activamente en el texto que ve el usuario final del informe, no solo quedar en el modelo.
4. **La rama `backup/pre-limpieza-corpus` se pushea por accidente** en algún `git push` futuro sin `--force` que arrastre ramas locales de forma no intencionada — bajo, pero real mientras la rama exista.
5. **El validador de referencias normativas (`extract_legal_references`, 5 familias de regex) no cubre citas alemanas** (`Tz.`, `Abs.`, `BMF-Schreiben`) — riesgo ya señalado en el audit anterior, que crece en cuanto se añada jurisprudencia o doctrina alemana citable.

---

## 12. Open decisions

Decisiones que corresponden al usuario, no a este informe:

1. ¿Se retira ya la copia de `tp_domain/knowledge/Cerebros_Fiscales/` del árbol de trabajo, o se pospone hasta implementar el paso 1?
2. ¿Se aplica la descontaminación de las 46 fichas fuera de `sub_tp/` dentro de Cerebros Fiscales (fuera del alcance de TPIP, pero condiciona qué puede citarse desde TPIP con propósito general), o se acepta el filtro manual caso a caso que ya aplican las fichas de `sub_tp/`?
3. ¿Se purga la rama `backup/pre-limpieza-corpus` ahora que el expurgo de `95c250a` está confirmado como no-ancestro y no-pusheado, o se conserva como red de seguridad adicional?
4. ¿La Evidence Store debería, a medio plazo, vivir fuera del repo de TPIP como recurso compartido entre proyectos fiscales del usuario (paralelo a la decisión ya tomada para el corpus), o es prematuro mientras exista un único proyecto consumidor?
5. ¿Se incorpora ya la doctrina TEAC (paso 6 del plan), o se espera a que exista una regla del motor que la consuma, para no añadir evidencia "decorativa" sin consumidor?

---

## 13. Autocrítica

Antes de cerrar, una revisión crítica de la propia recomendación de este Council:

**Dónde podría estar equivocada**: el consenso de "sin base de datos" descansa por completo en que el volumen se mantenga en el orden de decenas de fuentes. Si la Fase 2 del roadmap (más jurisdicciones, servicios intragrupo, safe harbours) se ejecuta con la ambición que sugiere el propio roadmap declarado, el umbral de "unas pocas centenas" que el Council fija para reconsiderar SQLite podría alcanzarse más rápido de lo que el tono general del informe sugiere. El informe trata ese umbral como lejano; no tiene por qué serlo.

**Qué supuesto podría romperse**: todo el diseño de §6 asume que un humano (el usuario) sigue siendo el único poblador y verificador del registro. El campo `verified_by`, descartado en la síntesis por redundante con `git blame`, deja de serlo en el momento en que haya más de una persona tocando el registro — y ese es exactamente el escenario en el que la perspectiva de trazabilidad jurídica lo pedía. La síntesis lo descartó por criterio de "no añadir lo que no hace falta hoy", que es correcto para hoy, pero es el primer campo a revertir si el supuesto de un único mantenedor deja de cumplirse.

**Qué parte es innecesariamente compleja**: el propio modelo de §6, con 4 enums nuevos y 2 validadores, ya es más de lo que la perspectiva minimalista habría aceptado sin objeción. Se incluyó porque dos perspectivas independientes llegaron al mismo campo crítico (`verification_confidence`) por caminos distintos, lo cual es una señal fuerte — pero sigue siendo una señal de dos análisis, no de una necesidad demostrada con el mismo rigor con que se demostró, por ejemplo, la existencia de las dos copias del corpus (hash byte a byte) o la contaminación de alcance (cita literal del propio `log.md`). Si el usuario, al implementar, encuentra que `binding_effect` o `verification_confidence` no se usan de forma consistente en la práctica, es más honesto simplificarlos que mantenerlos como aspiración sin uso real — lo cual sería repetir, a menor escala, exactamente el patrón de "campo con apariencia de rigor sin sustancia" que la perspectiva red-team señaló como riesgo (§4.2 de su análisis original, recogido en §11.3 de este informe).

**Qué se subestima**: el coste humano recurrente de mantener el nivel de honestidad epistémica que el propio corpus ya demuestra (las secciones "⚠️ SIN FUENTE EN EL CORPUS" verificadas en 13/13 fichas leídas). Este informe diseña campos que *permiten* esa honestidad (`DIRECTED_READING`, `OFFLINE` con disclaimer obligatorio) pero no puede garantizar que se rellenen con el mismo rigor que el corpus origen ya demuestra tener. Ese rigor es un hábito de trabajo del usuario, no una propiedad que un modelo de datos pueda imponer por sí solo — el validador impide que el campo quede vacío, no impide que se rellene con menos cuidado del que el propio corpus ya ha demostrado tener hasta ahora.
