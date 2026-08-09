# UE — Directiva Intereses-Cánones 2003/49/CE

**Origen:** `Cerebros_Fiscales/wiki/matriz/ue-directiva-intereses-canones-2003-49-ce.md`
**Tipo:** Normativa UE vigente
**Usar en:** Tax Impact Modeler (Fase 2), cálculo de retención en fuente

## Regla central

Los pagos de intereses o cánones que surjan en un Estado miembro quedan **exentos de cualquier impuesto** en ese Estado (por retención en origen o por liquidación), siempre que el beneficiario efectivo sea una sociedad de otro EM, o un EP situado en otro EM de una sociedad de un EM.

## Condiciones y plazos parametrizables

| Elemento | Valor |
|---|---|
| Periodo mínimo de tenencia exigible | 2 años ininterrumpidos (opcional para el EM) |
| Plazo de resolución sobre la exención | Máximo 3 meses desde la atestación |
| Requisito documental | Certificación acreditativa; sin ella, el Estado de la fuente puede exigir retención |

## Por qué es la pieza que falta para la Fase 2

El caso de referencia del roadmap es España → Luxemburgo, royalty de 1 M€ al 12%. Hoy TPIP dice si el 12% es defendible. No dice cuánto se paga.

Esta Directiva es la que determina si hay retención en fuente en el corredor intra-UE. Con ella más los CDI bilaterales se puede calcular el coste fiscal real y comparar escenarios: "si el royalty baja del 12% al 8%, ¿qué pasa con la base imponible en España y con la retención?".

## Aplicación en TPIP

- `tp_domain/calculations/withholding.py` (Fase 2)
- Precedencia: Directiva (exención intra-UE si se cumplen requisitos) → CDI bilateral → normativa interna
- El comparador de escenarios del roadmap Fase 2 depende de esto

## Enlaces en el corpus original

`[[matriz/ue-directiva-matriz-filial]]`, `[[matriz/boe-cdi-espana-luxemburgo-1986]]`
