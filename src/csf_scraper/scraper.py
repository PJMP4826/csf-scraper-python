"""Cliente para consultar los datos fiscales en el validador del SAT."""

import ssl
from types import TracebackType
from typing import ClassVar, Self

import httpx

from csf_scraper.data_extractor import DataExtractor
from csf_scraper.exceptions import CifDownloadException
from csf_scraper.exceptions.image_reader import ImageExtractorNotConfiguredException
from csf_scraper.pdf_reader import CsfPdfExtractor
from csf_scraper.persona_fisica import PersonaFisica
from csf_scraper.persona_moral import PersonaMoral
from csf_scraper.ports import RfcCifExtractorPort
from csf_scraper.value_objects.id_cif import IdCif
from csf_scraper.value_objects.rfc import Rfc


def _create_ssl_context() -> ssl.SSLContext:
    context = ssl.create_default_context()
    context.set_ciphers("DEFAULT@SECLEVEL=1")
    return context


class Scraper:
    """Obtiene una :class:`PersonaMoral` o :class:`PersonaFisica` desde el sitio del SAT.

    Todo el flujo es asíncrono: la descarga usa un
    :class:`httpx.AsyncClient` y la extracción de datos se espera con
    ``await``. El cliente se puede cerrar con :meth:`aclose` o usando el
    scraper como *async context manager*; usar ``async with`` es opcional::

        scraper = Scraper.create()
        try:
            person = await scraper.obtain_from_rfc_and_cif(rfc, id_cif)
        finally:
            await scraper.aclose()

        # Equivalente, cerrando al salir del bloque:
        async with Scraper.create() as scraper:
            person = await scraper.obtain_from_rfc_and_cif(rfc, id_cif)
    """

    url: ClassVar[str] = (
        "https://siat.sat.gob.mx/app/qr/faces/pages/mobile/validadorqr.jsf?D1=10&D2=1&D3=%s_%s"
    )

    def __init__(
        self,
        client: httpx.AsyncClient,
        *,
        pdf_extractor: RfcCifExtractorPort | None = None,
        image_extractor: RfcCifExtractorPort | None = None,
    ) -> None:
        self.client = client
        #: Extractor de CSF en PDF; por omisión usa ``pdftotext``.
        self.pdf_extractor: RfcCifExtractorPort = pdf_extractor or CsfPdfExtractor()
        #: Extractor de CSF escaneada (LLM/OCR); opcional.
        self.image_extractor = image_extractor

    @classmethod
    def create(
        cls,
        *,
        pdf_extractor: RfcCifExtractorPort | None = None,
        image_extractor: RfcCifExtractorPort | None = None,
    ) -> Self:
        """Crea un cliente HTTP asíncrono listo para usar contra el SAT."""
        return cls(
            httpx.AsyncClient(
                follow_redirects=True, timeout=None, verify=_create_ssl_context()
            ),
            pdf_extractor=pdf_extractor,
            image_extractor=image_extractor,
        )

    async def __aenter__(self) -> Self:
        """Permite usar el scraper en un bloque ``async with``."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Cierra el cliente HTTP al salir del bloque ``async with``."""
        await self.aclose()

    async def aclose(self) -> None:
        """Cierra el cliente HTTP subyacente."""
        await self.client.aclose()

    async def obtain_from_rfc_and_cif(
        self, rfc: str, id_cif: str
    ) -> PersonaMoral | PersonaFisica:
        """Obtiene la persona a partir de su RFC y su idCIF."""
        parsed_rfc = Rfc(rfc)
        parsed_cif = IdCif(id_cif)

        uri = type(self).url % (parsed_cif, parsed_rfc)
        html = await self._obtain_html(uri)
        person = DataExtractor(html).extract(is_fisica=parsed_rfc.is_fisica())

        person.rfc = parsed_rfc
        person.id_cif = parsed_cif
        return person

    async def obtain_from_pdf_path(self, path: str) -> PersonaMoral | PersonaFisica:
        """Obtiene la persona leyendo su RFC e idCIF de una CSF en PDF."""
        data = await self.pdf_extractor.extract(path)
        return await self.obtain_from_rfc_and_cif(data.rfc, data.id_cif)

    async def obtain_from_image_path(self, path: str) -> PersonaMoral | PersonaFisica:
        """Obtiene la persona leyendo su RFC e idCIF de una CSF escaneada (JPEG/PNG)."""
        if self.image_extractor is None:
            raise ImageExtractorNotConfiguredException()
        data = await self.image_extractor.extract(path)
        return await self.obtain_from_rfc_and_cif(data.rfc, data.id_cif)

    async def _obtain_html(self, uri: str) -> str:
        try:
            response = await self.client.get(uri)
            response.raise_for_status()
        except httpx.HTTPError as exception:
            raise CifDownloadException(uri) from exception
        return response.text
