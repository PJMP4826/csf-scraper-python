"""Manejo del flujo SSO/SAML del SAT tras el login.

Equivalente a ``SsoHandler`` de ``phpcfdi/csf-sat-scraper`` y a la parte
SAML de ``SATPortalConstancia.generar_constancia()`` de ``satcfdi``:

GET al SessionBroker, envío en cadena de los formularios SAML
(``/nidp/saml2/sso`` → ``/saml2/sp/acs/post``) y, si aparece, seguimiento
del ``<iframe id="iframetoload">`` del flujo CIEC. Se detiene al llegar a
la página de ``ConsultaTramite`` (formulario ``formReimpAcuse``), que es
responsabilidad de :class:`ConstanciaDocumentService`.
"""

import html as html_module
import re

import httpx

from csf_scraper.download.exceptions import SatFormNotFoundException, SatSsoException
from csf_scraper.download.form_utils import extract_form
from csf_scraper.download.services._portal import get_url, post_form
from csf_scraper.download.urls import CONSULTA_TRAMITE_URL, SESSION_BROKER_URL

_IFRAME_PATTERN = re.compile(r'<iframe[^>]+id="iframetoload"[^>]+src="([^"]+)"', re.IGNORECASE)

#: Máximo de formularios SAML a seguir (como el bucle de 10 de satcfdi).
_MAX_SSO_FORMS = 10


class SsoHandler:
    """Sigue el flujo SSO/SAML y devuelve el HTML de la página de trámite."""

    async def handle(
        self, client: httpx.AsyncClient, *, entry_url: str = SESSION_BROKER_URL
    ) -> str:
        """Ejecuta el flujo SSO y devuelve el HTML final (ConsultaTramite)."""
        response = await get_url(client, entry_url)
        html = response.text
        current_url = str(response.url)
        html, current_url = await self._follow_iframe(client, html, current_url)
        for _ in range(_MAX_SSO_FORMS):
            try:
                form = extract_form(html, base_url=current_url)
            except SatFormNotFoundException:
                return html
            if form.action == CONSULTA_TRAMITE_URL:
                return html
            response = await post_form(
                client, action=form.action, referer_url=current_url, data=form.fields
            )
            html = response.text
            current_url = str(response.url)
            html, current_url = await self._follow_iframe(client, html, current_url)
        raise SatSsoException("The SAT SSO workflow did not reach the tramite page.")

    async def _follow_iframe(
        self, client: httpx.AsyncClient, html: str, current_url: str
    ) -> tuple[str, str]:
        match = _IFRAME_PATTERN.search(html)
        if match is None:
            return html, current_url
        iframe_url = html_module.unescape(match.group(1))
        response = await get_url(client, iframe_url, referer_url=current_url)
        return response.text, str(response.url)
