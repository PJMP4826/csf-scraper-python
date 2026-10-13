"""Value object del RFC (Registro Federal de Contribuyentes)."""

import re
from typing import Any, Self

from pydantic_core import CoreSchema, core_schema

from csf_scraper.exceptions.value_objects import InvalidRfcFormatException

#: Alfanumérico: de 3 a 4 letras (incluye ``Ñ`` y ``&``), 6 dígitos de fecha y 3 de homoclave.
_PATTERN = re.compile(r"[A-ZÑ&]{3,4}\d{6}[A-Z\d]{3}\Z")


class Rfc(str):
    """RFC validado de una persona física (13 caracteres) o moral (12 caracteres).

    Se construye con ``Rfc("DIM8701081LA")``; lanza
    :class:`~csf_scraper.exceptions.value_objects.InvalidRfcFormatException` si el
    valor no cumple el formato. Normaliza espacios y mayúsculas.
    """

    __slots__ = ()

    def __new__(cls, value: Any) -> Self:
        if isinstance(value, cls):
            return value
        text = value.strip().upper() if isinstance(value, str) else value
        if not isinstance(text, str) or _PATTERN.fullmatch(text) is None:
            raise InvalidRfcFormatException(f"Invalid RFC format: {value!r}")
        return super().__new__(cls, text)

    @classmethod
    def ensure(cls, value: Any) -> Self:
        """Convierte ``value`` a :class:`Rfc` validando (y normalizando) su formato."""
        return cls(value)

    def is_fisica(self) -> bool:
        """Indica si el RFC corresponde a una persona física (13 caracteres)."""
        return len(self) == 13

    def is_moral(self) -> bool:
        """Indica si el RFC corresponde a una persona moral (12 caracteres)."""
        return not self.is_fisica()

    @classmethod
    def __get_pydantic_core_schema__(cls, source: Any, handler: Any) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )
