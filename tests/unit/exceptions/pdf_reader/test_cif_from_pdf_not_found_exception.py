from csf_scraper import CifFromPdfNotFoundException, CsfScraperException


def test_implements_library_exception_type() -> None:
    assert issubclass(CifFromPdfNotFoundException, CsfScraperException)
