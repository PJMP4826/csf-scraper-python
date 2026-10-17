import asyncio

import pytest

from csf_scraper import PdfCsfTextParser, RfcCifData
from csf_scraper.exceptions.pdf_reader import (
    CifFromPdfNotFoundException,
    EmptyPdfContentException,
    RfcFromPdfNotFoundException,
)
from csf_scraper.pdf_reader import CsfPdfExtractor
from tests.helpers import file_contents


class _StubTextProvider:
    def __init__(self, contents: str) -> None:
        self.contents = contents
        self.received: str | None = None

    async def extract(self, path: str) -> str:
        self.received = path
        return self.contents


def test_parser_returns_validated_dto() -> None:
    data = PdfCsfTextParser(file_contents("csf-content.txt")).extract()

    assert isinstance(data, RfcCifData)
    assert data.rfc == "DIM8701081LA"
    assert data.id_cif == "12345678"


def test_parser_without_rfc_raises() -> None:
    with pytest.raises(RfcFromPdfNotFoundException):
        PdfCsfTextParser(file_contents("csf-bad-content.txt")).extract()


def test_parser_without_cif_raises() -> None:
    with pytest.raises(CifFromPdfNotFoundException):
        PdfCsfTextParser("RFC: DIM8701081LA\n").extract()


def test_parser_with_empty_contents_raises() -> None:
    with pytest.raises(EmptyPdfContentException):
        PdfCsfTextParser("")


def test_reader_extracts_from_path() -> None:
    provider = _StubTextProvider(file_contents("csf-content.txt"))

    data = asyncio.run(CsfPdfExtractor(provider).extract("csf.pdf"))

    assert provider.received == "csf.pdf"
    assert data.rfc == "DIM8701081LA"
    assert data.id_cif == "12345678"
