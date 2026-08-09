# OCDE — Directrices de Precios de Transferencia 2022: los tres marcos

**Origen:** `Cerebros_Fiscales/wiki/sub_tp/ocde-directrices-precios-transferencia-2022.md`
**Fuente primaria:** OECD Transfer Pricing Guidelines 2022, Cap. I, VI y VII
**Alcance de la ficha original:** lectura dirigida a tres capítulos. Cap. II-V y VIII-X sin desarrollar.
**Usar en:** `tp_domain/rules/comparable_selection.py`, cuestionario de la UI (Fase 2B)

## Cap. I — Marco de 6 pasos sobre riesgo

Sustituye y detalla la doctrina *cash box* (párr. 1.71-1.103):

1. **Identificar los riesgos económicamente significativos** con especificidad. Cinco categorías no jerárquicas: estratégicos/de mercado, infraestructura/operacionales, financieros, transaccionales, y de peligro (*hazard*).
2. **Asunción contractual del riesgo.** El contrato escrito es el punto de partida, pero una asunción ex ante solo tiene valor probatorio si refleja un compromiso genuino anterior a la materialización. Una "asunción" ex post no es asunción.
3. **Análisis funcional respecto del riesgo.** Qué entidad ejerce control (capacidad + desempeño efectivo) y cuál tiene capacidad financiera.
4. **Interpretar los pasos 1-3.** Contrastar si la conducta es consistente con los términos contractuales.
5. **Asignación del riesgo.** Si quien asume contractualmente el riesgo no lo controla ni tiene capacidad financiera, **el riesgo se reasigna a quien sí ejerce el control efectivo**. Esta es la base técnica exacta de la doctrina *cash box*.
6. **Fijación del precio** remunerando tanto la asunción como la mitigación.

**Dato duro:** el control de un riesgo requiere simultáneamente capacidad de decisión **y** desempeño funcional efectivo. La autoridad formal sin ejercicio real no basta (párr. 1.65-1.66, 1.93).

## Cap. VI — DEMPE e intangibles

**Regla central (párr. 6.42):** "el propietario legal de un intangible, por sí solo, no confiere ningún derecho a retener en última instancia los retornos derivados de su explotación". El retorno depende de funciones desempeñadas, activos utilizados y riesgos asumidos.

**Marco de 6 pasos (párr. 6.34):** identificar intangibles y riesgos → identificar propiedad legal → identificar quién desempeña funciones, usa activos y gestiona riesgos → confirmar consistencia contrato/conducta → delinear la transacción real → determinar precios.

**"Funciones importantes" (párr. 6.56)**, lista no exhaustiva: diseño y control de programas de I+D y marketing; dirección y fijación de prioridades de investigación; control de decisiones estratégicas de desarrollo; gestión y control presupuestario; decisiones sobre defensa y protección del intangible; control de calidad continuo sobre funciones externalizadas.

Si el propietario legal **externaliza** la mayoría de estas funciones, atribuirle una porción material del retorno debe examinarse con especial cautela, y **la fiabilidad de un método unilateral se reduce sustancialmente** (párr. 6.57): suele requerirse profit split o valoración ex ante.

**Propiedad legal por defecto (párr. 6.40):** si no hay propietario legal identificable, se considera tal a quien controla de facto las decisiones de explotación y puede excluir a terceros del uso.

## Cap. VII — Servicios intragrupo

**Benefits test (párr. 7.5-7.6):** existe servicio intragrupo si la actividad proporciona valor económico o comercial que mejora o mantiene la posición de negocio del destinatario, evaluado según si una empresa independiente comparable habría pagado por ella o la habría realizado internamente. Si no, **no debe considerarse servicio intragrupo**. Es el test que el Art. 18.5 LIS traduce como "ventaja o utilidad".

**Shareholder activities (párr. 7.9-7.10), excluidas de cargo:** costes de la estructura jurídica de la matriz (juntas, emisión de acciones, cotización), consolidación contable en interés exclusivo de la matriz, relación con inversores, cumplimiento fiscal de la matriz. Distinto del *stewardship* más amplio (planificación, gestión de emergencias, asistencia en gestión diaria), que sí puede facturarse.

## Nota terminológica del corpus

El acrónimo "DEMPE" **no aparece ni una sola vez** en el texto de las Directrices (verificado por búsqueda exhaustiva). El original siempre usa la expresión desarrollada. Es terminología de práctica profesional, no de fuente primaria.

## Aplicación en TPIP

- El marco de 6 pasos sobre riesgo es un **árbol de decisión** implementable como cuestionario
- Las "funciones importantes" del párr. 6.56 son una **checklist** que alimenta la selección de método: si hay externalización material, degradar la recomendación de CUP hacia profit split
- El benefits test filtra si una transacción de tipo `management_fee` debe siquiera analizarse

## Enlaces en el corpus original

`[[sub_tp/beps-acciones-8-10-precios-transferencia]]`, `[[sub_tp/lis-art18-operaciones-vinculadas-precios-transferencia]]`, `[[sub_tp/teac-rg-7833-2023-servicios-intragrupo-doble-vinculacion]]`
