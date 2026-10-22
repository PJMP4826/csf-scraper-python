"""Obtiene los datos fiscales actuales de una persona moral o física del SAT.

El núcleo de la librería no depende de ningún cliente de LLM. Los adaptadores
que sí lo requieren (por ahora :class:`GeminiImageReader`, que necesita el
extra ``llm-gemini``) se resuelven de forma perezosa (:pep:`562`), de modo que
``import csf_scraper`` funciona con las dependencias base únicamente.
"""

from typing import TYPE_CHECKING

from csf_scraper.data_extractor import DataExtractor
from csf_scraper.exceptions import (
    CifDownloadException,
    CifNotFoundException,
    CsfScraperException,
)
from csf_scraper.exceptions.image_reader import (
    CifFromImageNotFoundException,
    ImageExtractorNotConfiguredException,
    ImageReaderApiException,
    ImageReaderAuthenticationException,
    ImageReaderUnavailableException,
    ImageReadingException,
    InvalidImageException,
    InvalidImageFormatException,
    RfcFromImageNotFoundException,
)
from csf_scraper.exceptions.pdf_reader import (
    CifFromPdfNotFoundException,
    EmptyPdfContentException,
    PdfToTextConvertException,
    RfcFromPdfNotFoundException,
)
from csf_scraper.exceptions.value_objects import (
    InvalidIdCifFormatException,
    InvalidRfcFormatException,
)
from csf_scraper.image_readers import (
    CSF_PROMPT,
    MAX_RETRIES,
    MAX_RETRY_BACKOFF,
    RETRY_BACKOFF,
    RETRY_PROMPT,
    CsfImageExtractor,
    ImageReaderPort,
    LlmImageReaderService,
    RfcCifSchema,
)
from csf_scraper.pdf_reader import CsfPdfExtractor, PdfCsfTextParser, PdfTextProvider
from csf_scraper.persona import Persona
from csf_scraper.persona_fisica import PersonaFisica
from csf_scraper.persona_moral import PersonaMoral
from csf_scraper.ports import RfcCifExtractorPort
from csf_scraper.regimen import Regimen
from csf_scraper.rfc_cif_data import RfcCifData
from csf_scraper.scraper import Scraper
from csf_scraper.value_objects import CsfImage, IdCif, Rfc

if TYPE_CHECKING:
    from csf_scraper.image_readers.adapters.llms import GeminiImageReader

__all__ = [
    "CSF_PROMPT",
    "MAX_RETRIES",
    "MAX_RETRY_BACKOFF",
    "RETRY_BACKOFF",
    "RETRY_PROMPT",
    "CifDownloadException",
    "CifFromImageNotFoundException",
    "CifFromPdfNotFoundException",
    "CifNotFoundException",
    "CsfImage",
    "CsfImageExtractor",
    "CsfPdfExtractor",
    "CsfScraperException",
    "DataExtractor",
    "EmptyPdfContentException",
    "GeminiImageReader",
    "IdCif",
    "ImageExtractorNotConfiguredException",
    "ImageReaderApiException",
    "ImageReaderAuthenticationException",
    "ImageReaderPort",
    "ImageReaderUnavailableException",
    "ImageReadingException",
    "InvalidIdCifFormatException",
    "InvalidImageException",
    "InvalidImageFormatException",
    "InvalidRfcFormatException",
    "LlmImageReaderService",
    "PdfCsfTextParser",
    "PdfTextProvider",
    "PdfToTextConvertException",
    "Persona",
    "PersonaFisica",
    "PersonaMoral",
    "Regimen",
    "Rfc",
    "RfcCifData",
    "RfcCifExtractorPort",
    "RfcCifSchema",
    "RfcFromImageNotFoundException",
    "RfcFromPdfNotFoundException",
    "Scraper",
]


def __getattr__(name: str) -> object:
    """Resuelve los adaptadores opcionales de forma perezosa.

    Así ``from csf_scraper import GeminiImageReader`` sigue funcionando, pero
    solo importa el SDK de Google cuando alguien realmente lo pide.
    """
    if name == "GeminiImageReader":
        from csf_scraper.image_readers.adapters.llms import GeminiImageReader

        return GeminiImageReader

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
