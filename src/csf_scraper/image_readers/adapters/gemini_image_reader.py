"""Adaptador del lector de imágenes basado en Gemini (Google GenAI).

Aquí sí se importan las librerías de LlamaIndex, porque el transporte hacia el
proveedor es responsabilidad exclusiva del adaptador::

    from llama_index.llms.google_genai import GoogleGenAI

    reader = GeminiImageReader(api_key="…", model_name="gemini-2.5-flash")

El paquete ``llama-index-llms-google-genai`` es una dependencia opcional
(``pip install csf-scraper[llm-gemini]``).
"""

from __future__ import annotations


from llama_index.llms.google_genai import GoogleGenAI

from csf_scraper.value_objects.csf_image import CsfImage
from csf_scraper.image_readers.ports.image_reader_port import ImageReaderPort
from csf_scraper.image_readers.schemas.rfc_cif_schema import RfcCifSchema
from csf_scraper.image_readers.services.llm_image_reader_service import (
    MAX_RETRIES,
    LlmImageReaderService,
)


class GeminiImageReader(LlmImageReaderService, ImageReaderPort):
    """Lee el RFC y el idCIF de una imagen de CSF usando Gemini.

    Hereda de :class:`~csf_scraper.image_readers.services.LlmImageReaderService`
    el prompt, el armado de la imagen, los reintentos y el mapeo a
    :class:`~csf_scraper.rfc_cif_data.RfcCifData`. Lo propio de este adaptador
    es crear el cliente de LlamaIndex y ejecutar el programa multimodal que
    tipa la respuesta con :class:`~csf_scraper.image_readers.RfcCifSchema`.

    Args:
        api_key: Clave de la API de Google GenAI.
        model_name: Modelo de Gemini a utilizar.
        max_retries: Intentos totales antes de rendirse.
    """

    def __init__(
        self,
        api_key: str,
        model_name: str,
        *,
        max_retries: int = MAX_RETRIES,
    ) -> None:
        if not api_key:
            raise ValueError("The Gemini image reader requires an API key.")
        super().__init__(model=model_name, max_retries=max_retries)
        self._llm_provider = GoogleGenAI(api_key=api_key, model=model_name)

    @property
    def provider(self) -> str:
        """Identificador del proveedor."""
        return "gemini"

    async def read(self, image: CsfImage) -> RfcCifSchema:
        """Ejecuta el programa multimodal de LlamaIndex y tipa la respuesta."""
        return await self._run_program(image=image, llm_provider=self._llm_provider)
