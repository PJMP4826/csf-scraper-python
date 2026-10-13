"""Obtiene los datos fiscales actuales de una persona moral o física del SAT."""

from csf_scraper.data_extractor import DataExtractor
from csf_scraper.exceptions import (
    CifDownloadException,
    CifNotFoundException,
    CsfScraperException,
)
from csf_scraper.exceptions.image_reader import (
    CifFromImageNotFoundException,
    ImageReaderNotConfiguredException,
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
from csf_scraper.image_readers.ports.image_reader_port import ImageReaderPort
from csf_scraper.pdf_reader import PdfCsfTextReader
from csf_scraper.persona import Persona
from csf_scraper.persona_fisica import PersonaFisica
from csf_scraper.persona_moral import PersonaMoral
from csf_scraper.regimen import Regimen
from csf_scraper.rfc_cif_data import RfcCifData
from csf_scraper.scraper import Scraper
from csf_scraper.value_objects import CsfImage, IdCif, Rfc

__all__ = [
    "CifDownloadException",
    "CifFromImageNotFoundException",
    "CifFromPdfNotFoundException",
    "CifNotFoundException",
    "CsfImage",
    "CsfScraperException",
    "DataExtractor",
    "EmptyPdfContentException",
    "IdCif",
    "ImageReaderNotConfiguredException",
    "ImageReaderPort",
    "ImageReadingException",
    "InvalidIdCifFormatException",
    "InvalidImageException",
    "InvalidImageFormatException",
    "InvalidRfcFormatException",
    "PdfCsfTextReader",
    "PdfToTextConvertException",
    "Persona",
    "PersonaFisica",
    "PersonaMoral",
    "Regimen",
    "Rfc",
    "RfcCifData",
    "RfcFromImageNotFoundException",
    "RfcFromPdfNotFoundException",
    "Scraper",
]
