"""Puerto que abstrae el motor de lectura de imágenes (LLM multimodal u OCR)."""

from typing import Protocol

from csf_scraper.rfc_cif_data import RfcCifData
from csf_scraper.value_objects.csf_image import CsfImage


class ImageReaderPort(Protocol):
    """Extrae el :class:`RfcCifData` de la imagen de una CSF.

    Implementaciones posibles: un LLM multimodal (p. ej. Gemini) o un pipeline
    de OCR (OpenCV + Tesseract). El motor concreto es inyectado en
    :class:`~csf_scraper.scraper.Scraper`.
    """

    def read(self, image: CsfImage) -> RfcCifData:
        """Devuelve el RFC y el idCIF leídos de ``image``."""
        ...
