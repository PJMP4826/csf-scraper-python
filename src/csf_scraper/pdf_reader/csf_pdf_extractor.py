"""Extracción del RFC y el idCIF a partir de un archivo PDF de CSF."""

from typing import Protocol

from csf_scraper.pdf_reader.pdf_csf_text_parser import PdfCsfTextParser
from csf_scraper.pdf_reader.pdf_to_text import PdfToText
from csf_scraper.ports.rfc_cif_extractor_port import RfcCifExtractorPort
from csf_scraper.rfc_cif_data import RfcCifData


class PdfTextProvider(Protocol):
    """Fuente del texto de un PDF; permite sustituir ``pdftotext`` en los tests."""

    async def extract(self, path: str) -> str:
        """Devuelve el texto plano del PDF en ``path``."""
        ...


class CsfPdfExtractor(RfcCifExtractorPort):
    """Implementa :class:`RfcCifExtractorPort` leyendo CSFs en PDF.

    Convierte el PDF a texto (``pdftotext`` por omisión, de forma asíncrona) y
    delega el *parsing* en :class:`PdfCsfTextParser`. El proveedor de texto se
    puede inyectar para probar el extractor sin invocar el binario.
    """

    def __init__(self, text_provider: PdfTextProvider | None = None) -> None:
        self._text_provider: PdfTextProvider = text_provider or PdfToText()

    async def extract(self, path: str) -> RfcCifData:
        """Devuelve el RFC y el idCIF del PDF en ``path``."""
        contents = await self._text_provider.extract(path)
        return PdfCsfTextParser(contents).extract()
