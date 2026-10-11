"""Excepciones de la librería."""


class CsfScraperException(Exception):
    """Tipo base de todas las excepciones de la librería."""


class CifDownloadException(CsfScraperException):
    """La petición HTTP para descargar la información del CIF falló."""

    def __init__(self, url: str) -> None:
        super().__init__("The request has failed")
        self.url = url


class CifNotFoundException(CsfScraperException):
    """No se encontró la información del CIF en la respuesta del SAT."""
