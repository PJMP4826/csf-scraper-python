from csf_scraper.pdf_reader import PdfCsfTextParser
from tests.helpers import file_contents


def test_obtains_cif() -> None:
    extractor = PdfCsfTextParser(file_contents("csf-content.txt"))
    assert extractor.get_cif_id() == "12345678"


def test_bad_content_returns_empty_rfc() -> None:
    extractor = PdfCsfTextParser(file_contents("csf-bad-content.txt"))
    assert extractor.get_cif_id() is None
