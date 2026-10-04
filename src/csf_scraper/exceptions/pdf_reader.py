"""Excepciones del lector de PDF (migración de ``src/Exceptions/PdfReader/*.php``)."""

from csf_scraper.exceptions import CsfScraperException


class CifFromPdfNotFoundException(CsfScraperException):
    """No se pudo obtener el idCIF del PDF procesado.

    Equivalente a ``Exceptions\\PdfReader\\CifFromPdfNotFoundException``.
    """


class EmptyPdfContentException(CsfScraperException):
    """El contenido del PDF está vacío.

    Equivalente a ``Exceptions\\PdfReader\\EmptyPdfContentException``.
    """


class RfcFromPdfNotFoundException(CsfScraperException):
    """No se pudo obtener el RFC del PDF procesado.

    Equivalente a ``Exceptions\\PdfReader\\RfcFromPdfNotFoundException``.
    """


class PdfToTextConvertException(CsfScraperException):
    """La ejecución de ``pdftotext`` falló.

    Equivalente a ``Exceptions\\PdfReader\\PdfToTextConvertException``
    (extiende ``RuntimeException`` en PHP).
    """

    def __init__(
        self,
        message: str,
        command: list[str],
        exit_code: int,
        output: str,
        error: str,
    ) -> None:
        super().__init__(message)
        self.command = command
        self.exit_code = exit_code
        self.output = output
        self.error = error
