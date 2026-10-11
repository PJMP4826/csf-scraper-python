"""Helpers de los tests de integración."""

from csf_scraper import Scraper
from tests.helpers import file_contents

#: Expresión regular del URL del validador QR del SAT.
VALIDADOR_URL_REGEX = r"^https://siat\.sat\.gob\.mx/app/qr/faces/pages/mobile/validadorqr\.jsf"


class ScraperHelper(Scraper):
    """Lee ``csf-content.txt`` en vez de llamar a ``pdftotext``."""

    def _pdf_to_text_content(self, path: str) -> str:
        return file_contents("csf-content.txt")
