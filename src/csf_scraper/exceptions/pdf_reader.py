"""Excepciones del lector de PDF."""

from csf_scraper.exceptions import CsfScraperException


class CifFromPdfNotFoundException(CsfScraperException):
    """No se pudo obtener el idCIF del PDF procesado."""


class EmptyPdfContentException(CsfScraperException):
    """El contenido del PDF está vacío."""


class RfcFromPdfNotFoundException(CsfScraperException):
    """No se pudo obtener el RFC del PDF procesado."""


class PdfToTextConvertException(CsfScraperException):
    """La ejecución de ``pdftotext`` falló."""

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
