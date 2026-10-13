"""Cliente para consultar los datos fiscales en el validador del SAT."""

import ssl
from typing import ClassVar, Self

import httpx

from csf_scraper.data_extractor import DataExtractor
from csf_scraper.exceptions import CifDownloadException
from csf_scraper.exceptions.image_reader import ImageReaderNotConfiguredException
from csf_scraper.image_readers.ports.image_reader_port import ImageReaderPort
from csf_scraper.pdf_reader import PdfCsfTextReader, PdfToText
from csf_scraper.persona_fisica import PersonaFisica
from csf_scraper.persona_moral import PersonaMoral
from csf_scraper.value_objects.csf_image import CsfImage
from csf_scraper.value_objects.id_cif import IdCif
from csf_scraper.value_objects.rfc import Rfc


def _create_ssl_context() -> ssl.SSLContext:
    context = ssl.create_default_context()
    context.set_ciphers("DEFAULT@SECLEVEL=1")
    return context


class Scraper:
    """Obtiene una :class:`PersonaMoral` o :class:`PersonaFisica` desde el sitio del SAT."""

    url: ClassVar[str] = (
        "https://siat.sat.gob.mx/app/qr/faces/pages/mobile/validadorqr.jsf?D1=10&D2=1&D3=%s_%s"
    )

    def __init__(
        self, client: httpx.Client, image_reader: ImageReaderPort | None = None
    ) -> None:
        self.client = client
        #: Motor de lectura de imágenes (LLM/OCR); opcional, por defecto solo PDF.
        self.image_reader = image_reader

    @classmethod
    def create(cls, image_reader: ImageReaderPort | None = None) -> Self:
        """Crea un cliente HTTP listo para usar contra el SAT."""
        return cls(
            httpx.Client(
                follow_redirects=True, timeout=None, verify=_create_ssl_context()
            ),
            image_reader=image_reader,
        )

    def obtain_from_rfc_and_cif(
        self, rfc: str, id_cif: str
    ) -> PersonaMoral | PersonaFisica:
        """Obtiene la persona a partir de su RFC y su idCIF."""
        parsed_rfc = Rfc(rfc)
        parsed_cif = IdCif(id_cif)

        uri = type(self).url % (parsed_cif, parsed_rfc)
        html = self._obtain_html(uri)
        person = DataExtractor(html).extract(is_fisica=parsed_rfc.is_fisica())

        person.rfc = parsed_rfc
        person.id_cif = parsed_cif
        return person

    def obtain_from_pdf_path(self, path: str) -> PersonaMoral | PersonaFisica:
        """Obtiene la persona leyendo su RFC e idCIF de una CSF en PDF."""
        data = PdfCsfTextReader(self._pdf_to_text_content(path)).extract()
        return self.obtain_from_rfc_and_cif(data.rfc, data.id_cif)

    def obtain_from_image_path(self, path: str) -> PersonaMoral | PersonaFisica:
        """Obtiene la persona leyendo su RFC e idCIF de una CSF escaneada (JPEG/PNG)."""
        if self.image_reader is None:
            raise ImageReaderNotConfiguredException()
        data = self.image_reader.read(CsfImage.new_from_path(path))
        return self.obtain_from_rfc_and_cif(data.rfc, data.id_cif)

    def _pdf_to_text_content(self, path: str) -> str:
        return PdfToText().extract(path)

    def _obtain_html(self, uri: str) -> str:
        try:
            response = self.client.get(uri)
            response.raise_for_status()
        except httpx.HTTPError as exception:
            raise CifDownloadException(uri) from exception
        return response.text
