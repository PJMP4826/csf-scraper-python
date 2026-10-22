"""Lectura de imágenes de la Constancia de Situación Fiscal.

El paquete base solo expone el puerto, el adaptador de ruta y la base de los
lectores LLM. :class:`GeminiImageReader` vive en
``csf_scraper.image_readers.adapters`` y requiere el extra ``llm-gemini``, por
eso se resuelve de forma perezosa (:pep:`562`).
"""

from typing import TYPE_CHECKING

from csf_scraper.image_readers.csf_image_extractor import CsfImageExtractor
from csf_scraper.image_readers.ports import ImageReaderPort
from csf_scraper.image_readers.schemas import RfcCifSchema
from csf_scraper.image_readers.services import (
    CSF_PROMPT,
    MAX_RETRIES,
    MAX_RETRY_BACKOFF,
    RETRY_BACKOFF,
    RETRY_PROMPT,
    LlmImageReaderService,
)

if TYPE_CHECKING:
    from csf_scraper.image_readers.adapters.llms import GeminiImageReader

__all__ = [
    "CSF_PROMPT",
    "MAX_RETRIES",
    "MAX_RETRY_BACKOFF",
    "RETRY_BACKOFF",
    "RETRY_PROMPT",
    "CsfImageExtractor",
    "GeminiImageReader",
    "ImageReaderPort",
    "LlmImageReaderService",
    "RfcCifSchema",
]


def __getattr__(name: str) -> object:
    """Resuelve :class:`GeminiImageReader` de forma perezosa.

    Mantiene el import base libre de ``google-genai`` y de
    ``llama-index-llms-google-genai``; si se pide sin el extra ``llm-gemini``
    se propaga el ``ModuleNotFoundError`` del paquete faltante.
    """
    if name == "GeminiImageReader":
        from csf_scraper.image_readers.adapters.llms import GeminiImageReader

        return GeminiImageReader

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
