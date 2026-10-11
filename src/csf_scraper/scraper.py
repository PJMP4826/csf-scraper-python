"""Cliente para consultar los datos fiscales en el validador del SAT."""

import ssl
from typing import ClassVar, Self

import httpx
from stdnum.mx import rfc as mx_rfc

from csf_scraper.data_extractor import DataExtractor
from csf_scraper.exceptions import CifDownloadException
from csf_scraper.exceptions.pdf_reader import (
    CifFromPdfNotFoundException,
    RfcFromPdfNotFoundException,
)
from csf_scraper.pdf_reader import CsfExtractor, PdfToText
from csf_scraper.persona_fisica import PersonaFisica
from csf_scraper.persona_moral import PersonaMoral


def _create_ssl_context() -> ssl.SSLContext:
    context = ssl.create_default_context()
    context.set_ciphers("DEFAULT@SECLEVEL=1")
    return context


class Scraper:
    """Obtiene una :class:`PersonaMoral` o :class:`PersonaFisica` desde el sitio del SAT."""

    url: ClassVar[str] = (
        "https://siat.sat.gob.mx/app/qr/faces/pages/mobile/validadorqr.jsf?D1=10&D2=1&D3=%s_%s"
    )

    def __init__(self, client: httpx.Client) -> None:
        self.client = client

    @classmethod
    def create(cls) -> Self:
        """Crea un cliente HTTP listo para usar contra el SAT."""
        return cls(
            httpx.Client(follow_redirects=True, timeout=None, verify=_create_ssl_context()),
        )

    def obtain_from_rfc_and_cif(self, rfc: str, id_cif: str) -> PersonaMoral | PersonaFisica:
        """Obtiene la persona a partir de su RFC y su idCIF."""
        parsed_rfc = rfc.strip()
        mx_rfc.validate(parsed_rfc)

        uri = type(self).url % (id_cif, parsed_rfc)
        html = self._obtain_html(uri)
        person = DataExtractor(html).extract(is_fisica=len(parsed_rfc) == 13)

        person.rfc = parsed_rfc
        person.id_cif = id_cif
        return person

    def obtain_from_pdf_path(self, path: str) -> PersonaMoral | PersonaFisica:
        """Obtiene la persona leyendo su RFC e idCIF de una CSF en PDF."""
        extractor = CsfExtractor(self._pdf_to_text_content(path))
        rfc = extractor.get_rfc()
        cif = extractor.get_cif_id()

        if rfc is None:
            raise RfcFromPdfNotFoundException("Cannot obtain rfc from given PDF")
        if cif is None:
            raise CifFromPdfNotFoundException("Cannot obtain cif from given PDF")
        return self.obtain_from_rfc_and_cif(rfc, cif)

    def _pdf_to_text_content(self, path: str) -> str:
        return PdfToText().extract(path)

    def _obtain_html(self, uri: str) -> str:
        try:
            response = self.client.get(uri)
            response.raise_for_status()
        except httpx.HTTPError as exception:
            raise CifDownloadException(uri) from exception
        return response.text
