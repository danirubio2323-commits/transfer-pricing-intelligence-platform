# Investigación fiscal — índice

Fichas de análisis fiscal propio que sirven de **fuente a las reglas ejecutables** de TPIP.

Regla de separación:

- **Esta carpeta** contiene el criterio fiscal: qué dice la norma, de dónde sale, qué implica.
- **`tp_domain/rules/` y `tp_domain/calculations/`** contienen el código que implementa ese criterio.
- La ficha nunca vive dentro de `tp_domain/`; el módulo cita la ficha en su docstring.

Ninguna de estas fichas reproduce material de terceros. Son análisis propio con cita a fuente primaria. El corpus documental completo (PDFs de fuentes oficiales, doctrina y publicaciones OCDE) vive fuera de este repositorio, en el proyecto `Cerebros_Fiscales`.

---

## Mapa ficha → código

| Ficha | Destino en código | Fase | Qué aporta |
|---|---|---|---|
| `jurisdictions/spain/art18-lis-operaciones-vinculadas.md` | `tp_domain/rules/spanish_rules.py` | 2A | Perímetro de vinculación 25%, umbral 45 M€, régimen sancionador (1.000/10.000 €, 15%, límite 10%/1% INCN). **La regla española es la ausencia de regla estadística** |
| `jurisdictions/germany/astg-rango-intercuartilico-ajuste-mediana.md` | `tp_domain/rules/german_rules.py` | 2A | Rango intercuartílico obligatorio y ajuste automático a la mediana (§1.3a AStG). Es una rama de cálculo, no una constante |
| `jurisdictions/spain/ris-documentacion-masterfile-localfile.md` | Generación de informes + `defensibility_score` | 2A/2B | Masterfile/Local file, umbrales 45 M€ y 750 M€, qué es "dato" y qué "conjunto de datos" a efectos de sanción |
| `frameworks/safe-harbours-y-htvi.md` | `tp_domain/rules/safe_harbours.py` | 2B | Margen fijo del 5% en servicios de bajo valor añadido (evita el benchmark); umbrales HTVI del 20% y 5 años |
| `jurisdictions/eu/directiva-intereses-canones-2003-49.md` | `tp_domain/calculations/withholding.py` | 2 | Exención de retención en fuente intra-UE y sus condiciones. Pieza base del Tax Impact Modeler |
| `frameworks/ocde-directrices-2022-marcos-riesgo-dempe-servicios.md` | `tp_domain/rules/comparable_selection.py` + cuestionario UI | 2B | Marco de riesgo en 6 pasos (cap. I), DEMPE (cap. VI), *benefits test* (cap. VII). Especifica cuestionario, no constantes |
| `frameworks/criterios-seleccion-comparables.md` | `tp_domain/calculations/comparable_scoring.py` | 2B | Taxonomía de criterios de comparabilidad frente a los dos que aplica hoy el motor (industria + ventana temporal) |
| `processes/doctrina-teac-bilateralidad-y-servicios.md` | Factores de riesgo cualitativos + informe | 2A | Criterio administrativo español. Solo RG 7833/2023 tiene eficacia vinculante general — la distinción importa |
| `jurisdictions/eu/propuesta-directiva-tp-2023-retirada.md` | **Ninguno — guardarraíl negativo** | — | COM(2023) 529, retirada el 21 oct 2025. Documenta una regla que **no** debe implementarse como vigente |

---

## Convención de trazabilidad

Cada módulo de `tp_domain/rules/` debe abrir con la referencia a su ficha y a la fuente primaria:

```python
"""
Reglas de la jurisdicción española.

Fuente del criterio: documentation/tax-research/jurisdictions/spain/art18-lis-operaciones-vinculadas.md
Fuente primaria:     Ley 27/2014 (LIS), Art. 18
Verificado contra:   BOE-A-2014-12328
"""
```

Motivo: un informe generado por TPIP debe poder remitir cada conclusión a su base legal. Si la cadena módulo → ficha → norma se rompe, el informe deja de ser defendible.
