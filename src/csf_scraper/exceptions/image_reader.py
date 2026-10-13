"""Excepciones del lector de imágenes (CSF escaneada)."""

from csf_scraper.exceptions import CsfScraperException


class InvalidImageException(CsfScraperException):
    """La ruta de la imagen no existe o no puede leerse."""


class InvalidImageFormatException(CsfScraperException):
    """El archivo recibido no es una imagen soportada (JPEG o PNG)."""


class ImageReaderNotConfiguredException(CsfScraperException):
    """No se inyectó un motor de lectura de imágenes (LLM/OCR)."""

    def __init__(self) -> None:
        super().__init__(
            "An image reader is required to obtain the data from an image; "
            "inject one via Scraper(..., image_reader=...).",
        )


class ImageReadingException(CsfScraperException):
    """El motor de lectura de imágenes (LLM/OCR) falló al procesar la CSF."""


class RfcFromImageNotFoundException(CsfScraperException):
    """No se pudo obtener el RFC de la imagen procesada."""


class CifFromImageNotFoundException(CsfScraperException):
    """No se pudo obtener el idCIF de la imagen procesada."""
