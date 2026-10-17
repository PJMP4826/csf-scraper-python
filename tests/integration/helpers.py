"""Helpers de los tests de integración."""

from csf_scraper import CsfPdfExtractor, Scraper
from tests.helpers import file_contents

#: Expresión regular del URL del validador QR del SAT.
VALIDADOR_URL_REGEX = r"^https://siat\.sat\.gob\.mx/app/qr/faces/pages/mobile/validadorqr\.jsf"


class _FixtureTextProvider:
    """Proveedor de texto que devuelve un fixture en vez de llamar a ``pdftotext``."""

    async def extract(self, path: str) -> str:
        return file_contents("csf-content.txt")


class ScraperHelper(Scraper):
    """Lee ``csf-content.txt`` en vez de llamar a ``pdftotext``."""

    def __init__(self, client, **kwargs: object) -> None:  # type: ignore[no-untyped-def]
        super().__init__(
            client,
            pdf_extractor=CsfPdfExtractor(_FixtureTextProvider()),
            **kwargs,  # type: ignore[arg-type]
        )
