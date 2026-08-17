"""Formulario de la operación vinculada.

Es un `forms.Form` y no un `ModelForm` a propósito: aquí no se guarda un
formulario, se guarda un `AnalysisResult`. Lo que este formulario produce es un
`Transaction` del dominio, y el dominio es quien valida de verdad.

Las opciones del desplegable de tipo salen de `SUPPORTED_TRANSACTION_TYPES`, no
están escritas a mano. Cuando la Fase 2 añada los servicios intragrupo, el
desplegable los recoge solo — y mientras tanto no ofrece nada que el motor no
sepa calcular.
"""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

from django import forms
from pydantic import ValidationError

from tp_domain.models import (
    SUPPORTED_TRANSACTION_TYPES,
    Industry,
    Transaction,
    TransactionType,
)

LARGO_TITULO = 160

#: Se derivan del dominio. Añadir un tipo allí lo hace aparecer aquí.
OPCIONES_TIPO = [
    (t.value, t.value.replace("_", " ").capitalize())
    for t in sorted(SUPPORTED_TRANSACTION_TYPES, key=lambda t: t.value)
]
OPCIONES_INDUSTRIA = [(i.value, i.value.capitalize()) for i in Industry]


class CasoForm(forms.Form):
    titulo = forms.CharField(max_length=LARGO_TITULO, required=False, label="Título")
    description = forms.CharField(max_length=300, label="Descripción de la operación")
    payer_country = forms.CharField(min_length=2, max_length=2, label="Jurisdicción pagadora")
    recipient_country = forms.CharField(min_length=2, max_length=2, label="Jurisdicción perceptora")
    transaction_type = forms.ChoiceField(choices=OPCIONES_TIPO, label="Tipo de operación")
    industry = forms.ChoiceField(choices=OPCIONES_INDUSTRIA, label="Sector")
    amount_eur = forms.DecimalField(min_value=Decimal("0.01"), label="Importe (€)")
    rate_percent = forms.DecimalField(
        min_value=Decimal("0"), max_value=Decimal("100"), label="Tipo (%)"
    )
    #: Sin valor por defecto: no existe un análisis «de hoy». La fecha efectiva
    #: determina qué comparables entran en la muestra.
    effective_date = forms.DateField(label="Fecha efectiva")

    def clean(self):
        """Construye el `Transaction` y traduce los errores de pydantic a errores de formulario."""
        datos = super().clean()
        if self.errors:
            return datos

        try:
            datos["transaction"] = Transaction(
                description=datos["description"],
                payer_country=datos["payer_country"],
                recipient_country=datos["recipient_country"],
                transaction_type=TransactionType(datos["transaction_type"]),
                industry=Industry(datos["industry"]),
                amount_eur=datos["amount_eur"],
                rate_percent=datos["rate_percent"],
                effective_date=datos["effective_date"],
            )
        except ValidationError as invalido:
            self._trasladar(invalido)
            return datos

        datos["titulo"] = self._titulo(datos)
        return datos

    def _trasladar(self, invalido: ValidationError) -> None:
        """Los errores de campo al campo; los del modelo entero, sin asociar.

        Así el usuario ve un solo conjunto de errores, no dos lenguajes distintos
        —el de Django y el de pydantic— diciendo lo mismo en dos sitios.
        """
        for fallo in invalido.errors():
            campo = fallo["loc"][0] if fallo["loc"] else None
            mensaje = fallo["msg"].removeprefix("Value error, ")
            if isinstance(campo, str) and campo in self.fields:
                self.add_error(campo, mensaje)
            else:
                self.add_error(None, mensaje)

    def _titulo(self, datos: dict) -> str:
        """Si no lo ponen, se deriva. Y si el derivado ya existe, se desambigua.

        La restricción única parcial de §4 impide que dos casos vivos del mismo
        usuario compartan título; sin desambiguar, guardar el segundo fallaría
        con un error de base de datos en vez de con algo legible.
        """
        titulo = (datos.get("titulo") or "").strip()
        if titulo:
            return titulo[:LARGO_TITULO]

        derivado = datos["description"].strip()[:LARGO_TITULO]
        if self._ya_existe(derivado):
            fecha = datos["effective_date"].isoformat()
            derivado = f"{derivado[: LARGO_TITULO - len(fecha) - 3]} ({fecha})"
        return derivado

    def _ya_existe(self, titulo: str) -> bool:
        usuario = getattr(self, "usuario", None)
        if usuario is None:
            return False
        from apps.comun.consultas import casos_de

        return casos_de(usuario).filter(titulo=titulo).exists()

    def __init__(self, *args, usuario=None, **kwargs):
        self.usuario = usuario
        super().__init__(*args, **kwargs)


def fecha_por_defecto() -> dt.date:
    """Solo para la plantilla, como sugerencia visible. Nunca como valor implícito."""
    return dt.date.today()
