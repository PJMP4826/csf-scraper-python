import httpx
import pytest

from csf_scraper import (
    CsfImage,
    ImageReaderNotConfiguredException,
    RfcCifData,
    Scraper,
)


def test_create_with_specific_openssl_cipher_list() -> None:
    scraper = Scraper.create()
    assert isinstance(scraper.client, httpx.Client)

    ssl_context = scraper.client._transport._pool._ssl_context
    assert ssl_context is not None
    assert ssl_context.security_level == 1


def test_create_accepts_an_image_reader() -> None:
    reader = _FakeImageReader(RfcCifData(rfc="DIM8701081LA", id_cif="12345678"))

    scraper = Scraper.create(image_reader=reader)

    assert scraper.image_reader is reader


def test_obtain_from_image_path_requires_a_reader() -> None:
    scraper = Scraper(httpx.Client())

    with pytest.raises(ImageReaderNotConfiguredException):
        scraper.obtain_from_image_path("csf.png")


class _FakeImageReader:
    """Estrategia de lectura de imágenes para pruebas."""

    def __init__(self, data: RfcCifData) -> None:
        self.data = data
        self.received: CsfImage | None = None

    def read(self, image: CsfImage) -> RfcCifData:
        self.received = image
        return self.data
