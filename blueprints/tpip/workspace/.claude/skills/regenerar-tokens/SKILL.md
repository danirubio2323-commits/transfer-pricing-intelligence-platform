---
name: regenerar-tokens
description: Regenerar el CSS de tokens tras tocar la paleta — "he cambiado un color", "quiero otro azul", "tokens desincronizados", "build_tokens --check sale en rojo", "el fondo de las tarjetas". Recuerda que la paleta se edita en infrastructure/theme.py y nunca en tokens.css, y que el script se invoca con -m.
---

# Regenerar los tokens de diseño

## Cuándo usarla

- «He cambiado un color», «quiero otro azul para el foco», «el gris de las tarjetas se ve mal».
- `uv run python -m scripts.build_tokens --check` sale con **1**.
- Cualquier edición de `infrastructure/theme.py` o de `static/css/app.css`.

## Por qué existe

Pantalla e informe son dos renderizadores del mismo análisis. La paleta vive **una sola vez**, en
`infrastructure/theme.py`, y `static/css/tokens.css` se genera desde ahí. Editar el CSS directamente
crea una segunda paleta que diverge en silencio, que es el problema que este mecanismo existe para
impedir.

## Pasos

1. **Edita `infrastructure/theme.py`**, nunca `tokens.css`. Y **añade claves, no renombres**:
   renombrar `surface` rompe `infrastructure/report/pdf_report.py` y las 38 pruebas de informe.
2. **Comprueba el contraste antes de fijar un hex.** WCAG 2.2 AA: 4,5:1 para texto normal, 3:1 para
   límites de componente. Los tres pares con menos margen hoy son `muted` sobre `surface` (6,49:1),
   `warn` sobre blanco (4,90:1 — cualquier aclarado lo rompe) y `border-strong` sobre blanco (4,54:1).
3. **Regenera:** `uv run python manage.py`… no. El comando es
   `uv run python -m scripts.build_tokens`. **Con `-m`, siempre.** La forma directa
   (`python scripts/build_tokens.py`) pone `scripts/` en `sys.path[0]` y no encuentra `infrastructure`.
   Si alguien "simplifica" el `-m`, esto deja de funcionar con un error de importación que parece un
   problema de instalación y no lo es.
4. **Comprueba la sincronía:** `--check` debe salir 0.
5. **Versiona `tokens.css`.** Está generado, pero se versiona: el CSS tiene que funcionar sin ejecutar
   nada.

## Verify

```powershell
uv run python -m scripts.build_tokens; if ($LASTEXITCODE -ne 0) { throw 'la generacion falla' }
uv run python -m scripts.build_tokens --check; if ($LASTEXITCODE -ne 0) { throw "tokens.css desincronizado (codigo $LASTEXITCODE)" }
uv run pytest tests/web/test_theme_tokens.py -q; if ($LASTEXITCODE -ne 0) { throw 'las pruebas de tokens fallan' }
$literales = Select-String -Path 'static/css/app.css' -Pattern '#[0-9A-Fa-f]{3,6}\b' -ErrorAction SilentlyContinue; if ($literales) { throw 'app.css contiene colores literales' }
uv run pytest tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'la paleta ha roto el informe' }
```

## No hagas

- **No edites `static/css/tokens.css` a mano.** El siguiente `--check` lo delata, y si nadie lo
  ejecuta, pantalla e informe divergen en silencio.
- **No escribas un color literal en `app.css`.** Todo sale de `var(--tpip-*)`.
- **No renombres una clave de `COLORS`.** Añade.
- **No quites el `-m`.**
- **No añadas una prueba de tokens a `tests/report/`**: cambiaría el recuento de 180. Va en
  `tests/web/test_theme_tokens.py`.
