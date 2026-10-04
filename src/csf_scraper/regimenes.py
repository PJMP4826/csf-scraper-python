"""Colección de regímenes (migración de ``src/Regimenes.php``)."""

from typing import Any

from pydantic import BaseModel, Field, model_serializer

from csf_scraper.regimen import Regimen


class Regimenes(BaseModel):
    """Lista ordenada de :class:`Regimen`.

    Equivalente a ``PhpCfdi\\CsfScraper\\Regimenes``.
    """

    regimenes: list[Regimen] = Field(default_factory=list)

    def get_regimenes(self) -> list[Regimen]:
        """Equivalente a ``Regimenes::getRegimenes()``."""
        return self.regimenes

    def add_regimen(self, *regimenes: Regimen) -> None:
        """Equivalente a ``Regimenes::addRegimen(Regimen $regimen, Regimen ...$regimenes)``."""
        if not regimenes:
            raise TypeError("add_regimen() missing required argument")
        self.regimenes.extend(regimenes)

    def to_array(self) -> list[dict[str, Any]]:
        """Equivalente a ``Regimenes::toArray()``."""
        return [regimen.to_array() for regimen in self.regimenes]

    @model_serializer(mode="plain")
    def serialize_regimenes(self) -> list[dict[str, Any]]:
        """Equivalente a ``Regimenes::jsonSerialize()`` (la colección serializa como lista)."""
        return self.to_array()
