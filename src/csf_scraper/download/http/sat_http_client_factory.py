"""Fábrica del cliente HTTP usado contra el portal del SAT.

Equivalente en Python de ``HttpClientFactory`` de
``phpcfdi/csf-sat-scraper``: defaults listos para el SAT (contexto SSL con
``DEFAULT@SECLEVEL=1``, timeouts, redirecciones, User-Agent de navegador y
jar de cookies propio) y una opción crítica no sobreescribible: el cliente
debe conservar sus cookies entre peticiones, porque la sesión del SAT vive
en ellas.
"""

import ssl

import httpx

#: Tiempo máximo de espera de una petición al SAT, en segundos.
DEFAULT_TIMEOUT_SECONDS = 30.0
#: Tiempo máximo para establecer la conexión, en segundos.
DEFAULT_CONNECT_TIMEOUT_SECONDS = 10.0


def create_sat_ssl_context() -> ssl.SSLContext:
    """Contexto SSL con el nivel de seguridad que aceptan los servidores del SAT."""
    context = ssl.create_default_context()
    context.set_ciphers("DEFAULT@SECLEVEL=1")
    return context


class SatHttpClientFactory:
    """Crea clientes ``httpx.AsyncClient`` listos para usar contra el SAT."""

    @staticmethod
    def create(
        *,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        connect_timeout: float = DEFAULT_CONNECT_TIMEOUT_SECONDS,
        trust_env: bool = False,
    ) -> httpx.AsyncClient:
        """Devuelve un cliente asíncrono con cookies, timeouts y SSL del SAT.

        ``trust_env`` es ``False`` por omisión: el cliente no usa los proxies
        del entorno, para que la sesión autenticada (FIEL) no se filtre por
        un proxy ambiente ni dependa de variables como ``NO_PROXY``.
        """
        return httpx.AsyncClient(
            follow_redirects=True,
            timeout=httpx.Timeout(timeout, connect=connect_timeout),
            verify=create_sat_ssl_context(),
            trust_env=trust_env,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/147.0.0.0 Safari/537.36"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;q=0.9,"
                    "image/avif,image/webp,image/apng,*/*;q=0.8"
                ),
                "Accept-Language": "es-MX,es;q=0.9,en;q=0.7",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            },
        )
