import httpx

from csf_scraper.download.http import SatHttpClientFactory, create_sat_ssl_context


def test_create_returns_an_async_client_with_sat_defaults() -> None:
    client = SatHttpClientFactory.create()

    assert isinstance(client, httpx.AsyncClient)
    assert client.follow_redirects is True
    assert client.timeout.connect == 10.0
    assert client.timeout.read == 30.0
    assert "Mozilla/5.0" in client.headers["User-Agent"]


def test_create_uses_the_sat_ssl_context() -> None:
    client = SatHttpClientFactory.create()
    ssl_context = client._transport._pool._ssl_context

    assert ssl_context is not None
    assert ssl_context.security_level == 1


def test_create_sat_ssl_context_has_security_level_1() -> None:
    assert create_sat_ssl_context().security_level == 1
