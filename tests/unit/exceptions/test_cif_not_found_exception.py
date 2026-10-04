from csf_scraper import CifNotFoundException, CsfScraperException


def test_implements_library_exception_type() -> None:
    assert issubclass(CifNotFoundException, CsfScraperException)
