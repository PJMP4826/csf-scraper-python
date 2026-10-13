import base64

import pytest

from csf_scraper import (
    CsfImage,
    InvalidImageException,
    InvalidImageFormatException,
)

JPEG_BYTES = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01" + b"jpeg-contents"
PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"png-contents"


def test_detects_jpeg() -> None:
    image = CsfImage.new_from_contents(JPEG_BYTES)
    assert image.get_mime_type() == "image/jpeg"
    assert image.as_bytes() == JPEG_BYTES


def test_detects_png() -> None:
    image = CsfImage.new_from_contents(PNG_BYTES)
    assert image.get_mime_type() == "image/png"


def test_returns_base64_contents() -> None:
    image = CsfImage.new_from_contents(PNG_BYTES)
    assert image.as_base64() == base64.b64encode(PNG_BYTES).decode("ascii")


def test_new_from_path(tmp_path) -> None:
    path = tmp_path / "csf.png"
    path.write_bytes(PNG_BYTES)

    image = CsfImage.new_from_path(str(path))

    assert image.get_mime_type() == "image/png"


def test_rejects_empty_contents() -> None:
    with pytest.raises(InvalidImageException):
        CsfImage.new_from_contents(b"")


def test_rejects_unsupported_format() -> None:
    with pytest.raises(InvalidImageFormatException):
        CsfImage.new_from_contents(b"not an image")


def test_rejects_missing_path() -> None:
    with pytest.raises(InvalidImageException):
        CsfImage.new_from_path("/no/such/file.png")
