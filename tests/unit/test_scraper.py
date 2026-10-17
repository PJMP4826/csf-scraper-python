import asyncio

import httpx
import pytest
import respx

from csf_scraper import (
    CifNotFoundException,
    ImageExtractorNotConfiguredException,
    RfcCifData,
    Scraper,
)
from tests.helpers import file_contents
from tests.integration.helpers import VALIDADOR_URL_REGEX


def test_create_with_specific_openssl_cipher_list() -> None:
    scraper = Scraper.create()
    assert isinstance(scraper.client, httpx.AsyncClient)

    ssl_context = scraper.client._transport._pool._ssl_context
    assert ssl_context is not None
    assert ssl_context.security_level == 1


def test_create_accepts_an_image_extractor() -> None:
    extractor = _FakeExtractor(RfcCifData(rfc="DIM8701081LA", id_cif="12345678"))

    scraper = Scraper.create(image_extractor=extractor)

    assert scraper.image_extractor is extractor


def test_create_accepts_a_pdf_extractor() -> None:
    extractor = _FakeExtractor(RfcCifData(rfc="DIM8701081LA", id_cif="12345678"))

    scraper = Scraper.create(pdf_extractor=extractor)

    assert scraper.pdf_extractor is extractor


def test_obtain_from_image_path_requires_an_extractor() -> None:
    scraper = Scraper(httpx.AsyncClient())

    with pytest.raises(ImageExtractorNotConfiguredException):
        asyncio.run(scraper.obtain_from_image_path("csf.png"))


def test_obtain_from_image_path_delegates_to_the_extractor() -> None:
    extractor = _FakeExtractor(RfcCifData(rfc="DIM8701081LA", id_cif="12345678"))
    scraper = Scraper(httpx.AsyncClient(), image_extractor=extractor)

    with respx.mock:
        respx.get(url__regex=VALIDADOR_URL_REGEX).mock(
            return_value=httpx.Response(200, text=file_contents("error.html")),
        )
        with pytest.raises(CifNotFoundException):
            asyncio.run(scraper.obtain_from_image_path("csf.png"))

    assert extractor.received == "csf.png"


class _FakeExtractor:
    """Estrategia de extracción para pruebas."""

    def __init__(self, data: RfcCifData) -> None:
        self.data = data
        self.received: str | None = None

    async def extract(self, path: str) -> RfcCifData:
        self.received = path
        return self.data
