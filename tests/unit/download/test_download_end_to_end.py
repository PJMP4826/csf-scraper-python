"""Flujo completo de descarga con el SAT mockeado (respx)."""

import asyncio

import httpx
import respx
from tests.unit.download._fiel_certs import PASSWORD, make_fiel_key_and_cert

from csf_scraper.download import ConstanciaDownloader, FielCredentials
from csf_scraper.download.http import SatHttpClientFactory
from csf_scraper.download.urls import (
    CONSTANCIA_PDF_URL,
    CONSULTA_TRAMITE_URL,
    LOGIN_FIEL_SSO_URL,
    SAML_ACS_URL,
    SAML_SSO_URL,
    SESSION_BROKER_URL,
)

_SSO_HTML = """<html><body>
<form action="https://login.siat.sat.gob.mx/nidp/app/login?id=fiel" method="post">
  <input type="hidden" name="foo" value="1" />
</form>
</body></html>"""

_CERTFORM_HTML = """<html><body>
<form id="certform" action="https://login.siat.sat.gob.mx/nidp/app/login" method="post">
  <input type="hidden" name="guid" value="guid-e2e" />
</form>
</body></html>"""

_SAML_REQUEST_HTML = f"""<html><body>
<form action="{SAML_SSO_URL}" method="post">
  <input type="hidden" name="SAMLRequest" value="req" />
</form>
</body></html>"""

_SAML_RESPONSE_HTML = f"""<html><body>
<form action="{SAML_ACS_URL}" method="post">
  <input type="hidden" name="SAMLResponse" value="resp" />
</form>
</body></html>"""

_TRAMITE_HTML = f"""<html><body>
<form id="formReimpAcuse" action="{CONSULTA_TRAMITE_URL}" method="post">
  <input type="hidden" name="javax.faces.ViewState" value="vs-e2e" />
</form>
</body></html>"""

_PDF = b"%PDF-1.7\n%constancia e2e\n"


def test_full_download_flow_with_a_real_fiel_signer() -> None:
    certificate, key = make_fiel_key_and_cert()
    credentials = FielCredentials.from_bytes(certificate=certificate, key=key, password=PASSWORD)

    with respx.mock:
        respx.get(LOGIN_FIEL_SSO_URL).mock(return_value=httpx.Response(200, text=_SSO_HTML))
        respx.post("https://login.siat.sat.gob.mx/nidp/app/login?id=fiel").mock(
            return_value=httpx.Response(200, text=_CERTFORM_HTML)
        )
        respx.post("https://login.siat.sat.gob.mx/nidp/app/login").mock(
            return_value=httpx.Response(200, text="ok")
        )
        respx.get(SESSION_BROKER_URL).mock(
            return_value=httpx.Response(200, text=_SAML_REQUEST_HTML)
        )
        respx.post(SAML_SSO_URL).mock(return_value=httpx.Response(200, text=_SAML_RESPONSE_HTML))
        respx.post(SAML_ACS_URL).mock(return_value=httpx.Response(200, text=_TRAMITE_HTML))
        respx.post(CONSULTA_TRAMITE_URL).mock(return_value=httpx.Response(200, text="ok"))
        respx.get(CONSTANCIA_PDF_URL).mock(return_value=httpx.Response(200, content=_PDF))
        logout_route = respx.get(url__regex=r".*logout.*").mock(
            return_value=httpx.Response(200, text="bye")
        )

        async def _run() -> bytes:
            downloader = ConstanciaDownloader.create(
                credentials=credentials, client=SatHttpClientFactory.create()
            )
            async with downloader:
                pdf = await downloader.download()
                return pdf.as_bytes()

        assert asyncio.run(_run()) == _PDF

    assert len(logout_route.calls) == 1
