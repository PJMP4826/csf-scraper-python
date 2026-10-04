"""Port Python de `phpcfdi/csf-scraper <https://github.com/phpcfdi/csf-scraper>`_."""

from csf_scraper.exceptions import (
    CifDownloadException,
    CifNotFoundException,
    CsfScraperException,
)
from csf_scraper.exceptions.pdf_reader import (
    CifFromPdfNotFoundException,
    EmptyPdfContentException,
    PdfToTextConvertException,
    RfcFromPdfNotFoundException,
)

__all__ = [
    "CifDownloadException",
    "CifFromPdfNotFoundException",
    "CifNotFoundException",
    "CsfScraperException",
    "EmptyPdfContentException",
    "PdfToTextConvertException",
    "RfcFromPdfNotFoundException",
]
