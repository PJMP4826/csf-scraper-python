import pytest

from csf_scraper import RfcCifData
from csf_scraper.exceptions.pdf_reader import (
    CifFromPdfNotFoundException,
    RfcFromPdfNotFoundException,
)
from csf_scraper.pdf_reader import PdfCsfTextReader
from tests.helpers import file_contents


def test_extract_returns_validated_dto() -> None:
    data = PdfCsfTextReader(file_contents("csf-content.txt")).extract()

    assert isinstance(data, RfcCifData)
    assert data.rfc == "DIM8701081LA"
    assert data.id_cif == "12345678"


def test_extract_without_rfc_raises() -> None:
    with pytest.raises(RfcFromPdfNotFoundException):
        PdfCsfTextReader(file_contents("csf-bad-content.txt")).extract()


def test_extract_without_cif_raises() -> None:
    with pytest.raises(CifFromPdfNotFoundException):
        PdfCsfTextReader("RFC: DIM8701081LA\n").extract()
