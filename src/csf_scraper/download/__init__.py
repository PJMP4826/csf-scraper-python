"""Descarga de la Constancia de Situación Fiscal desde el portal del SAT.

Módulo de descarga (autenticado con FIEL). La lectura pública de la CSF
—por RFC+idCIF, PDF o imagen— vive en el paquete raíz ``csf_scraper``.
"""

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
from csf_scraper.download.value_objects import CsfPdf

__all__ = [
    "ConstanciaNotAvailableException",
    "CsfPdf",
    "FielCredentialsException",
    "FormExtractionResult",
    "InvalidPdfException",
    "SatFormNotFoundException",
    "SatHttpClientFactory",
    "SatLoginException",
    "SatNetworkException",
    "SatSsoException",
    "create_sat_ssl_context",
    "extract_form",
]
