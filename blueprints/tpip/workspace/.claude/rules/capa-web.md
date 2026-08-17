---
description: Convenciones de la capa web — vistas, servicios, formularios, URLs y plantillas de Django. Léelas antes de tocar apps/, config/ o templates/.
paths:
  - "apps/**"
  - "config/**"
  - "templates/**"
---

# Capa web

## Autorización — lo que más caro sale equivocarse

- **Toda lectura de una fila con propietario pasa por `apps/comun/guardas.py`.** Ninguna vista escribe
  `Caso.objects` por su cuenta; todo listado sale de `apps/comun/consultas.py::casos_de()`, donde el
  propietario **no es un parámetro opcional**.
  Una comprobación duplicada en siete vistas es una que un día falta en la octava, y esa octava **no da
  error: devuelve los datos de otro**.
- **Un recurso ajeno responde 404, nunca 403.** Un 403 confirma que el identificador existe, y con eso
  se enumera la base de datos de otro usuario sin ver una sola fila. El 404 no distingue «no existe» de
  «no es tuyo», que es justo la propiedad que se quiere. El único 403 legítimo del proyecto es el del
  token CSRF.
- **La sesión se exige por omisión**, en `apps/comun/middleware.py`, con una lista blanca explícita.
  Olvidar un decorador dejaría una vista abierta; olvidar añadir una ruta a la lista blanca la deja
  cerrada. El fallo por omisión tiene que ser el seguro.

## Fronteras

| Fichero | Puede | Nunca debe |
|---|---|---|
| `apps/*/views.py` | Leer la petición, llamar a `services.py`, devolver respuesta | Importar `tp_domain.calculations` o `ai.claude_client` |
| `apps/analisis/services.py` | Motor, cuota, persistencia y capa de IA | Contener nada de HTTP |
| Plantillas | Mostrar | Calcular, o escribir una URL a mano |

## Códigos de estado

- **Un formulario inválido responde `422`**, no el `200` habitual de Django. Un estado distinto hace
  que «el formulario ha rechazado la entrada» sea comprobable por una máquina.
- `405` para un método no permitido: un `GET` a `/salir/` o a una ruta de borrado.
- `400` solo para una ruta de ficha que se sale del corpus. `404` para todo lo que no existe o no es
  del solicitante.
- El formulario reenviado tras un error **conserva todos los valores ya introducidos**.

## Persistencia

- **El borrado es suave**: se pone `deleted_at`. Ninguna vista llama a `.delete()` sobre un `Caso`.
- **Dar de baja una cuenta es `is_active = False`**, nunca un `DELETE`: las claves foráneas son
  `PROTECT` y un borrado real debe chocar.
- Todo lo que lea un `Caso` lo rehidrata con `AnalysisResult.model_validate(obj.payload)` y trabaja
  sobre el objeto de dominio. **Ninguna plantilla lee claves sueltas de `payload`.**
- `payload` es la fuente de verdad; `engine_version`, `dataset_version` y `has_ai_explanation` se
  derivan de él **al guardar**, nunca al revés.

## Plantillas

- `{% url %}` siempre. Ninguna URL escrita a mano.
- **Nada de `|safe` sobre datos de entrada.** Las dos únicas excepciones son contenido de confianza
  escrito por quien administra: el Markdown del corpus, que vive en el repositorio, y el de las
  unidades de estudio, redactado desde el panel por una cuenta `is_staff`.
- Los estados vacíos se escriben, no se dejan en blanco. Y en el listado son **dos distintos**: «aún no
  has analizado nada» frente a «ningún caso coincide» — un filtro mal escrito no debe parecer una base
  de datos vacía.

## Paginación

**El tamaño de página lo decide el servidor.** `?por_pagina=` se acepta y se recorta a 100; el valor
por defecto es 20; un valor no numérico cae al valor por defecto sin error. Un cliente no puede pedir
la tabla entera.

## Migraciones

Se generan con `uv run python manage.py makemigrations <app>` y **nunca se escriben ni se renombran a
mano**. `AUTH_USER_MODEL` no se cambia jamás: hacerlo después de la migración inicial es reescribir la
capa de datos entera.
