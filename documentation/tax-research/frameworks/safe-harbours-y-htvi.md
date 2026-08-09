# Safe harbours y HTVI — las reglas numéricas de la OCDE

**Origen:** `Cerebros_Fiscales/wiki/sub_tp/ocde-vs-onu-divergencias-precios-transferencia.md`
**Fuente primaria:** OECD TPG 2022, Cap. VI D.4 y Cap. VII D; ONU, Manual Práctico 2013 (ST/ESA/347)
**Usar en:** `tp_domain/rules/safe_harbours.py` (Fase 2B)

Esta es la ficha con más reglas directamente codificables de todo el corpus.

## Servicios de bajo valor añadido — margen fijo del 5%

**OCDE (Cap. VII, párr. 7.43-7.65):** régimen simplificado y electivo.

- **Margen del 5% sobre costes relevantes** (párr. 7.61-7.62), idéntico para todas las categorías de servicios calificados, **sin necesidad de justificarlo mediante estudio de comparables**.
- **Retención en fuente (párr. 7.65):** la OCDE recomienda que, cuando una jurisdicción aplique retención sobre estos cargos, la limite **únicamente al elemento de margen** (el 5%), no al importe bruto.

Esto es implementable tal cual: si la transacción califica como servicio de bajo valor añadido, el motor puede devolver directamente el 5% sin pasar por el benchmark.

## Intangibles de difícil valoración (HTVI) — las 4 excepciones

**Mecanismo (Cap. VI, párr. 6.186-6.188):** la evidencia *ex post* constituye **evidencia presuntiva** sobre si la valoración *ex ante* fue razonable. Invierte la asimetría de información entre contribuyente y Administración.

**Cuatro excepciones tasadas (párr. 6.193)** que impiden aplicarlo:

1. El contribuyente aporta proyecciones ex ante detalladas y evidencia fiable de que la diferencia se debe a eventos imprevisibles o a la materialización de probabilidades ya contempladas.
2. La transferencia está cubierta por un **APA bilateral o multilateral vigente**.
3. **La diferencia entre proyección y resultado real no supera el 20%** de la compensación pactada.
4. **Han transcurrido 5 años** desde el primer ingreso comercial del intangible sin ajustes significativos.

Las excepciones 3 y 4 son umbrales numéricos: 20% y 5 años. Directamente parametrizables.

## OCDE vs ONU — dónde divergen de verdad

La divergencia **no está** en los métodos de valoración: ambos parten del mismo principio de plena competencia (Art. 9 MC-OCDE / MC-ONU).

Está en la **tolerancia a mecanismos administrables que se apartan del análisis funcional pleno** cuando la capacidad técnica o la disponibilidad de comparables es limitada:

| | OCDE (2013) | ONU (Manual 2013) |
|---|---|---|
| Safe harbours | Prefiere flexibilidad administrativa caso por caso | Sección propia (3.8) exponiendo ventajas para pymes y administraciones con pocos recursos |
| Tributación presuntiva | No desarrollada | Sección 3.7 propia, con Japón como caso práctico; invierte la carga de la prueba |
| Orientación | Estado de residencia | **Preserva más derechos al Estado de la fuente** (párr. 1.8.2) |

## ⚠️ Advertencia de alcance heredada del corpus

El ejemplar del Manual ONU en `raw/` es la **edición original de 2013**. Existen ediciones de 2017 y 2021 que no están en el corpus. El estándar HTVI de la OCDE es de 2015/2018, **posterior** a la edición ONU disponible: por eso "hard-to-value" no aparece ni una vez en el Manual ONU de este corpus.

En consecuencia, **no se puede afirmar que la ONU diverja de la OCDE en HTVI**. Solo que la edición disponible es anterior a que el estándar existiera. El corpus lo marca como hueco activo.

Si TPIP llegara a comparar OCDE vs ONU, esta limitación tiene que viajar con el dato.

## Aplicación en TPIP

- Safe harbour del 5%: rama de cálculo alternativa que evita el benchmark
- Umbrales HTVI (20%, 5 años): validadores para transacciones sobre intangibles
- La divergencia OCDE/ONU es relevante si TPIP se extiende a corredores con países en desarrollo
