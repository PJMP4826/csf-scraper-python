import httpx

from csf_scraper import Scraper


def test_create_with_specific_openssl_cipher_list() -> None:
    scraper = Scraper.create()
    assert isinstance(scraper.client, httpx.Client)

    ssl_context = scraper.client._transport._pool._ssl_context
    assert ssl_context is not None
    assert ssl_context.security_level == 1
