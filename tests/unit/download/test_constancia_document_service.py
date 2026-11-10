import asyncio
from urllib.parse import parse_qs

import httpx
import pytest
import respx

from csf_scraper.download.exceptions import ConstanciaNotAvailableException, InvalidPdfException
from csf_scraper.download.http import SatHttpClientFactory
from csf_scraper.download.services import ConstanciaDocumentService
from csf_scraper.download.urls import CONSTANCIA_PDF_URL, CONSULTA_TRAMITE_URL

_TRAMITE_HTML = f"""<html><body>
<form id="formReimpAcuse" action="{CONSULTA_TRAMITE_URL}" method="post">
  <input type="hidden" name="javax.faces.ViewState" value="vs-9" />
  <input type="hidden" name="formReimpAcuse:tipoTramite_input" value="1" />
</form>
</body></html>"""

_PDF = b"%PDF-1.7\n%constancia\n"


def _client() -> httpx.AsyncClient:
    return SatHttpClientFactory.create()


def test_download_sends_the_jsf_form_and_returns_a_validated_pdf() -> None:
    service = ConstanciaDocumentService()

    with respx.mock:
        form_route = respx.post(CONSULTA_TRAMITE_URL).mock(
            return_value=httpx.Response(200, text="ok")
        )
        respx.get(CONSTANCIA_PDF_URL).mock(return_value=httpx.Response(200, content=_PDF))

        pdf = asyncio.run(service.download(_client(), _TRAMITE_HTML))

    assert pdf.as_bytes() == _PDF
    body = parse_qs(form_route.calls[0].request.content.decode())
    assert body["javax.faces.partial.ajax"] == ["true"]
    assert body["javax.faces.source"] == ["formReimpAcuse:j_idt50"]
    assert body["javax.faces.ViewState"] == ["vs-9"]
    assert body["formReimpAcuse:tipoTramite_input"] == ["0"]


def test_download_rejects_a_non_pdf_response() -> None:
    service = ConstanciaDocumentService()

    with respx.mock:
        respx.post(CONSULTA_TRAMITE_URL).mock(return_value=httpx.Response(200, text="ok"))
        respx.get(CONSTANCIA_PDF_URL).mock(
            return_value=httpx.Response(200, content=b"<html>error</html>")
        )

        with pytest.raises(InvalidPdfException):
            asyncio.run(service.download(_client(), _TRAMITE_HTML))


def test_download_without_the_final_form_raises() -> None:
    service = ConstanciaDocumentService()

    with respx.mock, pytest.raises(ConstanciaNotAvailableException):
        asyncio.run(service.download(_client(), "<html><body>no form</body></html>"))
