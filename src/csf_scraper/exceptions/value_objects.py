"""Excepciones de los value objects del dominio."""

from csf_scraper.exceptions import CsfScraperException


class InvalidRfcFormatException(CsfScraperException, ValueError):
    """El valor recibido no corresponde al formato de un RFC."""


class InvalidIdCifFormatException(CsfScraperException, ValueError):
    """El valor recibido no corresponde al formato de un idCIF."""
