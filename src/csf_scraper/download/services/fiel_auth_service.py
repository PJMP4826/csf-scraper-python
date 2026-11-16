"""Autenticación FIEL contra el portal del SAT.

Flujo tomado de ``SATPortalConstancia.login()`` + ``PortalManager.fiel_login()``
de ``SAT-CFDI/python-satcfdi``:

1. GET ``/nidp/idff/sso?id=fiel_Aviso``.
2. Seguir los formularios intermedios de auto-envío hasta llegar a la página
   que contiene ``certform`` (con un cliente nuevo el SAT sirve primero un
   formulario vacío que el navegador autoenvía por JavaScript).
3. Enviar ``certform`` con el token FIEL (``generate_token``) y la fecha de
   vencimiento del certificado.

El formulario visible de archivos (``<form role="form">``) es solo del lado
cliente: el navegador calcula el token con JavaScript y hace
``certform.submit()``. Por eso aquí se prefiere ``certform`` en cuanto
aparece y no se envía el formulario de archivos.
"""

import contextlib

import httpx

from csf_scraper.download.exceptions import SatFormNotFoundException, SatLoginException
from csf_scraper.download.form_utils import FormExtractionResult, extract_form
from csf_scraper.download.ports.auth_port import AuthPort
from csf_scraper.download.ports.signer_port import SignerPort
from csf_scraper.download.services._portal import get_url, post_form
from csf_scraper.download.services.token_service import generate_token
from csf_scraper.download.urls import LOGIN_BASE_URL, LOGIN_FIEL_SSO_URL, LOGOUT_URL

#: Formularios intermedios de auto-envío que se siguen antes de ``certform``.
_MAX_BOOTSTRAP_FORMS = 3


class FielAuthService(AuthPort):
    """Implementa :class:`AuthPort` con credenciales FIEL (sin CAPTCHA)."""

    def __init__(self, signer: SignerPort) -> None:
        self._signer = signer

    async def login(self, client: httpx.AsyncClient) -> None:
        """Inicia sesión FIEL con el cliente HTTP compartido."""
        response = await get_url(client, LOGIN_FIEL_SSO_URL)
        response, cert_form = await self._reach_cert_form(client, response)
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

    async def _reach_cert_form(
        self, client: httpx.AsyncClient, response: httpx.Response
    ) -> tuple[httpx.Response, FormExtractionResult]:
        """Sigue los formularios de auto-envío hasta encontrar ``certform``."""
        for _ in range(_MAX_BOOTSTRAP_FORMS):
            cert_form = self._find_cert_form(response)
            if cert_form is not None:
                return response, cert_form
            try:
                form = extract_form(response.text, base_url=str(response.url))
            except SatFormNotFoundException as exception:
                raise SatLoginException("The SAT FIEL login page has no form.") from exception
            response = await post_form(
                client, action=form.action, referer_url=str(response.url), data=form.fields
            )
        raise SatLoginException("The SAT FIEL login page has no certform.")

    @staticmethod
    def _find_cert_form(response: httpx.Response) -> FormExtractionResult | None:
        try:
            return extract_form(response.text, base_url=str(response.url), form_id="certform")
        except SatFormNotFoundException:
            return None

    async def logout(self, client: httpx.AsyncClient) -> None:
        """Cierra la sesión y deja el cliente sin cookies.

        El portal responde al logout con la página "Access Manager" pero
        conserva el ``JSESSIONID``; si el cliente se reutiliza, el siguiente
        ``GET fiel_Aviso`` devuelve esa página sin formularios. Vaciar el
        cookie jar deja el cliente listo para un nuevo inicio de sesión.
        """
        with contextlib.suppress(Exception):
            await get_url(client, LOGOUT_URL, referer_url=f"{LOGIN_BASE_URL}/nidp/app?sid=0")
        client.cookies.clear()
