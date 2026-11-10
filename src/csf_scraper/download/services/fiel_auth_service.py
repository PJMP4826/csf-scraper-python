"""Autenticación FIEL contra el portal del SAT.

Flujo tomado de ``SATPortalConstancia.login()`` + ``PortalManager.fiel_login()``
de ``SAT-CFDI/python-satcfdi``:

1. GET ``/nidp/idff/sso?id=fiel_Aviso`` y envío del primer formulario.
2. En la página resultante, envío del formulario ``certform`` con el token
   FIEL (``generate_token``) y la fecha de vencimiento del certificado.
"""

import contextlib

import httpx

from csf_scraper.download.exceptions import SatFormNotFoundException, SatLoginException
from csf_scraper.download.form_utils import extract_form
from csf_scraper.download.ports.auth_port import AuthPort
from csf_scraper.download.ports.signer_port import SignerPort
from csf_scraper.download.services._portal import get_url, post_form
from csf_scraper.download.services.token_service import generate_token
from csf_scraper.download.urls import LOGIN_BASE_URL, LOGIN_FIEL_SSO_URL, LOGOUT_URL


class FielAuthService(AuthPort):
    """Implementa :class:`AuthPort` con credenciales FIEL (sin CAPTCHA)."""

    def __init__(self, signer: SignerPort) -> None:
        self._signer = signer

    async def login(self, client: httpx.AsyncClient) -> None:
        """Inicia sesión FIEL con el cliente HTTP compartido."""
        response = await get_url(client, LOGIN_FIEL_SSO_URL)
        try:
            form = extract_form(response.text, base_url=str(response.url))
        except SatFormNotFoundException as exception:
            raise SatLoginException("The SAT FIEL login page has no form.") from exception
        response = await post_form(
            client, action=form.action, referer_url=str(response.url), data=form.fields
        )
        try:
            cert_form = extract_form(response.text, base_url=str(response.url), form_id="certform")
        except SatFormNotFoundException as exception:
            raise SatLoginException("The SAT FIEL login page has no certform.") from exception
        guid = cert_form.fields.get("guid")
        if not guid:
            raise SatLoginException("The SAT certform has no guid.")
        token = generate_token(self._signer, code=guid)
        data = {
            **cert_form.fields,
            "token": token.decode(),
            "fert": self._signer.fert,
        }
        await post_form(client, action=cert_form.action, referer_url=str(response.url), data=data)

    async def logout(self, client: httpx.AsyncClient) -> None:
        """Cierra la sesión; es *best effort* para no tapar el error original."""
        with contextlib.suppress(Exception):
            await get_url(client, LOGOUT_URL, referer_url=f"{LOGIN_BASE_URL}/nidp/app?sid=0")
