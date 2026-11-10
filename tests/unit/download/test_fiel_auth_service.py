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

_SSO_HTML = """<html><body>
<form action="https://login.siat.sat.gob.mx/nidp/app/login?id=fiel" method="post">
  <input type="hidden" name="foo" value="1" />
</form>
</body></html>"""

_CERTFORM_HTML = """<html><body>
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


def test_login_sends_the_fiel_token_and_fert() -> None:
    service = FielAuthService(_FakeSigner())

    with respx.mock:
        respx.get(LOGIN_FIEL_SSO_URL).mock(return_value=httpx.Response(200, text=_SSO_HTML))
        respx.post("https://login.siat.sat.gob.mx/nidp/app/login?id=fiel").mock(
            return_value=httpx.Response(200, text=_CERTFORM_HTML)
        )
        cert_route = respx.post("https://login.siat.sat.gob.mx/nidp/app/login").mock(
            return_value=httpx.Response(200, text="ok")
        )

        asyncio.run(service.login(_client()))

    assert len(cert_route.calls) == 1
    body = parse_qs(cert_route.calls[0].request.content.decode())
    expected_token = generate_token(_FakeSigner(), "guid-xyz").decode()
    assert body["token"] == [expected_token]
    assert body["fert"] == ["271110165438Z"]
    assert body["guid"] == ["guid-xyz"]


def test_login_without_certform_raises() -> None:
    service = FielAuthService(_FakeSigner())

    with respx.mock:
        respx.get(LOGIN_FIEL_SSO_URL).mock(return_value=httpx.Response(200, text=_SSO_HTML))
        respx.post("https://login.siat.sat.gob.mx/nidp/app/login?id=fiel").mock(
            return_value=httpx.Response(200, text="<html><body>no certform</body></html>")
        )
        with pytest.raises(SatLoginException):
            asyncio.run(service.login(_client()))


def test_logout_is_best_effort() -> None:
    service = FielAuthService(_FakeSigner())

    with respx.mock:
        respx.get(url__regex=r".*logout.*").mock(return_value=httpx.Response(500, text="err"))
        # No debe lanzar: el logout no puede tapar el error de la descarga.
        asyncio.run(service.logout(_client()))
