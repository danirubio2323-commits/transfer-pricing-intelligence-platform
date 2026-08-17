---
name: investigar-norma
description: Investigar Derecho de precios de transferencia y fiscalidad internacional para AMPLIAR EL CORPUS, y convertir el hallazgo en ficha citable. Úsala con peticiones amplias — "jurisprudencia alemana sobre ajuste secundario", "las normas de precios de transferencia de Italia", "qué dice la UE sobre servicios intragrupo" —, no solo cuando ya se sabe el artículo exacto. Encadena BOE, EUR-Lex, CENDOJ y Zotero, tría lo que merece ficha, y escribe el frontmatter que el indexador exige. Es trabajo de BACKSTAGE: la aplicación nunca sale a la red.
---

# Investigar una norma y convertirla en ficha

## Cuándo usarla

Peticiones **amplias**, que es como se investiga de verdad:

- «Busca jurisprudencia alemana sobre ajuste secundario»
- «¿Cuáles son las normas de precios de transferencia de Italia?»
- «Qué dice la UE sobre servicios intragrupo de bajo valor añadido»
- «Necesito algo sobre safe harbours en Portugal»

También sirve si ya sabes la referencia exacta, pero no es el caso normal: lo
habitual es explorar, ver qué hay, y decidir después qué merece ficha.

## Lo primero, porque condiciona todo lo demás

**Esto es backstage.** La aplicación TPIP corre en un proceso, en local, sin
servicios externos. Ninguna de estas herramientas se llama nunca desde `apps/`,
`tp_domain/` ni `ai/`. El circuito es:

```
BOE · EUR-Lex · CENDOJ · Zotero  →  tú escribes la ficha  →  la app la indexa y la cita
     (aquí, investigando)            (Markdown en disco)      (paso 19, sin red)
```

Si alguna vez parece buena idea que una vista consulte el BOE en caliente, no lo
es: convierte la aplicación en algo que depende de que responda un servidor
ajeno, y cuando falle no se sabrá si es el código, la red o ellos.

**Y una ficha no es una regla.** Escribir la ficha de Italia **no** modela
Italia: sigue saliendo `NOT_MODELLED` hasta que se toque el mapa de reglas, y eso
lo gobierna la skill `anadir-jurisdiccion`, que se invoca después. Asignarle a un
país la regla de otro por analogía es inventar Derecho comparado.

## Las cuatro fases

### 1 · Explorar

Elige la herramienta por jurisdicción, no por costumbre:

| Qué buscas | Con qué |
|---|---|
| Legislación española consolidada, artículos, versiones | `mcp-boe` — `search_consolidated_legislation`, `search_law_articles`, `get_law_text_block` |
| Jurisprudencia española (TS, AN, TSJ, TEAC) | `cendoj` — `buscar_jurisprudencia`, luego `obtener_texto_resolucion` |
| Derecho de la UE: directivas, CELEX, TJUE | `eur-lex` — `eurlex_search_documents`, `eurlex_get_cases`, `eurlex_get_document` |
| Concepto EuroVoc antes de filtrar en EUR-Lex | `eurlex_browse_subjects`, y pasa la URI devuelta al filtro |
| Bibliografía propia, PDFs anotados | `zotero` — `zotero_semantic_search`, `zotero_get_item_fulltext` |
| **Cualquier otra jurisdicción** (DE, IT, FR, PT…) | **No hay MCP.** `WebSearch` + `WebFetch` contra la fuente oficial del país |

**Sé explícito sobre la última fila.** Alemania, Italia y el resto no tienen
servidor dedicado. Se llega a ellos por web, y eso cambia lo que se puede afirmar
sobre la verificación — ver fase 4.

Empieza ancho y estrecha: primero qué existe, después qué dice.

### 2 · Triar

No todo lo que aparece merece ficha. Antes de capturar nada, responde:

- **¿Es fuente primaria o comentario?** Un artículo de doctrina orienta, pero no
  se cita en un informe. El corpus solo admite lo primero.
- **¿Está vigente?** Una norma derogada puede seguir siendo útil como contexto
  —la propuesta de Directiva de 2023 está fichada precisamente por eso— pero
  entonces su ficha lo dice en el cuerpo, sin ambigüedad.
- **¿Aporta una regla que el motor pueda usar, o es contexto?** Ambas cosas
  valen, pero la primera es la que desbloquea una jurisdicción.
- **¿Ya está en el corpus?** Mira `documentation/tax-research/` antes de
  duplicar. Ampliar una ficha existente suele ser mejor que abrir otra.

Di en voz alta qué descartas y por qué. Un corpus crece mejor con criterio
explícito que con volumen.

### 3 · Capturar

Trae el **texto**, no el resumen. `obtener_texto_resolucion`, `get_law_text_block`
o `eurlex_get_document` dan el cuerpo; los buscadores dan solo la referencia.

Guarda en Zotero lo que vayas a volver a necesitar: `zotero_add_item` con el
identificador, y `zotero_attach_file` si hay PDF. Las anotaciones que hagas allí
son recuperables después con `zotero_get_annotations`.

Los artículos concretos **se sacan trabajando el documento**, no antes. Es el
orden natural: primero tienes el texto delante, después decides qué apartado
manda.

### 4 · Estructurar la ficha

Ubicación, por jurisdicción:

```
documentation/tax-research/jurisdictions/<pais>/   ES, DE, EU… un directorio por país
documentation/tax-research/frameworks/             OCDE, marcos transversales
documentation/tax-research/processes/              doctrina administrativa, procedimiento
```

La `jurisdiccion` **se deduce de la carpeta**, no del frontmatter. `frameworks/` y
`processes/` no son jurisdiccionales.

Frontmatter obligatorio — las ocho claves, todas no vacías:

```yaml
---
titulo: "Alemania — §1.3a AStG: estrechamiento del rango y ajuste a la mediana"
fuente_primaria: "Außensteuergesetz (AStG), §1.3a"
rango_normativo: "Ley federal"
clase: "legislation"                                # legislation | guidelines | case_law | dataset
tipo_localizador: "url"                             # boe_id | url | offline | internal
localizador: "https://www.gesetze-im-internet.de/astg/__1.html"
verificada_el: 2026-08-17
confianza_verificacion: "primary_source_verified"   # o directed_reading
---
```

Puedes conservar además las claves propias del proyecto —`origen`, `tipo`,
`usar_en`, `enlaces`— que sirven para trabajar en Obsidian. El esquema es
ampliable; lo que no es opcional son las ocho de arriba.

**Cuatro reglas que no se saltan:**

1. **`clase`, `tipo_localizador` y `confianza_verificacion` salen del vocabulario
   cerrado de `tp_domain/sources.py`.** Un valor fuera de ahí rompe el indexado.
2. **Nunca inventes un localizador.** Si la norma no tiene identificador público
   resoluble, `tipo_localizador: offline` y el localizador es la referencia del
   documento tal como la citarías en un escrito. Un identificador inventado es
   peor que uno ausente: parece verificable.
3. **`confianza_verificacion` es una afirmación sobre lo que hiciste, no sobre lo
   fiable que parezca la fuente.** `primary_source_verified` solo si leíste el
   texto primario. Si te apoyaste en un resumen o en una lectura dirigida,
   `directed_reading`. Una fecha de verificación sola sugiere más certeza de la
   que hubo — para eso existe este campo.
4. **Si la ficha corresponde a una entrada del registro cerrado de
   `tp_domain/sources.py`, su `localizador` debe coincidir carácter a carácter con
   el `locator` de esa entrada.** Hay un gate que lo comprueba.

## Al terminar

```bash
uv run python manage.py reindexar_corpus
```

Reconstruye el índice desde los `.md`. El fichero en disco es la fuente de verdad;
la tabla `Ficha` solo lo refleja.

Después, y solo si lo investigado aporta una **regla estadística** de una
jurisdicción nueva, invoca `anadir-jurisdiccion`. Esa skill impone el orden
correcto: ficha primero, registro de fuentes después, mapa de reglas al final.

## Qué NO hace esta skill

- No toca `JURISDICTION_RANGE_RULES`. Eso es `anadir-jurisdiccion`.
- No añade entradas al registro de `tp_domain/sources.py` por su cuenta.
- No escribe unidades de estudio: el material didáctico es otra entidad y **nunca
  es fuente citable en un informe**.
- No consulta nada desde el código de la aplicación. Nunca.
