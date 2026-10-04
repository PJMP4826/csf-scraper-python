"""Interfaces del dominio (migración de ``src/Interfaces/*.php``)."""

from typing import Protocol

from csf_scraper.persona_fisica import PersonaFisica
from csf_scraper.persona_moral import PersonaMoral


class DataExtractorInterface(Protocol):
    """Equivalente a ``PhpCfdi\\CsfScraper\\Interfaces\\DataExtractorInterface``."""

    def extract(self, is_fisica: bool) -> PersonaMoral | PersonaFisica:
        """Extrae la información de la persona desde el HTML del CSF."""
        ...
