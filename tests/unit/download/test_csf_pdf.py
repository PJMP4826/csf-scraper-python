import hashlib

import pytest

from csf_scraper.download.exceptions import InvalidPdfException
from csf_scraper.download.value_objects import CsfPdf

_PDF = b"%PDF-1.7\n%fake constancia\n"


def test_new_from_contents_accepts_a_pdf() -> None:
    pdf = CsfPdf.new_from_contents(_PDF)

    assert pdf.as_bytes() == _PDF
    assert pdf.size == len(_PDF)
    assert len(pdf) == len(_PDF)
    assert pdf.sha256 == hashlib.sha256(_PDF).hexdigest()


def test_new_from_contents_rejects_empty_bytes() -> None:
    with pytest.raises(InvalidPdfException):
        CsfPdf.new_from_contents(b"")


def test_new_from_contents_rejects_non_pdf_bytes() -> None:
    with pytest.raises(InvalidPdfException):
        CsfPdf.new_from_contents(b"<html>not a pdf</html>")


def test_save_writes_the_bytes(tmp_path) -> None:  # type: ignore[no-untyped-def]
    pdf = CsfPdf.new_from_contents(_PDF)
    path = tmp_path / "constancia.pdf"

    pdf.save(str(path))

    assert path.read_bytes() == _PDF


def test_new_from_path_reads_and_validates(tmp_path) -> None:  # type: ignore[no-untyped-def]
    path = tmp_path / "constancia.pdf"
    path.write_bytes(_PDF)

    assert CsfPdf.new_from_path(str(path)).as_bytes() == _PDF


def test_new_from_missing_path_raises() -> None:
    with pytest.raises(InvalidPdfException):
        CsfPdf.new_from_path("/no/existe/constancia.pdf")
