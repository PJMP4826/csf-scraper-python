import asyncio

import httpx
import respx

from csf_scraper.download.http import SatHttpClientFactory
from tests.helpers import file_contents
from tests.integration.helpers import VALIDADOR_URL_REGEX, ScraperHelper


@respx.mock
def test_obtain_from_pdf_bytes_reads_the_person_from_memory() -> None:
    respx.get(url__regex=VALIDADOR_URL_REGEX).mock(
        return_value=httpx.Response(200, text=file_contents("scrap_moral.html")),
    )
    scraper = ScraperHelper(SatHttpClientFactory.create())

    person = asyncio.run(scraper.obtain_from_pdf_bytes(b"%PDF-1.7\n%fake\n"))

    assert person.is_moral()
    assert person.razon_social == "Mi razón social"
    assert str(person.rfc) == "DIM8701081LA"
