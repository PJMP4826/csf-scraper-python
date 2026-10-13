"""Adaptador del lector de imágenes basado en un LLM multimodal (Gemini)."""

from csf_scraper.rfc_cif_data import RfcCifData
from csf_scraper.value_objects.csf_image import CsfImage


class GeminiImageReader:
    """Lee el RFC y el idCIF de una imagen de CSF usando Gemini.

    Implementa el puerto
    :class:`~csf_scraper.image_readers.ports.image_reader_port.ImageReaderPort`.
    """

    def __init__(self, api_key: str, model_name: str) -> None:
        self._api_key = api_key
        self._model_name = model_name

    def read(self, image: CsfImage) -> RfcCifData:
        """Extrae el RFC y el idCIF de ``image`` mediante Gemini.

        TODO: invocar el modelo multimodal con ``image.get_mime_type()`` y
        ``image.as_base64()``, mapear la respuesta a :class:`RfcCifData` y
        envolver los fallos del motor en
        :class:`~csf_scraper.exceptions.image_reader.ImageReadingException`.
        """
        raise NotImplementedError
