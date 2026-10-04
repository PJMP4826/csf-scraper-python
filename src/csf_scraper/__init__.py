"""Port Python de `phpcfdi/csf-scraper <https://github.com/phpcfdi/csf-scraper>`_."""

from csf_scraper.data_extractor import DataExtractor
from csf_scraper.exceptions import (
    CifDownloadException,
    CifNotFoundException,
    CsfScraperException,
)
from csf_scraper.exceptions.pdf_reader import (
    CifFromPdfNotFoundException,
    EmptyPdfContentException,
    PdfToTextConvertException,
    RfcFromPdfNotFoundException,
)
from csf_scraper.persona import Persona
from csf_scraper.persona_fisica import PersonaFisica
from csf_scraper.persona_moral import PersonaMoral
from csf_scraper.regimen import Regimen
from csf_scraper.regimenes import Regimenes
from csf_scraper.scraper import Scraper

__all__ = [
    "CifDownloadException",
    "CifFromPdfNotFoundException",
    "CifNotFoundException",
    "CsfScraperException",
    "DataExtractor",
    "EmptyPdfContentException",
    "PdfToTextConvertException",
    "Persona",
    "PersonaFisica",
    "PersonaMoral",
    "Regimen",
    "Regimenes",
    "RfcFromPdfNotFoundException",
    "Scraper",
]
