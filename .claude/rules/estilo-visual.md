---
description: Lenguaje visual — paleta, tokens generados, tipografía y accesibilidad. Léelas antes de tocar static/ o cualquier plantilla.
paths:
  - "static/**"
  - "templates/**"
---

# Estilo visual

## La regla que existe para impedir la deriva

Pantalla e informe son **dos renderizadores del mismo análisis**, y en cuanto divergen dejan de parecer
el mismo producto. Por eso hay una sola fuente de verdad:

- **La paleta vive en `infrastructure/theme.py`**, en hexadecimal, junto a las etiquetas humanas de
  cada enum y la geometría normalizada del rango.
- **`static/css/tokens.css` es GENERADO** desde ahí con `uv run python -m scripts.build_tokens`. Se
  versiona, para que el CSS funcione sin ejecutar nada, pero **nunca se edita a mano**.
- **`static/css/app.css` no contiene ni un color literal.** Todo sale de `var(--tpip-*)`. Hay una
  comprobación que busca `#` seguido de tres o seis dígitos hexadecimales y falla si encuentra alguno.
- El gate `uv run python -m scripts.build_tokens --check` sale **0** si están sincronizados y **1** si
  no. Si lo ves en rojo: has editado `tokens.css` en vez de `theme.py`.

**La paleta se amplía añadiendo claves, jamás renombrando.** Renombrar `surface` rompe
`infrastructure/report/pdf_report.py` y las 38 pruebas de informe, y con ellas la invariante de 180.

## Los tokens

| Token | Valor | Uso |
|---|---|---|
| `--tpip-ink` | `#1A1A1A` | Texto principal |
| `--tpip-muted` | `#5A5A5A` | Texto secundario |
| `--tpip-rule` | `#C8C8C8` | Separadores |
| `--tpip-background` | `#FFFFFF` | Fondo de página |
| `--tpip-surface` | `#F7F8FA` | Tarjetas y paneles |
| `--tpip-surface-sunken` | `#EBEEF3` | Cabeceras de tabla |
| `--tpip-border-strong` | `#767676` | Borde de inputs y selects |
| `--tpip-focus` | `#1F4E79` | Anillo de foco y enlaces |
| `--tpip-band-outer` | `#DCE3EC` | Banda P10–P90, **relleno decorativo** |
| `--tpip-band-inner` | `#9FB3C8` | Banda intercuartílica, **relleno decorativo** |
| `--tpip-median` | `#334E68` | Mediana y tipo analizado |
| `--tpip-ok` | `#2E6B4F` | Defendible |
| `--tpip-warn` | `#8A6D1F` | Moderado |
| `--tpip-risk` | `#8C2F2F` | Riesgo alto, errores |

**Las dos bandas son relleno decorativo, nunca límite de componente ni fondo de texto.** `#9FB3C8`
sobre blanco da 2,15:1 y no alcanzaría el 3:1 que exige un límite.

**Contraste, ya medido.** Los tres pares con menos margen: `muted` sobre `surface` **6,49:1**; `warn`
sobre blanco **4,90:1** —cualquier aclarado lo rompe—; `border-strong` sobre blanco **4,54:1**.

## Estética

Sobria a propósito: gris tinta sobre blanco, superficies apenas tintadas, filetes finos y tres acentos
desaturados reservados al veredicto. **El color solo aparece donde comunica algo** —el nivel de
defendibilidad, la severidad de un riesgo, la banda del rango—; nunca decora.

Si un componente nuevo necesita un color que no esté en la tabla, la respuesta casi siempre es que no
necesita color. La referencia es el informe PDF: si el componente no cabría en ese documento sin
desentonar, no pertenece a esta interfaz.

- **Sin fuentes web**: `-apple-system, "Segoe UI", Roboto, system-ui, sans-serif`.
- **Sin sombras**: las superficies se separan por color y por `1px solid var(--tpip-rule)`.
- **Sin modo oscuro**: el informe no lo tiene, y mantener dos paletas para parecerse a él en una sola
  es trabajo con signo negativo.
- Espaciado base 4px: 4, 8, 12, 16, 24, 32, 48, 64. Radio 4px en controles, 8px en tarjetas, 0 en
  tablas. Ancho máximo 72rem.

## Accesibilidad — no es acabado

- `:focus-visible` con anillo de `var(--tpip-focus)` de 2px y `outline-offset: 2px`.
- Objetivos de puntero de **24×24 px CSS** como mínimo.
- **Todo el movimiento va dentro de `@media (prefers-reduced-motion: no-preference)`**: la ausencia de
  movimiento es el estado por defecto y la animación es la excepción que se activa.
- Las tablas anchas se desplazan **dentro de su contenedor** con `overflow-x: auto`; nunca arrastran la
  página.
- El SVG del rango lleva `role="img"` y un `<title>` que dice **en palabras** dónde cae el tipo
  respecto del rango: ese equivalente textual **es** la información que el producto da.
- Los errores son **texto**, nunca solo color.
