"""Extracción del RFC y el idCIF a partir del texto de una CSF."""

from csf_scraper.exceptions.pdf_reader import (
    CifFromPdfNotFoundException,
    EmptyPdfContentException,
    RfcFromPdfNotFoundException,
)
from csf_scraper.rfc_cif_data import RfcCifData
from csf_scraper.value_objects.id_cif import IdCif
from csf_scraper.value_objects.rfc import Rfc


class PdfCsfTextReader:
    """Obtiene el RFC y el idCIF de las líneas de texto de una CSF (salida de ``pdftotext``)."""

    def __init__(self, contents: str) -> None:
        if not contents:
            raise EmptyPdfContentException("Cannot read pdf contents.")
        self._lines = contents.split("\n")

    def get_rfc(self) -> str | None:
        """RFC encontrado tras la etiqueta ``RFC:``, o ``None`` si no existe."""
        return self._clean_value(self._first_line_starting_with("RFC:"))

    def get_cif_id(self) -> str | None:
        """idCIF encontrado tras la etiqueta ``idCIF:``, o ``None`` si no existe."""
        return self._clean_value(self._first_line_starting_with("idCIF:"))

    def extract(self) -> RfcCifData:
        """Devuelve el RFC y el idCIF validados de la CSF en texto."""
        rfc = self.get_rfc()
        cif = self.get_cif_id()

        if rfc is None:
            raise RfcFromPdfNotFoundException("Cannot obtain rfc from given PDF")
        if cif is None:
            raise CifFromPdfNotFoundException("Cannot obtain cif from given PDF")
        return RfcCifData(rfc=Rfc(rfc), id_cif=IdCif(cif))

    def _first_line_starting_with(self, prefix: str) -> str:
        return next((line for line in self._lines if line.startswith(prefix)), "")

    @staticmethod
    def _clean_value(entry: str) -> str | None:
        parts = entry.split(":")
        if len(parts) < 2:
            return None
        return parts[1].strip()
