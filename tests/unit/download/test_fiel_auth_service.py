import asyncio
import base64
from urllib.parse import parse_qs

import httpx
import pytest
import respx

from csf_scraper.download.exceptions import SatLoginException
from csf_scraper.download.http import SatHttpClientFactory
from csf_scraper.download.services import FielAuthService, generate_token
from csf_scraper.download.urls import LOGIN_FIEL_SSO_URL

_BOOTSTRAP_URL = (
    "https://login.siat.sat.gob.mx/nidp/app/login?id=fiel_Aviso&sid=0&option=credential&sid=0"
)

_BOOTSTRAP_HTML = f"""<html><body>
<form method="POST" action="{_BOOTSTRAP_URL}"></form>
<script>document.forms[0].submit();</script>
</body></html>"""

_CERTFORM_HTML = """<html><body>
<form role="form" method="post">
  <input type="file" name="txtCertificate" />
  <input type="file" name="txtPrivateKey" />
</form>
<form id="certform" action="https://login.siat.sat.gob.mx/nidp/app/login" method="post">
  <input type="hidden" name="guid" value="guid-xyz" />
  <input type="hidden" name="other" value="2" />
</form>
</body></html>"""


class _FakeSigner:
    rfc = "DIM8701081LA"
    certificate_number = "123456"
    fert = "271110165438Z"

    def sign_sha1(self, data: bytes) -> str:
        return base64.b64encode(b"sig:" + data).decode()


def _client() -> httpx.AsyncClient:
    return SatHttpClientFactory.create()


def test_login_sends_the_fiel_token_and_fert_when_certform_is_direct() -> None:
    service = FielAuthService(_FakeSigner())

    with respx.mock:
        respx.get(LOGIN_FIEL_SSO_URL).mock(return_value=httpx.Response(200, text=_CERTFORM_HTML))
        bootstrap_route = respx.post(_BOOTSTRAP_URL).mock(
            return_value=httpx.Response(500, text="should not be called")
        )
        cert_route = respx.post("https://login.siat.sat.gob.mx/nidp/app/login").mock(
            return_value=httpx.Response(200, text="ok")
        )

        asyncio.run(service.login(_client()))

    assert len(bootstrap_route.calls) == 0
    assert len(cert_route.calls) == 1
    body = parse_qs(cert_route.calls[0].request.content.decode())
    expected_token = generate_token(_FakeSigner(), "guid-xyz").decode()
    assert body["token"] == [expected_token]
    assert body["fert"] == ["271110165438Z"]
    assert body["guid"] == ["guid-xyz"]


def test_login_follows_the_bootstrap_form_until_certform() -> None:
    service = FielAuthService(_FakeSigner())

    with respx.mock:
        respx.get(LOGIN_FIEL_SSO_URL).mock(return_value=httpx.Response(200, text=_BOOTSTRAP_HTML))
        bootstrap_route = respx.post(_BOOTSTRAP_URL).mock(
            return_value=httpx.Response(200, text=_CERTFORM_HTML)
        )
        cert_route = respx.post("https://login.siat.sat.gob.mx/nidp/app/login").mock(
            return_value=httpx.Response(200, text="ok")
        )

        asyncio.run(service.login(_client()))

    assert len(bootstrap_route.calls) == 1
    assert len(cert_route.calls) == 1
    body = parse_qs(cert_route.calls[0].request.content.decode())
    assert body["token"] == [generate_token(_FakeSigner(), "guid-xyz").decode()]
    assert body["fert"] == ["271110165438Z"]
    assert body["guid"] == ["guid-xyz"]


def test_login_without_certform_raises() -> None:
    service = FielAuthService(_FakeSigner())

    no_certform_html = """<html><body>
    <form role="form" method="post"><input type="file" name="txtCertificate" /></form>
    </body></html>"""

    with respx.mock:
        respx.get(LOGIN_FIEL_SSO_URL).mock(return_value=httpx.Response(200, text=no_certform_html))
        respx.post(LOGIN_FIEL_SSO_URL).mock(return_value=httpx.Response(200, text=no_certform_html))
        with pytest.raises(SatLoginException):
            asyncio.run(service.login(_client()))


def test_logout_is_best_effort_and_clears_the_cookie_jar() -> None:
    service = FielAuthService(_FakeSigner())
    client = _client()
    client.cookies.set("JSESSIONID", "abc", domain="login.siat.sat.gob.mx", path="/nidp")

    with respx.mock:
        respx.get(url__regex=r".*logout.*").mock(return_value=httpx.Response(500, text="err"))
        # No debe lanzar: el logout no puede tapar el error de la descarga.
        asyncio.run(service.logout(client))

    assert len(client.cookies.jar) == 0
