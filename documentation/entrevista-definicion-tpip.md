# Entrevista de definición — TPIP (Transfer Pricing Intelligence Platform)

Fecha: 2026-08-09

Documento de referencia con las decisiones de alcance y producto tomadas antes de empezar a construir. Sustituye a las asunciones implícitas del documento de instrucciones del proyecto allí donde este las deja abiertas.

---

## 1. Identidad

**Nombre completo:** Transfer Pricing Intelligence Platform (TPIP).

**Idea central:** herramienta profesional que ayuda a analistas de precios de transferencia a evaluar si un transfer price es defendible bajo el principio de plena competencia (arm's length), comparando transacciones contra datos de referencia y generando informes profesionales.

**Objetivo del proyecto:** portfolio profesional — demuestra conocimiento de fiscalidad internacional, capacidad de convertir un problema fiscal en software, uso responsable de IA en un producto profesional, y visión de producto tax-tech. No es un trabajo académico ni un TFG.

---

## 2. Alcance del MVP (Fase 1)

| Eje | Decisión MVP | Fuera de alcance (por ahora) |
|---|---|---|
| Jurisdicciones | España (detalle normativo real: LIS, RD documentación TP) + resto UE con reglas simplificadas basadas en marco OCDE común | Multijurisdicción completa fuera de UE |
| Métodos TP | Solo TNMM | CUP, cost plus, resale price, profit split |
| Transacciones | Servicios intragrupo + Intangibles/cánones | Distribución, préstamos intragrupo (motor económico distinto — rating crediticio, curva de tipos) |
| Explícitamente excluido del MVP | Conexión a bases comerciales de pago (Orbis, Bloomberg, Amadeus), automatización completa de selección de comparables (sigue siendo asistida, no autónoma — regla de gobernanza IA ya fijada en las instrucciones del proyecto), presentación ante Hacienda, integraciones empresariales, chatbot fiscal general | — |

**Visión a futuro (no MVP, pero destino declarado):** multijurisdicción completa, todos los métodos OCDE, y las cuatro categorías de transacción incluyendo préstamos intragrupo. La arquitectura modular (`tp_domain/calculations/` separado por método, jurisdicción como parámetro y no hardcodeada) está pensada para escalar hacia ahí sin reescritura, apoyándose en que las capacidades actuales de IA permiten construir estos motores y el research companion con mucha más velocidad que hace unos años. El orden es: validar el MVP acotado y el patrón de trabajo primero, escalar alcance después — no al revés.

---

## 3. Usuario

**Durante el desarrollo:** solo Daru. No hay beta testers ni fiscalistas externos en esta fase.

**Objetivo de la demo final:** que un recruiter de Big Four / tax-tech piense las tres cosas a la vez — que Daru sabe fiscalidad internacional, que sabe construir producto tax-tech, y que esto podría evolucionar hacia un producto real.

---

## 4. Reparto de tareas Daru / Claude

Confirmado sin cambios:

- **Daru mantiene:** validación fiscal, decisiones de producto, criterio de utilidad profesional, revisión final de outputs importantes, decisión sobre qué entra en el portfolio.
- **Claude ejecuta:** arquitectura técnica, código, refactorización, documentación técnica, testing, propuestas alternativas, investigación técnica.

---

## 5. Fuentes y conocimiento

**Ubicación actual del conocimiento fiscal:** carpetas locales / documentos propios (no Zotero, no Obsidian, no otro Proyecto Claude separado, según lo confirmado).

**Relación con TPIP:** mezcla — TPIP puede reutilizar conocimiento fiscal general ya verificado, pero la documentación propia del producto (specs, prompts, arquitectura) se mantiene separada. Evita duplicar fuentes y mantiene el límite de responsabilidad entre proyectos.

---

## 6. Calendario

- **MVP funcionando:** 4 semanas desde el 2026-08-09 (objetivo ~2026-09-06), coincidiendo con el "Month 1" ya marcado en el roadmap del proyecto.
- **Tiempo semanal:** 20 h/semana (ritmo intensivo — deja margen para adelantar hacia Fase 2 dentro del primer mes si el MVP va bien).

---

## 7. Restricciones prácticas

- **Presupuesto:** algún gasto asumible (APIs de pago puntuales, algún dataset) si aporta valor claro a la demo — no gasto ilimitado.
- **Entorno de desarrollo:** principalmente Claude cloud (Cowork).
- **Disciplina de tokens/contexto:** se mantiene — prompts cortos pero completos, documentos de contexto separados, sin redundancia, tareas grandes divididas, subagentes cuando convenga.

---

## 8. Criterio de éxito

Criterio funcional (ya en las instrucciones del proyecto): *"un analista de transfer pricing puede usarlo para evaluar rápidamente una transacción."*

Criterio personal de portfolio (Daru, 2026-08-09):

> "Este chaval tiene huevos y cabeza — otros en su lugar se pasarían el verano en la playa."

---

## 8bis. Estrategia IA TPIP v1 — decisiones de diseño

**A) Qué ve primero el usuario:** dashboard profesional ("Analiza una transacción"), no un caso completo precargado. Trade-off aceptado: un dashboard vacío no cuenta nada por sí solo en una demo corta, así que debe incluir un caso de ejemplo accesible en un clic para no perder al espectador en los primeros segundos.

**B) Caso de demostración inicial ("Apple keynote" de TPIP):** el ya definido en las instrucciones del proyecto — empresa española paga un canon (royalty) del 12% a su matriz/filial en Luxemburgo por uso de tecnología, sector Software. TNMM indica que el margen está fuera del rango de comparables (benchmark 5%-8%), TPIP genera clasificación de riesgo y recomendación de documentación adicional. No se ha definido otro caso porque este ya es coherente con el alcance de MVP (España+UE, TNMM, intangibles) y no requiere inventar nada nuevo.

**C) Nivel de realismo de los datos:** sintéticos pero realistas para el MVP (rangos y márgenes plausibles por sector, con supuestos documentados — como ya piden las instrucciones del proyecto). Casos públicos reales o datos anclados a ellos quedan para fases posteriores, en la misma lógica que la ambición de multijurisdicción y métodos completos: escalar realismo después de validar el motor y el patrón de trabajo, no antes.

**D) Stack técnico:** ya implementado en el repo, con una desviación respecto a las instrucciones originales del proyecto que queda registrada aquí: Streamlit en lugar de React/TypeScript/Tailwind para el frontend. Resto según lo previsto — FastAPI, SQLAlchemy/SQLite, Anthropic API para la parte IA. Decisión vigente salvo que Daru diga lo contrario.

**E) Repositorio:** público en GitHub desde ya (`github.com/danirubio2323-commits/transfer-pricing-intelligence-platform`), visible durante todo el desarrollo — no se espera al MVP presentable para abrirlo.

---

## 9. Pendiente de definir

- Punto 3 del bloque 2 original (qué problema concreto resuelve TPIP frente a lo que existe hoy) sigue sin una respuesta explícita — no derivable de lo ya decidido, a revisar antes de escribir los prompts de la Fase 1 si se necesita justificar el "por qué ahora" del proyecto en la demo.
