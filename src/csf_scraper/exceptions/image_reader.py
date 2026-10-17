"""Excepciones del lector de imágenes (CSF escaneada)."""

from csf_scraper.exceptions import CsfScraperException


class InvalidImageException(CsfScraperException):
    """La ruta de la imagen no existe o no puede leerse."""


class InvalidImageFormatException(CsfScraperException):
    """El archivo recibido no es una imagen soportada (JPEG o PNG)."""


class ImageExtractorNotConfiguredException(CsfScraperException):
    """No se inyectó un extractor de imágenes (motor LLM/OCR)."""

    def __init__(self) -> None:
        super().__init__(
            "An image extractor is required to obtain the data from an image; "
            "inject one via Scraper(..., image_extractor=...).",
        )


class ImageReadingException(CsfScraperException):
    """El motor de lectura de imágenes (LLM/OCR) falló al procesar la CSF.

    ``provider`` y ``model`` identifican el motor que falló, de modo que un
    adaptador pueda reportar el origen del error sin exponer credenciales.
    """

    def __init__(
        self,
        message: str = "The image reader failed to process the CSF.",
        *,
        provider: str | None = None,
        model: str | None = None,
    ) -> None:
        super().__init__(message)
        self.provider = provider
        self.model = model


class RfcFromImageNotFoundException(CsfScraperException):
    """No se pudo obtener el RFC de la imagen procesada."""


class CifFromImageNotFoundException(CsfScraperException):
    """No se pudo obtener el idCIF de la imagen procesada."""
