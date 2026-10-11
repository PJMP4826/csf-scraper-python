"""Conversión de fechas ``dd-mm-yyyy`` a :class:`datetime.datetime`."""

from datetime import datetime
from typing import Annotated, Any

from pydantic import BeforeValidator


def parse_date(value: str) -> datetime | None:
    """Convierte una fecha ``dd-mm-yyyy`` a la medianoche; ``None`` si es inválida."""
    try:
        return datetime.strptime(value, "%d-%m-%Y")
    except (TypeError, ValueError):
        return None


def _coerce_date(value: Any) -> datetime | None:
    if value is None or isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return parse_date(value)
    return None


#: Campo de fecha opcional que acepta ``datetime``, ``None`` o una cadena ``dd-mm-yyyy``.
DateField = Annotated[datetime | None, BeforeValidator(_coerce_date)]
