"""Orquestador de la descarga de la Constancia de Situación Fiscal.

Equivalente en Python async de ``Scraper::download()`` de
``phpcfdi/csf-sat-scraper``: un orquestador fino que encadena los servicios
de un solo paso —autenticación FIEL, SSO/SAML y documento— con el mismo
cliente HTTP compartido, y cierra la sesión siempre, incluso si la
descarga falla (corrección del ``logout()`` fuera de ``finally`` de PHP).
"""

import asyncio
from types import TracebackType
from typing import Self

import httpx

from csf_scraper.download.http.sat_http_client_factory import SatHttpClientFactory
from csf_scraper.download.ports.auth_port import AuthPort
from csf_scraper.download.ports.constancia_downloader_port import ConstanciaDownloaderPort
from csf_scraper.download.services.constancia_document_service import (
    ConstanciaDocumentService,
)
from csf_scraper.download.services.fiel_auth_service import FielAuthService
from csf_scraper.download.services.sso_handler import SsoHandler
from csf_scraper.download.value_objects.csf_pdf import CsfPdf
from csf_scraper.download.value_objects.fiel_credentials import FielCredentials
from csf_scraper.persona_fisica import PersonaFisica
from csf_scraper.persona_moral import PersonaMoral


class ConstanciaDownloader(ConstanciaDownloaderPort):
    """Descarga la CSF en PDF autenticándose con FIEL.

    Uso::

        credentials = FielCredentials.from_files(
            certificate_path="fiel.cer", key_path="fiel.key", password="…")
        async with ConstanciaDownloader.create(credentials=credentials) as downloader:
            pdf = await downloader.download()
            pdf.save("constancia.pdf")
    """

    def __init__(
        self,
        client: httpx.AsyncClient,
        *,
        auth: AuthPort,
        sso_handler: SsoHandler,
        document_service: ConstanciaDocumentService,
    ) -> None:
        self.client = client
        self._auth = auth
        self._sso_handler = sso_handler
        self._document_service = document_service

    @classmethod
    def create(
        cls,
        *,
        credentials: FielCredentials,
        client: httpx.AsyncClient | None = None,
    ) -> Self:
        """Crea el descargador con un firmante FIEL y un cliente del SAT."""
        from csf_scraper.download.adapters import Signer

        signer = Signer.load(credentials)
        return cls(
            client or SatHttpClientFactory.create(),
            auth=FielAuthService(signer),
            sso_handler=SsoHandler(),
            document_service=ConstanciaDocumentService(),
        )

    async def __aenter__(self) -> Self:
        """Permite usar el descargador en un bloque ``async with``."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Cierra el cliente HTTP al salir del bloque ``async with``."""
        await self.aclose()

    async def aclose(self) -> None:
        """Cierra el cliente HTTP subyacente."""
        await self.client.aclose()

    async def download(self) -> CsfPdf:
        """Autentica, sigue el SSO y descarga la constancia como PDF validado."""
        try:
            await self._auth.login(self.client)
            last_html = await self._sso_handler.handle(self.client)
            return await self._document_service.download(self.client, last_html)
        finally:
            await self._auth.logout(self.client)

    async def download_and_parse(self) -> PersonaMoral | PersonaFisica:
        """Descarga la constancia y devuelve la persona que describe.

        Delega la lectura en :class:`~csf_scraper.scraper.Scraper`, así la
        descarga y la lectura siguen siendo dos responsabilidades separadas.
        """
        from csf_scraper.scraper import Scraper

        pdf = await self.download()
        async with Scraper.create() as scraper:
            return await scraper.obtain_from_pdf_bytes(pdf.as_bytes())

    def download_sync(self) -> CsfPdf:
        """Versión síncrona de :meth:`download` para scripts y CLI.

        Solo funciona fuera de un bucle de eventos en ejecución.
        """
        return asyncio.run(self.download())
