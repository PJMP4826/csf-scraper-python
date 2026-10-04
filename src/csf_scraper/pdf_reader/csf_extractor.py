"""Extracción de RFC e idCIF desde el texto de la CSF (``src/PdfReader/CsfExtractor.php``)."""

from csf_scraper.exceptions.pdf_reader import EmptyPdfContentException
from csf_scraper.text_utils import php_trim


class CsfExtractor:
    """Obtiene el RFC y el idCIF de las líneas de texto de una CSF.

    Equivalente a ``PhpCfdi\\CsfScraper\\PdfReader\\CsfExtractor``
    (clase ``final readonly`` marcada como ``@internal``).
    """

    def __init__(self, contents: str) -> None:
        if contents == "":
            raise EmptyPdfContentException("Cannot read pdf contents.")
        self._lines = contents.split("\n")

    def get_rfc(self) -> str | None:
        """Equivalente a ``getRfc()``: valor tras ``RFC:`` o ``None`` si no existe."""
        return self._obtain_clean_value(self._obtain_first_line_start_with("RFC:"))

    def get_cif_id(self) -> str | None:
        """Equivalente a ``getCifId()``: valor tras ``idCIF:`` o ``None`` si no existe."""
        return self._obtain_clean_value(self._obtain_first_line_start_with("idCIF:"))

    def _obtain_first_line_start_with(self, searchable: str) -> str:
        """Equivalente a ``obtainFirstLineStartWith()``."""
        for line in self._lines:
            if line.startswith(searchable):
                return line
        return ""

    def _obtain_clean_value(self, entry: str) -> str | None:
        """Equivalente a ``obtainCleanValue()``: solo el segmento tras el primer ``:``."""
        values = entry.split(":")
        if len(values) < 2:
            return None
        return php_trim(values[1])
