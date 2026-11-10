import asyncio

import httpx
import pytest

from csf_scraper.download import ConstanciaDownloader
from csf_scraper.download.http import SatHttpClientFactory
from csf_scraper.download.value_objects import CsfPdf

_PDF = b"%PDF-1.7\n%constancia\n"


class _FakeAuth:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def login(self, client: httpx.AsyncClient) -> None:
        self.calls.append("login")

    async def logout(self, client: httpx.AsyncClient) -> None:
        self.calls.append("logout")


class _FakeSso:
    def __init__(self, html: str = "<html>tramite</html>") -> None:
        self.html = html
        self.calls: list[str] = []

    async def handle(self, client: httpx.AsyncClient) -> str:
        self.calls.append("handle")
        return self.html


class _FakeDocument:
    def __init__(self, pdf: CsfPdf | None = None, *, fail: bool = False) -> None:
        self.pdf = pdf or CsfPdf.new_from_contents(_PDF)
        self.fail = fail
        self.received_html: str | None = None

    async def download(self, client: httpx.AsyncClient, last_html: str) -> CsfPdf:
        self.received_html = last_html
        if self.fail:
            raise RuntimeError("SAT exploded")
        return self.pdf


def _downloader(auth=None, sso=None, document=None) -> ConstanciaDownloader:  # type: ignore[no-untyped-def]
    return ConstanciaDownloader(
        SatHttpClientFactory.create(),
        auth=auth or _FakeAuth(),
        sso_handler=sso or _FakeSso(),
        document_service=document or _FakeDocument(),
    )


def test_download_runs_login_sso_document_and_logout_in_order() -> None:
    auth, sso, document = _FakeAuth(), _FakeSso(), _FakeDocument()
    downloader = _downloader(auth, sso, document)

    pdf = asyncio.run(downloader.download())

    assert pdf.as_bytes() == _PDF
    assert document.received_html == "<html>tramite</html>"
    assert auth.calls == ["login", "logout"]
    assert sso.calls == ["handle"]


def test_download_logs_out_even_when_the_document_fails() -> None:
    auth = _FakeAuth()
    downloader = _downloader(auth, _FakeSso(), _FakeDocument(fail=True))

    with pytest.raises(RuntimeError, match="SAT exploded"):
        asyncio.run(downloader.download())

    assert auth.calls == ["login", "logout"]


def test_download_sync_runs_the_async_flow() -> None:
    downloader = _downloader()

    pdf = downloader.download_sync()

    assert pdf.as_bytes() == _PDF


def test_downloader_closes_its_client_as_an_async_context_manager() -> None:
    async def _run() -> None:
        async with _downloader() as downloader:
            assert isinstance(downloader.client, httpx.AsyncClient)
            client = downloader.client
        assert client.is_closed

    asyncio.run(_run())
