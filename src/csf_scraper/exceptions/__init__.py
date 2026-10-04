"""Excepciones de la librería (migración de ``src/Exceptions/*.php``)."""


class CsfScraperException(Exception):
    """Tipo base de todas las excepciones de la librería.

    Equivalente a la interfaz ``PhpCfdi\\CsfScraper\\Exceptions\\CsfScraperException``.
    """


class CifDownloadException(CsfScraperException):
    """La petición HTTP para descargar el CIF falló.

    Equivalente a ``Exceptions\\CifDownloadException`` (extiende ``RuntimeException`` en PHP).
    Mensaje original: ``The request has failed``.
    """

    def __init__(self, url: str, previous: BaseException) -> None:
        super().__init__("The request has failed")
        self.url = url
        self.previous = previous


class CifNotFoundException(CsfScraperException):
    """No se encontró la información del CIF en la respuesta del SAT.

    Equivalente a ``Exceptions\\CifNotFoundException``.
    """
