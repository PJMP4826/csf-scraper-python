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
    assert pdf.filename is None


def test_new_from_contents_keeps_the_original_filename() -> None:
    pdf = CsfPdf.new_from_contents(_PDF, filename="Csf_AAPU790804II9.pdf")

    assert pdf.filename == "Csf_AAPU790804II9.pdf"


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


def test_save_into_a_directory_uses_the_original_filename(tmp_path) -> None:  # type: ignore[no-untyped-def]
    pdf = CsfPdf.new_from_contents(_PDF, filename="Csf_AAPU790804II9.pdf")

    pdf.save(str(tmp_path))

    assert (tmp_path / "Csf_AAPU790804II9.pdf").read_bytes() == _PDF


def test_save_into_a_directory_without_filename_uses_the_default(tmp_path) -> None:  # type: ignore[no-untyped-def]
    pdf = CsfPdf.new_from_contents(_PDF)

    pdf.save(str(tmp_path))

    assert (tmp_path / "constancia.pdf").read_bytes() == _PDF


def test_save_into_a_directory_sanitizes_the_filename(tmp_path) -> None:  # type: ignore[no-untyped-def]
    pdf = CsfPdf.new_from_contents(_PDF, filename="../../evil.pdf")

    pdf.save(str(tmp_path))

    assert (tmp_path / "evil.pdf").read_bytes() == _PDF
    assert not (tmp_path.parent / "evil.pdf").exists()


def test_new_from_path_reads_and_validates(tmp_path) -> None:  # type: ignore[no-untyped-def]
    path = tmp_path / "Csf_AAPU790804II9.pdf"
    path.write_bytes(_PDF)

    pdf = CsfPdf.new_from_path(str(path))

    assert pdf.as_bytes() == _PDF
    assert pdf.filename == "Csf_AAPU790804II9.pdf"


def test_new_from_missing_path_raises() -> None:
    with pytest.raises(InvalidPdfException):
        CsfPdf.new_from_path("/no/existe/constancia.pdf")
