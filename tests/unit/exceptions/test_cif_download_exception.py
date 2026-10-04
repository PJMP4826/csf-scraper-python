from csf_scraper import CifDownloadException, CsfScraperException


def test_implements_library_exception_type() -> None:
    assert issubclass(CifDownloadException, CsfScraperException)


def test_properties() -> None:
    url = "https://example.com"
    previous = Exception("previous")
    exception = CifDownloadException(url, previous)

    assert exception.url == url
    assert exception.previous is previous
