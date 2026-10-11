from csf_scraper import CifDownloadException, CsfScraperException


def test_implements_library_exception_type() -> None:
    assert issubclass(CifDownloadException, CsfScraperException)


def test_properties() -> None:
    url = "https://example.com"
    exception = CifDownloadException(url)

    assert exception.url == url
    assert str(exception) == "The request has failed"


def test_keeps_previous_exception_as_cause() -> None:
    previous = ValueError("previous")
    try:
        raise CifDownloadException("https://example.com") from previous
    except CifDownloadException as exception:
        assert exception.__cause__ is previous
