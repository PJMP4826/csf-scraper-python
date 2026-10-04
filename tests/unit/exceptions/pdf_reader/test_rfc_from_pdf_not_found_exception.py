from csf_scraper import CsfScraperException, RfcFromPdfNotFoundException


def test_implements_library_exception_type() -> None:
    assert issubclass(RfcFromPdfNotFoundException, CsfScraperException)
