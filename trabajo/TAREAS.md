\# TAREA ACTIVA — AUDITORÍA Y PROPUESTA DE LIMPIEZA

\#\# REGLA DE ROUTING

Quiero que trabajemos en este proyecto usando exclusivamente el gateway Free Claude Code/FCC configurado por el wrapper \`claude\`.

No uses Anthropic directamente.  
No uses mi OAuth de claude.ai.  
No investigues el routing.  
No modifiques ninguna configuración de routing.

\---

\#\# OBJETIVO

Antes de modificar cualquier cosa, haz una auditoría completa del estado actual del proyecto y prepara una propuesta de limpieza.

\#\#\# REGLA ABSOLUTA

NO BORRES, RENOMBRES NI MODIFIQUES NADA TODAVÍA.

Esta tarea es exclusivamente de:

1\. lectura;  
2\. auditoría;  
3\. clasificación;  
4\. propuesta.

No ejecutes ninguna acción destructiva ni ninguna modificación del repositorio.

\---

\# 1\. AUDITORÍA COMPLETA DEL REPOSITORIO

Revisa el repositorio completo y determina:

\- qué está terminado;  
\- qué queda pendiente;  
\- qué documentación está vigente;  
\- qué documentación está obsoleta;  
\- qué documentación está duplicada;  
\- qué código parece muerto;  
\- qué archivos o carpetas son temporales;  
\- qué backups existen;  
\- qué ramas Git existen y para qué sirven;  
\- qué ramas pueden eliminarse eventualmente;  
\- qué copias del corpus existen;  
\- qué elementos pueden eliminarse;  
\- qué elementos deberían archivarse;  
\- qué elementos deben conservarse por trazabilidad jurídica;  
\- qué elementos son críticos para el funcionamiento del sistema.

No te limites a buscar nombres sospechosos: lee el contexto suficiente para determinar realmente si cada elemento sigue teniendo utilidad.

\---

\# 2\. ZONAS A REVISAR ESPECIALMENTE

Revisa como mínimo:

\- \`documentation/\`  
\- \`tp\_domain/\`  
\- \`ai/\`  
\- \`tests/\`  
\- configuración del proyecto;  
\- scripts;  
\- archivos raíz;  
\- Git;  
\- ramas locales;  
\- ramas remotas si son visibles;  
\- \`.gitignore\`;  
\- backups;  
\- corpus y referencias al corpus;  
\- documentación de arquitectura;  
\- documentación de Fase 0;  
\- documentación de Fase 1\.

También revisa cualquier otra carpeta que pueda contener código, documentación, datos, artefactos temporales o duplicados.

\---

\# 3\. CONTRASTE CON FASE 0 Y FASE 1

Contrasta el estado real del repositorio con:

\- \`documentation/informe-fase0-council-arquitectura-juridica-2026-08-10.md\`  
\- \`documentation/auditoria-capa-juridica-2026-08-10.md\`  
\- \`documentation/fase1-clasificacion-corpus-sesgo-territorial-2026-08-10.md\`  
\- \`documentation/fase1-rewrite-propuesto-8-fichas-2026-08-10.md\`

Determina:

\- qué decisiones de Fase 0 ya se ejecutaron;  
\- cuáles siguen pendientes;  
\- qué decisiones cambiaron durante Fase 1;  
\- qué documentación refleja correctamente el estado actual;  
\- qué documentación quedó desactualizada;  
\- si existe alguna contradicción entre documentación y código real.

IMPORTANTE:

No asumas que la documentación es correcta simplemente porque existe.

El estado real del repositorio tiene prioridad.

\---

\# 4\. CORPUS CEREBROS\_FISCALES

Investiga el estado actual de todas las copias del corpus.

Determina:

\- dónde existe actualmente;  
\- cuál es la copia canónica;  
\- si existen copias congeladas;  
\- si existen backups;  
\- si existen duplicados;  
\- si existen referencias funcionales desde el código;  
\- si alguna copia puede eliminarse;  
\- si alguna debe conservarse temporalmente por seguridad;  
\- qué relación tiene cada copia con Git;  
\- qué relación tiene con los otros proyectos.

NO BORRES NI RENOMBRES NINGUNA COPIA.

Solo documenta qué debería hacerse posteriormente.

\---

\# 5\. GIT

Audita:

\- \`git status\`;  
\- ramas locales;  
\- ramas remotas visibles;  
\- commits relevantes;  
\- backups;  
\- ramas de limpieza;  
\- posibles commits históricos con material que ya no debería estar;  
\- si existen ramas que son únicamente una red de seguridad;  
\- si alguna rama debería conservarse;  
\- si alguna rama podría purgarse después de aprobación.

Presta especial atención a:

\`backup/pre-limpieza-corpus\`

y al commit:

\`95c250a\`

No elimines ni modifiques nada.

\---

\# 6\. CLASIFICACIÓN

Cada candidato a actuación debe clasificarse exactamente en una de estas categorías:

\#\#\# KEEP  
Debe mantenerse.

\#\#\# RENAME  
Tiene utilidad, pero el nombre o ubicación debería cambiarse.

\#\#\# ARCHIVE  
No debería formar parte del flujo activo, pero conviene conservarlo por historial, trazabilidad o seguridad.

\#\#\# REMOVE  
No aporta valor y puede eliminarse después de aprobación.

\#\#\# DO NOT TOUCH  
Debe permanecer exactamente como está por razones técnicas, jurídicas, históricas o de seguridad.

Para cada elemento clasificado, explica brevemente:

\- qué es;  
\- dónde está;  
\- para qué sirve;  
\- por qué recibe esa clasificación;  
\- qué riesgo existe si se elimina;  
\- qué acción propones posteriormente.

\---

\# 7\. NO HACER INFERENCIAS SIN VERIFICAR

Si algo parece innecesario pero no puedes demostrarlo, clasifícalo provisionalmente como:

\`DO NOT TOUCH\`

y explica qué habría que verificar antes.

No borres algo simplemente porque:

\- parece viejo;  
\- tiene un nombre extraño;  
\- parece duplicado;  
\- no se importa actualmente;  
\- parece relacionado con un proyecto anterior.

Primero verifica sus referencias y contexto.

\---

\# 8\. RESULTADO FINAL

Al terminar, NO MODIFIQUES NADA.

Entrega un informe estructurado con:

\#\# A. Estado general del proyecto

Resumen de cómo está actualmente.

\#\# B. Trabajo terminado

Lista de lo que ya está correctamente cerrado.

\#\# C. Trabajo pendiente

Lista priorizada.

\#\# D. Documentación

KEEP / RENAME / ARCHIVE / REMOVE / DO NOT TOUCH.

\#\# E. Código

KEEP / RENAME / ARCHIVE / REMOVE / DO NOT TOUCH.

\#\# F. Corpus

Situación de todas las copias.

\#\# G. Git y backups

Situación de ramas, commits y backups.

\#\# H. Limpieza propuesta

Lista concreta de acciones futuras.

\#\# I. Riesgos

Qué podría romperse o perderse con cada acción.

\#\# J. Plan recomendado

Orden óptimo de ejecución de la limpieza.

\---

\# 9\. REGLA FINAL

NO EJECUTES NINGUNA LIMPIEZA.

NO BORRES NADA.

NO RENOMBRES NADA.

NO MUEVAS NADA.

NO MODIFIQUES CÓDIGO.

NO MODIFIQUES DOCUMENTACIÓN.

NO HAGAS COMMITS.

NO HAGAS PUSH.

Solo audita, clasifica y propone.

Cuando termines, quiero una lista concreta de acciones para que el usuario pueda aprobarlas una por una.  
