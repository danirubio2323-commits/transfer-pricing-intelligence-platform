# Criterios de selección de comparables

**Origen:** síntesis de `sub_tp/ocde-directrices-precios-transferencia-2022.md`, `matriz/de-astg-transparencia-precios.md`, `sub_is/ris-rd634-2015-reglamento-impuesto-sociedades.md`
**Tipo:** taxonomía derivada, no ficha directa del corpus
**Usar en:** `tp_domain/calculations/comparable_scoring.py` (Fase 2B)

## Estado actual de TPIP

El motor filtra hoy por **dos criterios**:

1. Coincidencia exacta de industria
2. Ventana temporal: `data_year >= effective_date.year - 2`

Eso es lo mínimo defendible. No es lo que exige la normativa.

## Lo que la normativa exige además

### Análisis funcional (Alemania, §1.3 AStG; OCDE Cap. I)

*Funktions- und Risikoanalyse*: funciones ejercidas, riesgos asumidos, activos empleados. Es requisito previo a la comparabilidad, no un refinamiento opcional.

### Análisis de comparabilidad detallado (España, Art. 16 RIS)

El Local file debe contener análisis de comparabilidad detallado con remisión al Art. 17 RIS, más justificación razonada del método elegido.

### Ajustes de comparabilidad (Alemania, §1.3a AStG)

La regla del rango intercuartílico **se activa precisamente cuando persisten diferencias de comparabilidad tras los ajustes**. Es decir: el rango estrechado no es el caso general, es el remedio cuando los comparables no son perfectos.

Implicación para TPIP: aplicar siempre P25-P75 sin evaluar comparabilidad es asumir implícitamente que los comparables son imperfectos. Correcto por prudencia, pero conviene decirlo.

## Jerarquía de criterios propuesta

| Nivel | Criterio | Estado en TPIP |
|---|---|---|
| 1 | Industria | ✅ Implementado (obligatorio) |
| 2 | Ventana temporal | ✅ Implementado (2 años) |
| 3 | Perfil funcional (funciones/riesgos/activos) | ❌ Requiere ampliar `Comparable` |
| 4 | Mercado geográfico | ❌ El campo `country` existe, no se usa para filtrar |
| 5 | Tamaño / cifra de negocios | ❌ Campo inexistente |
| 6 | Independencia (no vinculadas entre sí) | ❌ Campo inexistente |

## Puertas de calidad de datos

Reglas que un comparable debería pasar antes de entrar en el rango:

- Dato del ejercicio dentro de la ventana temporal
- Métrica relevante no nula para el tipo de transacción (hoy sí se comprueba para `royalty_rate`)
- Muestra mínima: TPIP ya avisa por debajo de 5 comparables. No hay estándar legal de número mínimo en el Art. 18 LIS

## Qué haría falta en el modelo de datos

Ampliar `Comparable` con: `functions` (lista), `risks_assumed` (lista), `assets_employed` (lista), `turnover_eur`, `is_independent` (bool).

Y ampliar `Transaction` con el perfil funcional de la parte testada, para poder cruzar.

Esto es Fase 2B. Antes hay que decidir si el dataset sintético se amplía con esos campos o si el filtro funcional se hace por cuestionario en la UI.

## Riesgo abierto a documentar

La ventana temporal usa `effective_date.year - 2`. Con `datetime.now()` por defecto en la UI, el dataset (2024/2025) empezará a degradarse en 2027 y quedará vacío en 2028. Los tests fijan fecha 2026, así que **no saltarán**. Conviene un aviso en la UI o revisar el dataset periódicamente.
