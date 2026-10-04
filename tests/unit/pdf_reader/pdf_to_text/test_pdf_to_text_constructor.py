import platform

import pytest

from csf_scraper.pdf_reader import PdfToText


@pytest.mark.skipif(
    platform.system() != "Linux",
    reason="RequiresOperatingSystem('Linux')",
)
def test_pdftotext_is_installed_default_path() -> None:
    pdf_to_text = PdfToText()
    assert isinstance(pdf_to_text, PdfToText)


def test_throw_exception_when_path_not_found() -> None:
    pdf_to_text = PdfToText("aaa")
    with pytest.raises(FileNotFoundError):
        pdf_to_text.extract("path")
