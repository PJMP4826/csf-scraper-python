"""Puerto que abstrae el motor de lectura de imágenes (LLM multimodal u OCR)."""

from abc import ABC, abstractmethod

from csf_scraper.rfc_cif_data import RfcCifData
from csf_scraper.value_objects.csf_image import CsfImage


class ImageReaderPort(ABC):
    """Extrae el :class:`RfcCifData` de la imagen ya materializada de una CSF.

    Este es el contrato de un **motor**, no de un origen: recibe una
    :class:`~csf_scraper.value_objects.CsfImage` en memoria y nunca toca el
    disco. Para leer desde una ruta se usa
    :class:`~csf_scraper.image_readers.CsfImageExtractor`, que adapta este
    puerto al contrato público
    :class:`~csf_scraper.ports.RfcCifExtractorPort`.

    Reglas del contrato:

    - No lee archivos: toda la validación de formato la hace :class:`CsfImage`.
    - Devuelve :class:`RfcCifData` con los value objects ya construidos.
    - Las implementaciones de la librería reportan sus fallos con excepciones
      de la librería; en particular
      :class:`~csf_scraper.exceptions.image_reader.ImageReadingException`. Un
      motor externo puede propagar sus propias excepciones.

    Implementaciones: :class:`~csf_scraper.image_readers.adapters.llms.GeminiImageReader`
    (hereda de :class:`~csf_scraper.image_readers.LlmImageReaderService` y de
    este puerto; sirve de base para otros proveedores) o un pipeline de OCR
    (OpenCV + Tesseract).
    """

    @abstractmethod
    async def read(self, image: CsfImage) -> RfcCifData:
        """Devuelve el RFC y el idCIF leídos de ``image``."""
        ...
