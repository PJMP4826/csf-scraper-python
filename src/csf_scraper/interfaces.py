"""Interfaces del dominio (migración de ``src/Interfaces/*.php``)."""

from typing import Protocol

from csf_scraper.persona_fisica import PersonaFisica
from csf_scraper.persona_moral import PersonaMoral


class DataExtractorInterface(Protocol):
    """Equivalente a ``PhpCfdi\\CsfScraper\\Interfaces\\DataExtractorInterface``."""

    def extract(self, is_fisica: bool) -> PersonaMoral | PersonaFisica:
        """Extrae la información de la persona desde el HTML del CSF."""
        ...


class ScraperInterface(Protocol):
    """Equivalente a ``PhpCfdi\\CsfScraper\\Interfaces\\ScraperInterface``."""

    def obtain_from_rfc_and_cif(self, rfc: str, id_cif: str) -> PersonaMoral | PersonaFisica:
        """Obtiene la persona con la información del sitio del SAT."""
        ...

    def obtain_from_pdf_path(self, path: str) -> PersonaMoral | PersonaFisica:
        """Obtiene la persona; el RFC y el idCIF se leen de la CSF en PDF."""
        ...
