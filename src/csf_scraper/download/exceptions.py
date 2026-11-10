"""Excepciones del módulo de descarga de la Constancia de Situación Fiscal."""

from csf_scraper.exceptions import CsfScraperException


class FielCredentialsException(CsfScraperException):
    """Las credenciales FIEL no son válidas (certificado, llave o contraseña)."""


class SatNetworkException(CsfScraperException):
    """Una petición HTTP al SAT falló por un error de red o de transporte."""

    def __init__(self, url: str) -> None:
        super().__init__(f"The request to the SAT has failed: {url}")
        self.url = url


class SatLoginException(CsfScraperException):
    """El SAT rechazó el inicio de sesión (FIEL o CIEC)."""


class SatSsoException(CsfScraperException):
    """El flujo SSO/SAML del SAT no devolvió el formulario esperado."""


class SatFormNotFoundException(CsfScraperException):
    """No se encontró el formulario esperado en la respuesta HTML del SAT."""


class ConstanciaNotAvailableException(CsfScraperException):
    """El SAT no devolvió la constancia en PDF."""


class InvalidPdfException(CsfScraperException):
    """Los bytes recibidos no corresponden a un documento PDF válido."""
