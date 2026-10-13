from csf_scraper.pdf_reader import PdfCsfTextReader
from tests.helpers import file_contents


def test_obtains_cif() -> None:
    extractor = PdfCsfTextReader(file_contents("csf-content.txt"))
    assert extractor.get_cif_id() == "12345678"


def test_bad_content_returns_empty_rfc() -> None:
    extractor = PdfCsfTextReader(file_contents("csf-bad-content.txt"))
    assert extractor.get_cif_id() is None
