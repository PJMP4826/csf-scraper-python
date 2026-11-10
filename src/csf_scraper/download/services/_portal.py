"""Ayudantes HTTP internos para los servicios del portal del SAT.

Equivalente a ``PortalManager.form()`` de ``satcfdi``: cada POST de
formulario lleva ``Origin`` y ``Referer`` derivados de la URL actual, y los
errores de transporte se traducen a :class:`SatNetworkException`.
"""

from urllib.parse import urlparse, urlunparse

import httpx

from csf_scraper.download.exceptions import SatNetworkException


def _origin_and_referer(url: str) -> dict[str, str]:
    parts = urlparse(url)
    origin = urlunparse((parts.scheme, parts.netloc, "", "", "", ""))
    return {"Origin": origin, "Referer": url}


async def post_form(
    client: httpx.AsyncClient, *, action: str, referer_url: str, data: dict[str, str]
) -> httpx.Response:
    """Envía un formulario POST con las cabeceras que exige el SAT."""
    try:
        response = await client.post(action, headers=_origin_and_referer(referer_url), data=data)
        response.raise_for_status()
    except httpx.HTTPError as exception:
        raise SatNetworkException(action) from exception
    return response


async def get_url(
    client: httpx.AsyncClient, url: str, *, referer_url: str | None = None
) -> httpx.Response:
    """GET con ``Referer`` opcional; traduce errores de red."""
    headers = _origin_and_referer(referer_url) if referer_url else {}
    try:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
    except httpx.HTTPError as exception:
        raise SatNetworkException(url) from exception
    return response
