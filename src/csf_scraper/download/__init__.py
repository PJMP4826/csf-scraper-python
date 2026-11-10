"""Descarga de la Constancia de Situación Fiscal desde el portal del SAT.

Módulo de descarga (autenticado con FIEL). La lectura pública de la CSF
—por RFC+idCIF, PDF o imagen— vive en el paquete raíz ``csf_scraper``.
"""

from typing import TYPE_CHECKING

from csf_scraper.download.constancia_downloader import ConstanciaDownloader
from csf_scraper.download.exceptions import (
    ConstanciaNotAvailableException,
    FielCredentialsException,
    InvalidPdfException,
    SatFormNotFoundException,
    SatLoginException,
    SatNetworkException,
    SatSsoException,
)
from csf_scraper.download.form_utils import FormExtractionResult, extract_form
from csf_scraper.download.http import SatHttpClientFactory, create_sat_ssl_context
from csf_scraper.download.ports import AuthPort, ConstanciaDownloaderPort, SignerPort
from csf_scraper.download.services import (
    ConstanciaDocumentService,
    FielAuthService,
    SsoHandler,
    generate_token,
)
from csf_scraper.download.value_objects import CsfPdf, FielCredentials

if TYPE_CHECKING:
    from csf_scraper.download.adapters import Signer

__all__ = [
    "AuthPort",
    "ConstanciaDocumentService",
    "ConstanciaDownloader",
    "ConstanciaDownloaderPort",
    "ConstanciaNotAvailableException",
    "CsfPdf",
    "FielAuthService",
    "FielCredentials",
    "FielCredentialsException",
    "FormExtractionResult",
    "InvalidPdfException",
    "SatFormNotFoundException",
    "SatHttpClientFactory",
    "SatLoginException",
    "SatNetworkException",
    "SatSsoException",
    "Signer",
    "SignerPort",
    "SsoHandler",
    "create_sat_ssl_context",
    "extract_form",
    "generate_token",
]


def __getattr__(name: str) -> object:
    """Resuelve el adaptador FIEL de forma perezosa.

    Así ``from csf_scraper.download import Signer`` sigue funcionando, pero
    solo importa ``cryptography``/``pyOpenSSL`` cuando alguien realmente lo
    pide (extra ``fiel``).
    """
    if name == "Signer":
        from csf_scraper.download.adapters import Signer

        return Signer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
