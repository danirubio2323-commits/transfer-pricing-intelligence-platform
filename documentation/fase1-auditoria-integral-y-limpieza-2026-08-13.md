# Auditoría integral de estado + propuesta de limpieza

Fecha: 13 agosto 2026
Estado: **auditoría de solo lectura. No se ha modificado, movido ni borrado ningún fichero. No se han creado commits.**
Método: verificación directa del estado real en este momento (`git status`, `git branch -a`, `git log`, `git diff --stat`, ejecución de la suite de tests, `du`/`find`/`grep` sobre disco) — no se ha dado por buena ninguna afirmación de sesiones o turnos anteriores sin comprobarla ahora. Donde documentación y realidad no coinciden, se señala explícitamente.

No se ha vuelto a investigar routing/FCC. No se ha rehecho la clasificación de las 43 fichas ni la neutralización de las 8 ya aplicadas — se han dado por buenas, con un único hallazgo objetivo señalado en §Objetivo 2.

---

## Objetivo 1 — Estado del proyecto

### A. HECHO — terminado y verificado ahora mismo

- **Fase 0 completa**: informe de arquitectura y Council en `documentation/informe-fase0-council-arquitectura-juridica-2026-08-10.md` (38,8K, presente y legible).
- **Migración reversible del corpus**: `C:\Users\LEINAD\Desktop\Cerebros_Fiscales` es la copia canónica activa (194M, verificado ahora); `tp_domain\knowledge\Cerebros_Fiscales.pre-migracion` es la copia congelada (194M, verificado ahora). `tp_domain\knowledge\` no contiene ninguna otra carpeta — el renombrado se mantiene limpio, sin residuos.
- **Clasificación de 43 fichas** (no 41 — corrección ya hecha y documentada en su momento) en `documentation/fase1-clasificacion-corpus-sesgo-territorial-2026-08-10.md`: 35 KEEP, 8 REWRITE.
- **8 fichas REWRITE neutralizadas sobre el corpus canónico**, en dos pasadas (24 fragmentos + 2 correcciones 🔎, luego 7 fragmentos adicionales encontrados en verificación posterior). Verificado ahora: cero copias congeladas tocadas, `backup/pre-limpieza-corpus` intacta en `95c250a`.
- **`tp_domain/models.py` y `tp_domain/sources.py` modificados** — confirmado por `git diff --stat`: **+152/-6 líneas** en total, exactamente los dos ficheros esperados, ninguno más.
- **172/172 tests en verde**, re-ejecutados ahora mismo tras todos los cambios de esta fase (48,2 s).
- **Verificación en vivo real de las 5 fuentes**: ES vía `mcp-boe` (BOE-A-2014-12328, vigente), DE vía `gesetze-im-internet.de` (§1 Abs. 3a confirmado contra portal oficial), 2 fuentes OCDE con cita literal extraída directamente del PDF primario (párr. 3.57 y 6.42) — no de memoria.
- **`git status` actual**: rama `main`, 9 commits por delante de `origin/main` (sin cambios desde el inicio de la sesión), 2 ficheros modificados (`tp_domain/models.py`, `tp_domain/sources.py`), 4 ficheros de `documentation/` sin trackear. Nada más.

### B. PENDIENTE — lo que realmente queda de la Fase 1

- **Cero cobertura de test para los campos nuevos de `Source`.** Verificado ahora por grep: ningún test en `tests/` menciona `locator_type`, `verification_confidence`, `LocatorType`, `VerificationConfidence`, `superseded_by`, `in_force_from` ni `in_force_to`. El validador `_offline_requires_quote_and_disclaimer` (el que impide que una fuente OFFLINE se construya sin `quote`/`disclaimer`) nunca se ha ejercitado con un caso que debiera fallar — hoy solo se sabe que no rompe el camino feliz (los 172 tests pasan), no que el validador realmente bloquee lo que debe bloquear.
- El registro persistido del diff de las 8 fichas (`fase1-rewrite-propuesto-8-fichas-2026-08-10.md`) **no incluye los 7 fragmentos de la segunda pasada** — esos solo existen en el historial de esta conversación, no en ningún fichero del repositorio. Es el único rastro duradero de qué cambió exactamente en un corpus que vive fuera de git; hoy está incompleto.
- `documentation/tax-research/` sigue sin frontmatter YAML (gap #7 del audit del 10 de agosto) — no abordado en Fase 1, sigue abierto.
- TEAC y Evidence Store externa: explícitamente fuera de alcance de esta fase, siguen sin empezar.
- Nada de lo anterior es pendiente de código roto — el motor funciona, los tests pasan. Es pendiente de rigor documental y de cobertura, no de funcionalidad.

### C. BLOQUEANTES — decisiones que te corresponden a ti

1. ¿Se borra ya `Cerebros_Fiscales.pre-migracion` (194MB) o se mantiene como red de seguridad mientras no haya una confirmación final de que las 8 fichas neutralizadas están bien?
2. ¿Se purga `backup/pre-limpieza-corpus` ahora que el expurgo de `95c250a` lleva verificado varias veces, o sigue como red de seguridad?
3. ¿Se hace commit ya de `tp_domain/models.py`, `tp_domain/sources.py` y los 4 documentos nuevos, o se sigue trabajando sin comprometer?
4. ¿Se escribe cobertura de test para los campos nuevos de `Source` antes o después de la limpieza/commit?
5. ¿Se completa el registro del diff (los 7 fragmentos de la segunda pasada) en el fichero, o se acepta que quede solo en el historial de conversación?

### D. SIGUIENTE PASO recomendado, y por qué

Orden sugerido, de menor a mayor riesgo: **(1)** aprobar y ejecutar la limpieza de bajo riesgo de este informe (§Objetivo 2) — no toca nada crítico y reduce ruido antes de comprometer nada; **(2)** completar el registro del diff con los 7 fragmentos que faltan (barato, cierra el único gap real de trazabilidad); **(3)** añadir tests mínimos para el validador OFFLINE y los campos nuevos (cierra el gap de cobertura antes de que el código se toque más y el gap se olvide); **(4)** commit; **(5)** entonces PR, si sigues queriendo abrirla. Razón del orden: cada paso reduce el riesgo del siguiente — no tiene sentido comprometer código sin red de tests, ni abrir una PR con un repositorio todavía lleno de ruido documental. Es una recomendación, no una ejecución — nada de esto se ha hecho.

### E. RIESGOS

- **Validador sin test**: si un refactor futuro rompe `_offline_requires_quote_and_disclaimer` sin querer, nada lo detecta automáticamente.
- **4 documentos sin trackear**: existen en disco pero no en git — están a salvo del propio repositorio, pero no de un accidente de filesystem fuera de control de versiones.
- **Doble copia temporal del corpus**: mientras `Cerebros_Fiscales.pre-migracion` exista, hay dos sitios donde alguien podría editar por error; si se edita la canónica de nuevo, la congelada deja de ser un punto de comparación útil salvo que se recuerde cuál es cuál.
- **149MB de blobs de terceros en `.git` local** por la rama `backup/pre-limpieza-corpus` — sin riesgo de exposición pública mientras no se pushee, pero es la razón de que el repositorio pese lo que pesa localmente.
- **Registro de diff incompleto** (ver §B): si en el futuro alguien necesita reconstruir exactamente qué cambió en el corpus y por qué, la mitad de la traza (7 de 31 fragmentos) no está en ningún fichero.

### F. NO TOCAR — debe permanecer intacto por ahora

- `Cerebros_Fiscales.pre-migracion` (copia congelada completa).
- Rama `backup/pre-limpieza-corpus`.
- Las 35 fichas KEEP del corpus canónico.
- La frase deliberadamente excluida en `interfaz-art4-mcocde-residencia-irpf-irnr.md` ("aplicación práctica al corredor").
- Los 5 registros de `tp_domain/sources.py` ya verificados y migrados — no re-verificar de nuevo, ya está hecho y confirmado hoy.
- `api/` (placeholder deliberado, documentado en tres sitios distintos del repo).
- `Catalogo_Herramientas_IA_Daru.md` (correctamente gitignorado).

---

## Objetivo 2 — Tabla de limpieza del proyecto

Clasificación completa. Nada se ha ejecutado — es propuesta para tu aprobación.

| Elemento | Clasificación | Motivo | Riesgo si se ejecuta mal |
|---|---|---|---|
| `documentation/informe-fase0-council-arquitectura-juridica-2026-08-10.md` | **KEEP** | Referencia vigente de arquitectura, activa | — |
| `documentation/fase1-clasificacion-corpus-sesgo-territorial-2026-08-10.md` | **KEEP** | Referencia vigente, base de la neutralización ya aplicada | — |
| `documentation/fase1-rewrite-propuesto-8-fichas-2026-08-10.md` | **ARCHIVE**, con nota | Ya no es una "propuesta" — está aplicada. Sigue siendo el único registro escrito de qué cambió en un corpus que vive fuera de git, así que tiene valor de traza, pero no de trabajo activo. **El nombre ya es engañoso** ("propuesto" cuando está aplicado) y **el contenido está incompleto** (falta la segunda pasada de 7 fragmentos, ver §B) — antes de archivarlo, considera completarlo y renombrarlo (p. ej. `fase1-rewrite-aplicado-8-fichas-2026-08-10.md`) | Si se borra sin más, se pierde la única traza escrita de la neutralización del corpus |
| `documentation/auditoria-capa-juridica-2026-08-10.md` | **KEEP** | Auditoría técnica de referencia, distinta en alcance del informe de Fase 0 (una es técnica de todo el sistema, la otra es la decisión de arquitectura del Council) — no son redundantes | — |
| `documentation/analisis-cerebros-fiscales.md` | **KEEP** | Única fuente sobre contenido y estructura del corpus | — |
| `documentation/auditoria-estado-2026-08-09.md` | **ARCHIVE** | Superada técnicamente por la del día 10; conserva el único registro del riesgo de copyright de `95c250a` cuando aún era reversible | Se pierde ese registro histórico si se borra en vez de archivarse |
| `documentation/entrevista-definicion-tpip.md` | **KEEP**, con nota | Vigente como documento de producto; un punto (TNMM vs. CUP) desactualizado y ya señalado en otro sitio | — |
| `documentation/patron-wiki-llm-karpathy.md` | **KEEP** | Nota técnica atemporal, no describe estado | — |
| `documentation/plan-limpieza-corpus.md` | **DO NOT TOUCH** | Traza probatoria del expurgo de `95c250a`; su paso 8 (purga de rama) sigue pendiente — activo mientras esa decisión (bloqueante C.2) no se tome | Perder la justificación documentada de por qué el `.gitignore` tiene el bloque que tiene |
| `documentation/revision-arquitectura-154dd0b.md` | **ARCHIVE** | Los 5 bloqueantes que describe ya están resueltos, verificado en su momento | — |
| `documentation/spec-modelo-datos-fase1.md` | **ARCHIVE** | Especificación ya implementada casi literalmente | — |
| `documentation/tax-research/**` (9 fichas) | **KEEP**, con nota | Vigente y citada desde código real; sigue sin frontmatter YAML (§B) | — |
| `TPIP.bat` | **DO NOT TOUCH** | Gitignorado, no versionado, lanzador local con ruta absoluta de esta máquina | Ninguno — no afecta al repo |
| `TPIP.bat.txt` | **REMOVE** | Duplicado byte a byte de `TPIP.bat`, también gitignorado y sin versionar — eliminarlo no tiene impacto en git ni en el repo público | Ninguno real — es higiene local pura |
| `Catalogo_Herramientas_IA_Daru.md` | **DO NOT TOUCH** | Correctamente gitignorado; expone superficie de entorno personal, exclusión ya aplicada y correcta | Exponer info personal si se sacara del `.gitignore` |
| `requirements.txt` — línea `pytest-asyncio` | **REMOVE candidate** (línea, no fichero) | Declarada, sin ningún uso (`asyncio`/`async def` no aparece en `tests/` ni `ai/`, reconfirmado ahora) | Ninguno — no hay tests async que dependan de ella |
| `tp_domain/calculations/arm_length_range.py::load_comparables` | **REMOVE candidate** | Sin ningún punto de llamada fuera de su propio módulo, reconfirmado ahora por grep exhaustivo | Bajo — verificar una vez más con grep antes de borrar, por si algún script externo al repo lo importa |
| `tp_domain/calculations/arm_length_range.py::calculate_defensibility_score` | **REMOVE candidate** | Wrapper sin llamadas; la lógica real ya se usa inline en `statistical_rules.assess()`, reconfirmado ahora | Igual que el anterior |
| `api/` (`__init__.py` de 0 bytes) | **DO NOT TOUCH** | Placeholder deliberado de fase futura, documentado en tres sitios distintos | — |
| `tp_domain/knowledge/Cerebros_Fiscales.pre-migracion/` (194MB) | **DO NOT TOUCH por ahora** | Es la red de seguridad de una migración que se ejecutó hace horas, con una segunda pasada de correcciones aprobada aún más reciente — prematuro decidir su destino ya | Perder la posibilidad de comparar/revertir si algo de la neutralización resultara incorrecto |
| Rama `backup/pre-limpieza-corpus` | **DO NOT TOUCH por ahora** | Ya señalado como bloqueante C.2 — decisión pendiente, no ejecutar sin tu confirmación explícita | Perder la red de seguridad del expurgo de `95c250a` si se purga antes de estar seguros |
| `__pycache__/`, `.pytest_cache/`, `tpip.egg-info/`, `.venv/`, `.agents/`, `.claude/` | **DO NOT TOUCH** | Correctamente gitignorados, artefactos locales normales, no requieren acción | — |
| `ai/`, `infrastructure/`, `tp_domain/` (código), `ui/app.py`, `tests/` | **KEEP** | Coherentes entre sí, 172/172 tests en verde, sin código muerto adicional al ya señalado | — |

### Recomendación concreta de qué limpiar primero

Solo dos acciones tienen riesgo verdaderamente nulo y beneficio inmediato — empezaría por ahí, y nada más, hasta que decidas los bloqueantes de §C:

1. **Borrar `TPIP.bat.txt`** (duplicado exacto, gitignorado, sin impacto en git).
2. **Quitar `pytest-asyncio` de `requirements.txt`/`pyproject.toml`** (dependencia declarada sin ningún uso).

Todo lo demás de esta tabla depende de una decisión tuya (los `ARCHIVE` de documentación, los dos `REMOVE candidate` de código muerto, y sobre todo los tres `DO NOT TOUCH por ahora` que son, en realidad, los bloqueantes C.1 y C.2 disfrazados de fila de tabla). No he tocado nada.
