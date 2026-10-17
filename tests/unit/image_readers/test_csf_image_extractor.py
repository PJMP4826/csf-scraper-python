"""Pruebas del puente entre ruta de archivo y motor de lectura de imágenes."""

import asyncio

import pytest

from csf_scraper import (
    CsfImage,
    CsfImageExtractor,
    InvalidImageFormatException,
    RfcCifData,
)

PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"png-contents"


def test_reads_the_image_from_the_path(tmp_path) -> None:
    path = tmp_path / "csf.png"
    path.write_bytes(PNG_BYTES)
    reader = _FakeImageReader(RfcCifData(rfc="DIM8701081LA", id_cif="12345678"))

    data = asyncio.run(CsfImageExtractor(reader).extract(str(path)))

    assert reader.received is not None
    assert reader.received.as_bytes() == PNG_BYTES
    assert data.rfc == "DIM8701081LA"


def test_validates_the_image_format(tmp_path) -> None:
    path = tmp_path / "csf.txt"
    path.write_bytes(b"not an image")

    with pytest.raises(InvalidImageFormatException):
        asyncio.run(
            CsfImageExtractor(
                _FakeImageReader(RfcCifData(rfc="DIM8701081LA", id_cif="12345678"))
            ).extract(str(path))
        )


def test_propagates_reader_errors(tmp_path) -> None:
    path = tmp_path / "csf.png"
    path.write_bytes(PNG_BYTES)

    with pytest.raises(ValueError):
        asyncio.run(CsfImageExtractor(_ExplodingReader()).extract(str(path)))


class _FakeImageReader:
    def __init__(self, data: RfcCifData) -> None:
        self.data = data
        self.received: CsfImage | None = None

    async def read(self, image: CsfImage) -> RfcCifData:
        self.received = image
        return self.data


class _ExplodingReader:
    async def read(self, image: CsfImage) -> RfcCifData:
        raise ValueError("reader failed")
