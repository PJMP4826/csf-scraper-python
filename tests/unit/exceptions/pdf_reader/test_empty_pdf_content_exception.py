from csf_scraper import CsfScraperException, EmptyPdfContentException


def test_implements_library_exception_type() -> None:
    assert issubclass(EmptyPdfContentException, CsfScraperException)
