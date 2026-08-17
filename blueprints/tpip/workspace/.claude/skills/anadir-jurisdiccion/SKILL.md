---
name: anadir-jurisdiccion
description: Añadir una jurisdicción nueva al motor de precios de transferencia — modelar un país, "añadir Francia", "modelar Italia", "esta operación es con Portugal y sale NOT_MODELLED". Impone el orden correcto: primero la ficha de investigación con fuente primaria verificada, después el registro de fuentes, y solo entonces el mapa de reglas. Úsala siempre antes de tocar JURISDICTION_RANGE_RULES.
---

# Añadir una jurisdicción

## Cuándo usarla

- «Quiero modelar Francia», «añade Italia», «¿por qué Portugal sale como no modelada?»
- Cualquier cambio a `JURISDICTION_RANGE_RULES` en `tp_domain/rules/statistical_rules.py`.
- Cualquier entrada nueva en el registro de `tp_domain/sources.py`.

## Por qué existe

El mapa de jurisdicciones **crece ficha a ficha, nunca por analogía**. Una jurisdicción no estudiada
devuelve `NOT_MODELLED`, y eso no es un hueco: es una respuesta. Suponer «sin regla estadística» para
un país que nadie ha leído sería asignarle la regla española, que es exactamente lo que un informe de
precios de transferencia no puede permitirse decir sin respaldo.

`NOT_MODELLED` es correcto hasta que exista la ficha. **Atajar el orden de abajo produce Derecho
comparado inventado con apariencia de cálculo.**

## Pasos

1. **Escribe la ficha de investigación primero**, en
   `documentation/tax-research/jurisdictions/<pais>/<tema>.md`, con el frontmatter completo que exige
   el indexador: `titulo`, `fecha_creacion`, `origen`, `fuente_primaria`, `tipo`, `usar_en`,
   `rango_normativo`, `clase`, `tipo_localizador`, `localizador`, `verificada_el` y
   `confianza_verificacion`.
   La jurisdicción **se deduce del directorio**, no del frontmatter: `jurisdictions/<pais>/`.
2. **Verifica contra el texto primario.** Si has leído la disposición oficial, marca
   `confianza_verificacion: primary_source_verified`. Si es una lectura dirigida y no exhaustiva,
   marca `directed_reading` — y dilo, no lo maquilles. Una fecha de verificación sola no debe leerse
   como más certeza de la que hubo.
3. **Reindexa y comprueba** que la ficha aparece: `uv run python manage.py reindexar_corpus`.
4. **Añade la fuente al registro cerrado** de `tp_domain/sources.py`, con el **mismo `id`** que usa la
   ficha, para que resuelvan sin tabla de traducción. Si su `locator_type` es `OFFLINE`, es obligatorio
   `quote` y `disclaimer`.
5. **Solo ahora**, añade el país a `JURISDICTION_RANGE_RULES` con su `RangeRule`, y sus fuentes a
   `_RULE_SOURCES`.
6. **Escribe la prueba de dominio que lo fija**, en `tests/domain/test_rules.py`. Y como la suite
   rescatada mantiene 180 pruebas, **si añades una aquí, retira una que haya quedado redundante** o
   consúltalo antes de romper la invariante.

## Verify

```powershell
uv run python manage.py reindexar_corpus; if ($LASTEXITCODE -ne 0) { throw 'el reindexado falla' }
uv run pytest tests/domain -q; if ($LASTEXITCODE -ne 0) { throw 'las reglas de dominio fallan' }
uv run pytest tests/domain tests/ai tests/report -q; if ($LASTEXITCODE -ne 0) { throw 'la red de seguridad se ha roto' }
```

## No hagas

- **No añadas un país a `JURISDICTION_RANGE_RULES` sin su ficha.** Es el atajo que esta skill existe
  para impedir.
- **No copies la regla de un país vecino.** España y Alemania difieren precisamente en esto, y esa
  asimetría es el producto.
- **No inventes un identificador de localizador.** Si no hay uno público resoluble, usa `OFFLINE` con
  su cita literal y su descargo.
- **No cambies el `id` de una fuente ya emitida.** Hay informes en PDF que la citan.
