"""Value object del idCIF (identificador del CIF del SAT)."""

import re
from typing import Any, Self

from pydantic_core import CoreSchema, core_schema

from csf_scraper.exceptions.value_objects import InvalidIdCifFormatException

#: Entre 8 y 13 dígitos (los idCIF observados van de 8 a 13 posiciones).
_PATTERN = re.compile(r"\d{8,13}\Z")


class IdCif(str):
    """idCIF validado (de 8 a 13 dígitos).

    Se construye con ``IdCif("1904014102123")``; lanza
    :class:`~csf_scraper.exceptions.value_objects.InvalidIdCifFormatException` si el
    valor no cumple el formato.
    """

    __slots__ = ()

    def __new__(cls, value: Any) -> Self:
        if isinstance(value, cls):
            return value
        text = value.strip() if isinstance(value, str) else value
        if not isinstance(text, str) or _PATTERN.fullmatch(text) is None:
            raise InvalidIdCifFormatException(f"Invalid idCIF format: {value!r}")
        return super().__new__(cls, text)

    @classmethod
    def ensure(cls, value: Any) -> Self:
        """Convierte ``value`` a :class:`IdCif` validando su formato."""
        return cls(value)

    @classmethod
    def __get_pydantic_core_schema__(cls, source: Any, handler: Any) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )
