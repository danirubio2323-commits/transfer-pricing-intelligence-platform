"""El único punto donde se juntan Django y el dominio.

Aquí no hay nada de HTTP: ni `request`, ni `HttpResponse`, ni códigos de estado.
Esa frontera es lo que permite que este mismo código lo llame mañana un comando
de gestión o el arnés de evaluación sin arrastrar una petición web falsa.

La capa de IA todavía no está enchufada: la añade el paso 17, y lo hará aquí,
después de comprobar la cuota. El orden importa y por eso el tope se construye
antes (paso 16).
"""

from __future__ import annotations

import structlog

from apps.analisis.models import Caso
from apps.comun.escrituras import crear_caso_de
from tp_domain.calculations.arm_length_range import calculate_arm_length_range
from tp_domain.models import Transaction

logger = structlog.get_logger(__name__)


def crear_caso(usuario, transaction: Transaction, titulo: str) -> Caso:
    """Calcula, persiste con propietario y devuelve el caso.

    El motor se ejecuta entero antes de tocar la base de datos: si el cálculo
    fallara, no queda una fila a medias.
    """
    resultado = calculate_arm_length_range(transaction)

    # Se crea desde `apps/comun`, igual que se lee: el propietario no puede
    # depender de que quien escriba el servicio se acuerde de ponerlo.
    caso = crear_caso_de(usuario, titulo, resultado.model_dump(mode="json"))

    logger.info(
        "caso_creado",
        caso=str(caso.id),
        usuario=usuario.get_username(),
        pagadora=transaction.payer_country,
        perceptora=transaction.recipient_country,
        # La posición vive en cada veredicto por jurisdicción, no en el
        # resultado: el rango es uno, pero el Derecho aplicable es de cada país.
        posiciones={a.country: getattr(a.position, "value", None) for a in resultado.assessments},
    )
    return caso
