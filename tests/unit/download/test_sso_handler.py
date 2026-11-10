import asyncio

import httpx
import pytest
import respx

from csf_scraper.download.exceptions import SatSsoException
from csf_scraper.download.http import SatHttpClientFactory
from csf_scraper.download.services import SsoHandler
from csf_scraper.download.urls import (
    CONSULTA_TRAMITE_URL,
    SAML_ACS_URL,
    SAML_SSO_URL,
    SESSION_BROKER_URL,
)

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
  <input type="hidden" name="javax.faces.ViewState" value="vs-1" />
</form>
</body></html>"""


def _client() -> httpx.AsyncClient:
    return SatHttpClientFactory.create()


def test_handle_follows_saml_forms_until_the_tramite_page() -> None:
    handler = SsoHandler()

    with respx.mock:
        respx.get(SESSION_BROKER_URL).mock(
            return_value=httpx.Response(200, text=_SAML_REQUEST_HTML)
        )
        respx.post(SAML_SSO_URL).mock(return_value=httpx.Response(200, text=_SAML_RESPONSE_HTML))
        respx.post(SAML_ACS_URL).mock(return_value=httpx.Response(200, text=_TRAMITE_HTML))

        html = asyncio.run(handler.handle(_client()))

    assert "formReimpAcuse" in html
    assert "vs-1" in html


def test_handle_returns_html_without_forms_as_is() -> None:
    handler = SsoHandler()

    with respx.mock:
        respx.get(SESSION_BROKER_URL).mock(
            return_value=httpx.Response(200, text="<html><body>already here</body></html>")
        )

        assert asyncio.run(handler.handle(_client())) == "<html><body>already here</body></html>"


def test_handle_follows_the_iframe() -> None:
    handler = SsoHandler()
    iframe_url = "https://wwwmat.sat.gob.mx/iframe/page"

    with respx.mock:
        iframe_html = (
            f'<html><body><iframe id="iframetoload" src="{iframe_url}"></iframe></body></html>'
        )
        respx.get(SESSION_BROKER_URL).mock(return_value=httpx.Response(200, text=iframe_html))
        respx.get(iframe_url).mock(return_value=httpx.Response(200, text=_SAML_REQUEST_HTML))
        respx.post(SAML_SSO_URL).mock(return_value=httpx.Response(200, text=_SAML_RESPONSE_HTML))
        respx.post(SAML_ACS_URL).mock(return_value=httpx.Response(200, text=_TRAMITE_HTML))

        html = asyncio.run(handler.handle(_client()))

    assert "formReimpAcuse" in html


def test_handle_raises_after_too_many_sso_forms() -> None:
    handler = SsoHandler()
    loop_html = """<html><body>
    <form action="https://login.siat.sat.gob.mx/nidp/saml2/sso" method="post">
      <input type="hidden" name="SAMLRequest" value="req" />
    </form>
    </body></html>"""

    with respx.mock:
        respx.get(SESSION_BROKER_URL).mock(return_value=httpx.Response(200, text=loop_html))
        respx.post(SAML_SSO_URL).mock(return_value=httpx.Response(200, text=loop_html))

        with pytest.raises(SatSsoException):
            asyncio.run(handler.handle(_client()))
