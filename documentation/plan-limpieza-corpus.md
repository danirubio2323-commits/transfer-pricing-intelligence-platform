# Plan de limpieza del corpus — Paso 0

Fecha: 2026-08-09
Estado: **propuesta, pendiente de aprobación. No ejecutado.**
Commit objeto de análisis: `95c250a` — "Add: complete transfer pricing corpus (Cerebros_Fiscales)", 262 ficheros, 450.882 líneas, **actualmente HEAD y sin pushear**.

Aviso: no soy abogado y esto no es asesoramiento jurídico. La clasificación por titularidad se ha hecho a partir del editor identificable en el nombre de cada fichero; **no he verificado la procedencia ni las condiciones de reutilización de cada PDF uno a uno**. La decisión final sobre qué se publica es tuya.

---

## 1. Inventario del commit `95c250a`

262 ficheros: 117 PDF, 129 Markdown, 10 JSON, 6 HTML.

### 1.1 Normativa y jurisprudencia pública — riesgo bajo

| Bloque | Nº | Observación |
|---|---|---|
| `Normativa_Estatal/` | 9 | LIS, LGT, IRPF, IRNR, Ley 7/2024, reglamentos |
| `UE_Directivas/` | 22 | ATAD I/II, DAC1-8, Matriz-Filial, Intereses y Cánones, Pilar Dos |
| `Concierto_Economico_Gipuzkoa/` | 11 | Normas forales y Ley 12/2002 |
| `Jurisprudencia/` | 21 | TS, TC, TEAC, TJUE (incl. conclusiones AG), DGT |
| CDI bilaterales (dentro de `Normativa_Internacional/`) | ~19 | 10 convenios, protocolos, MLI |

En Derecho español, las disposiciones legales y las resoluciones judiciales quedan fuera de la protección de la propiedad intelectual (art. 13 TRLPI). El material de la UE tiene reutilización autorizada con mención de la fuente (Decisión 2011/833/UE). El riesgo aquí es bajo — pero **la necesidad también es cero**: ninguna línea de código los lee.

### 1.2 Textos legales extranjeros — riesgo intermedio, sin verificar

`Derecho_Comparado/`, 10 PDF: AStG, KStG y UmwStG (DE), IRC (EE.UU.), CGI (FR), LIR (LU), VPB 1969 (NL), CTA 2010 y TCGA 1992 (RU), LIFD (CH).

Son textos oficiales, pero **no he comprobado de qué portal o edición procede cada PDF**. Algunos portales permiten reutilización (legislation.gov.uk bajo Open Government Licence, gesetze-im-internet.de); de otros no lo sé. Además son los ficheros más pesados del repo: el TCGA 1992 pesa 35 MB él solo, y los tres mayores suman 68 MB.

### 1.3 Material de terceros con copyright — riesgo alto

Aproximadamente **32 documentos**. Es el núcleo del problema.

**Doctrina y notas de firma (14):** EY (×2), KPMG (×2), Deloitte, Garrigues (×2), Cuatrecasas, Uría Menéndez, Fundación Impuestos y Competitividad, Navarro (2021), Benítez Clerie (2020), Alonso Arce (2025), y uno sin autor identificado.

**OCDE (16) y ONU (2):** Directrices de Precios de Transferencia 2022, Modelo de Convenio 2017, informes finales BEPS acciones 2/3/4/6/7, Administrative Guidance y Consolidated Commentary GloBE, Minimum Tax Implementation Handbook, Manual Práctico de Precios de Transferencia de la ONU.

Dos motivos, y el segundo pesa más que el primero:

1. Las condiciones de la OCDE permiten descargar y copiar contenido **para uso propio** con reconocimiento de la fuente; la redistribución y el uso comercial requieren autorización expresa. Publicar los ficheros en un repositorio público es redistribución, no uso propio. Las Directrices de Precios de Transferencia 2022 son además una publicación de pago.
2. El repositorio es público, lleva tu nombre y su destinatario declarado son equipos fiscales de Big Four y tax-tech. Republicar los *tax alerts* de EY, KPMG, Deloitte y Garrigues en el portfolio con el que te presentas ante ellos es un problema de criterio profesional antes que de licencia. Un revisor de esas firmas lo ve en el primer vistazo al árbol de ficheros.

Detalle adicional: el `LICENSE` del repo es MIT. Tal como está, estarías licenciando bajo MIT un árbol que contiene material del que no eres titular.

### 1.4 Ruido que no debería estar en ningún caso

- 10 ficheros `.json` de configuración de Obsidian (`.obsidian/app.json`, `workspace.json`, etc.).
- `CLAUDE.md`, `PAQUETE_MIGRACION_CLAUDE_PROJECT.md` y `Bienvenido.md`: documentación operativa **del proyecto Cerebros_Fiscales**, no de TPIP. Rompe el límite de responsabilidad entre proyectos.

### 1.5 Documentación propia y material derivado — se mantiene

**10 fichas escritas para TPIP** (fuera de `Cerebros_Fiscales/`, autoría propia, originales):

```
tp_domain/knowledge/jurisdictions/spain/art18-lis-operaciones-vinculadas.md
tp_domain/knowledge/jurisdictions/spain/ris-documentacion-masterfile-localfile.md
tp_domain/knowledge/jurisdictions/germany/astg-rango-intercuartilico-ajuste-mediana.md
tp_domain/knowledge/jurisdictions/eu/directiva-intereses-canones-2003-49.md
tp_domain/knowledge/jurisdictions/eu/propuesta-directiva-tp-2023-retirada.md
tp_domain/knowledge/frameworks/ocde-directrices-2022-marcos-riesgo-dempe-servicios.md
tp_domain/knowledge/frameworks/safe-harbours-y-htvi.md
tp_domain/knowledge/data_systems/criterios-seleccion-comparables.md
tp_domain/knowledge/data_systems/patron-wiki-llm-karpathy.md
tp_domain/knowledge/processes/doctrina-teac-bilateralidad-y-servicios.md
```

Son análisis propio con cita a fuente primaria, no reproducción. La de `astg-…` ya apunta explícitamente a `tp_domain/rules/german_rules.py`. Es lo único de todo el commit que tiene valor para el producto.

**114 fichas `wiki/` de Cerebros_Fiscales:** también de autoría propia, pero pertenecen al otro proyecto. Mantenerlas dentro de TPIP duplica conocimiento que ya vive en otro sitio y garantiza que las dos copias diverjan. Se sacan por criterio de ecosistema, no por riesgo legal.

---

## 2. Estrategia propuesta

| Acción | Qué |
|---|---|
| **Sacar del repo** | Todo `tp_domain/knowledge/Cerebros_Fiscales/`: 117 PDF, 6 HTML, 114 fichas wiki, 10 JSON de Obsidian y los 3 documentos del otro proyecto |
| **Mantener** | Las 10 fichas propias, **movidas a `documentation/tax-research/`** |
| **Sustituir por índice** | Un `documentation/tax-research/corpus-index.md` con, por cada fuente que TPIP cite de verdad: título, identificador (BOE-A-…, CELEX, ECLI) y ruta relativa en el corpus canónico. Sin PDFs. **Se construye cuando se codifique `tp_domain/rules/`, no ahora** — el Paso 0 no debe crecer |
| **Añadir a `.gitignore`** | `tp_domain/knowledge/`, `knowledge/`, `**/.obsidian/`, `*.pdf`, `*.epub` |

**Por qué las fichas salen de `tp_domain/`:** `tp_domain/` es lógica fiscal ejecutable (regla §7 de las instrucciones). Markdown de investigación no es dominio. Además, `pyproject.toml` declara `tp_domain` como paquete distribuible; documentación colgando de ahí acabará empaquetada antes o después.

**Sobre `*.pdf` en el `.gitignore`:** te obligará a un `git add -f` deliberado el día que quieras versionar el informe PDF de ejemplo de la demo. Ese es exactamente el punto — que volver a meter un PDF sea un acto consciente y no el resultado de un `git add .`.

**Decisión que necesito de ti antes de tocar nada:** el plan asume que la copia canónica del corpus sigue existiendo en `C:\Users\LEINAD\Desktop\Cerebros_Fiscales`, como indica `documentation/analisis-cerebros-fiscales.md`. **No puedo verificarlo: solo tengo acceso a la carpeta de TPIP.** Confírmalo antes del paso que borra la copia, o el borrado es destructivo.

---

## 3. Impacto

| Ámbito | Impacto | Verificación |
|---|---|---|
| **Código** | **Ninguno** | `grep` sobre `*.py`, `*.toml`, `*.yml`, `*.json`: cero referencias a `knowledge/` |
| **Tests** | **Ninguno** | Los 33 tests importan solo `tp_domain.models` y `tp_domain.calculations`. Deben seguir en verde tras la limpieza |
| **Funcionamiento** | **Ninguno** | Ni la app Streamlit ni el motor leen el corpus. La única fuente de datos es `tp_domain/comparables.json`, que no se toca |
| **Documentación** | Menor | `analisis-cerebros-fiscales.md` ya apunta a la ruta externa del Desktop, no al repo. Su propuesta de `infrastructure/wiki_parser.py` seguirá siendo válida, pero deberá leer la ruta de una variable de entorno (`TPIP_CORPUS_PATH`) en vez de una ruta interna. No hay que cambiarlo ahora |
| **Peso** | 193 MB fuera del árbol; `.git` baja de 148 MB a orden de kilobytes tras el `gc` |
| **Lo que se pierde** | Autocontención: el repo deja de llevar sus fuentes dentro. A cambio deja de duplicar conocimiento que vive en Cerebros_Fiscales, que es la regla de ecosistema que ya tienes fijada |

---

## 4. Comandos git propuestos

Situación de partida que hace esto sencillo: `95c250a` **es HEAD y no está pusheado** (`origin/main` sigue en `1564c86`). No hace falta `git filter-repo` ni reescribir historial publicado. Los otros 3 commits locales (tests + CI, limpieza de artefactos, `.gitignore`) son correctos y se conservan.

```bash
# ── 0. Red de seguridad (nada es irreversible hasta el paso 7)
git branch backup/pre-limpieza-corpus 95c250a

# ── 1. Deshacer SOLO el commit del corpus, conservando los ficheros en disco
git reset --mixed HEAD~1
git log --oneline -4          # HEAD debe quedar en 1b1a625

# ── 2. Rescatar las 10 fichas propias fuera de tp_domain/
mkdir -p documentation/tax-research
mv tp_domain/knowledge/jurisdictions documentation/tax-research/
mv tp_domain/knowledge/frameworks    documentation/tax-research/
mv tp_domain/knowledge/data_systems  documentation/tax-research/
mv tp_domain/knowledge/processes     documentation/tax-research/

# ── 3. Eliminar la copia del corpus del árbol de trabajo
#     EJECUTAR SOLO tras confirmar que C:\Users\LEINAD\Desktop\Cerebros_Fiscales sigue existiendo
rm -rf tp_domain/knowledge

# ── 4. Actualizar .gitignore  (edición manual, ver bloque más abajo)

# ── 5. Deshacer el cambio espurio de LICENSE (solo son finales de línea)
git checkout -- LICENSE

# ── 6. Commit limpio — revisar SIEMPRE antes de confirmar
git status
git add .gitignore documentation/tax-research documentation/analisis-cerebros-fiscales.md
git add documentation/entrevista-definicion-tpip.md documentation/auditoria-estado-2026-08-09.md
git add documentation/plan-limpieza-corpus.md AGENTS.md
git status                                          # confirmar que NO aparece ningún .pdf
git commit -m "Add: fichas de investigación fiscal derivadas y documentación de producto

Sustituye al corpus completo: el material de terceros (OCDE, notas de firma,
doctrina) no se redistribuye. La copia canónica vive fuera del repositorio."

# ── 7. Verificación previa al push
git ls-files | grep -Ei "\.(pdf|html|epub)$"        # debe devolver vacío
git log --stat --oneline origin/main..HEAD | head -40
pytest tests/ -q                                     # 33 en verde

# ── 8. Purga local de objetos inalcanzables — PASO IRREVERSIBLE
#     Ejecutar solo cuando el paso 7 sea correcto
git branch -D backup/pre-limpieza-corpus
git reflog expire --expire=now --all
git gc --prune=now
du -sh .git

# ── 9. Publicar
git push origin main
```

Nota sobre el paso 8: mientras la rama `backup/` exista, los blobs del corpus siguen siendo alcanzables y `gc` no los borra — por eso el orden es verificar, luego borrar la rama, luego purgar. Aun sin purgar, `git push` **no** envía objetos inalcanzables: la exposición pública queda resuelta en el paso 6. El `gc` es higiene local y recupera además los 7,2 MB de *garbage* que ya arrastra `.git`.

### Bloque a añadir al `.gitignore`

```gitignore
# Corpus fiscal — vive fuera del repositorio (Cerebros_Fiscales).
# TPIP consume material derivado, no fuentes de terceros.
tp_domain/knowledge/
knowledge/
**/.obsidian/

# Documentos de fuente: nunca se versionan en este repo.
# Para un PDF legítimo (informe de demo), usar `git add -f` de forma deliberada.
*.pdf
*.epub
```

---

## 5. Dos decisiones sueltas, para que no se cuelen por inercia

1. **`Catalogo_Herramientas_IA_Daru.md`** está sin trackear y el comando del paso 6 no lo incluye a propósito. Describe tu entorno completo de IA — MCPs, plugins, autenticaciones. No hay problema de terceros, es tuyo, pero publicarlo en el repo de portfolio es una decisión que conviene tomar a conciencia y no con un `git add .`. Mi recomendación: dejarlo fuera; no aporta nada a TPIP y expone tu superficie de herramientas.
2. **`Derecho_Comparado/`** (bloque 1.2) sale del repo igual que el resto en este plan. Si en algún momento quisieras versionar textos legales extranjeros, habría que verificar antes portal y licencia de origen fichero a fichero. No lo he hecho.
