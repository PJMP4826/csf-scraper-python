"""Value object del PDF de la Constancia de Situación Fiscal descargada."""

import hashlib
from pathlib import Path
from typing import Self

from csf_scraper.download.exceptions import InvalidPdfException

#: Cabecera (magic bytes) de todo documento PDF.
_PDF_HEADER = b"%PDF-"


class CsfPdf:
    """PDF de una CSF ya descargado, validado por su cabecera.

    Se construye desde bytes (:meth:`new_from_contents`) o desde una ruta
    (:meth:`new_from_path`); en ambos casos se valida que el contenido
    empiece por ``%PDF-``. Es el equivalente tipado del ``Stringable`` /
    ``StreamInterface`` que devuelve ``phpcfdi/csf-sat-scraper``, pero con
    validación: nunca representa bytes que no son un PDF.
    """

    __slots__ = ("_contents",)

    def __init__(self, contents: bytes) -> None:
        if not contents:
            raise InvalidPdfException("The downloaded constancia is empty.")
        if not contents.startswith(_PDF_HEADER):
            raise InvalidPdfException(
                "The downloaded content is not a PDF document (expected %PDF- header)."
            )
        self._contents = contents

    @classmethod
    def new_from_contents(cls, contents: bytes) -> Self:
        """Valida ``contents`` como PDF y devuelve el value object."""
        return cls(contents)

    @classmethod
    def new_from_path(cls, path: str) -> Self:
        """Lee y valida el PDF en ``path``."""
        try:
            contents = Path(path).read_bytes()
        except OSError as exception:
            raise InvalidPdfException(f"Cannot read PDF from path: {path}") from exception
        return cls(contents)

    def as_bytes(self) -> bytes:
        """Contenido binario del PDF."""
        return self._contents

    def save(self, path: str) -> None:
        """Escribe el PDF en ``path``."""
        Path(path).write_bytes(self._contents)

    @property
    def size(self) -> int:
        """Tamaño del PDF en bytes."""
        return len(self._contents)

    @property
    def sha256(self) -> str:
        """Huella SHA-256 del contenido, en hexadecimal."""
        return hashlib.sha256(self._contents).hexdigest()

    def __len__(self) -> int:
        return len(self._contents)
