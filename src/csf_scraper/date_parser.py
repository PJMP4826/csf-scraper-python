"""Parsing de fechas, equivalente a ``DateTimeImmutable::createFromFormat('!d-m-Y', $valor)``.

Migración del uso de ``createFromFormat('!d-m-Y', ...)`` en ``Persona``,
``PersonaFisica``, ``PersonaMoral`` y ``Regimen``.
"""

import re
from datetime import datetime, timedelta
from typing import Annotated, Any

from pydantic import BeforeValidator

_DATE_PATTERN = re.compile(r"(\d{1,2})-(\d{1,2})-(\d{1,4})")


def parse_date(value: str) -> datetime | None:
    """Convierte ``dd-mm-yyyy`` a fecha a medianoche; devuelve ``None`` si PHP devolvería ``false``.

    Reproduce el comportamiento observado de ``createFromFormat``: entrada estricta
    (sin datos extra ni espacios), día/mes de 1-2 dígitos, año de 1-4 dígitos y
    normalización de desbordes (``31-02-2020`` -> ``2020-03-02``, ``00-01-2020`` ->
    ``2019-12-31``, ``01-13-2020`` -> ``2021-01-01``).
    """
    match = _DATE_PATTERN.fullmatch(value)
    if match is None:
        return None
    day, month, year = (int(group) for group in match.groups())
    month_offset = month - 1
    year += month_offset // 12
    month = month_offset % 12 + 1
    try:
        base = datetime(year, month, 1)
        return base + timedelta(days=day - 1)
    except (OverflowError, OSError, ValueError):
        # año fuera del rango soportado por datetime (PHP acepta, p. ej., el año 0000)
        return None


def _coerce_date(value: Any) -> datetime | None:
    if value is None or isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return parse_date(value)
    return None


#: Tipo de campo para las fechas de los modelos (``?DateTimeImmutable`` en PHP).
DateField = Annotated[datetime | None, BeforeValidator(_coerce_date)]
