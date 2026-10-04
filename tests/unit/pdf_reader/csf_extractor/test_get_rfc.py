import platform

import pytest

from csf_scraper.exceptions.pdf_reader import EmptyPdfContentException
from csf_scraper.pdf_reader import CsfExtractor
from tests.helpers import file_contents


def test_obtains_rfc() -> None:
    csf_extractor = CsfExtractor(file_contents("csf-content.txt"))
    assert csf_extractor.get_rfc() == "DIM8701081LA"


def test_bad_content_returns_empty_rfc() -> None:
    csf_extractor = CsfExtractor(file_contents("csf-bad-content.txt"))
    assert csf_extractor.get_rfc() is None


@pytest.mark.skipif(
    platform.system() != "Linux",
    reason="RequiresOperatingSystem('Linux')",
)
def test_cannot_read_content() -> None:
    with pytest.raises(EmptyPdfContentException):
        CsfExtractor("")
