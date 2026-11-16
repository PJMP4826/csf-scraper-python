"""Value object del PDF de la Constancia de Situación Fiscal descargada."""

import hashlib
from pathlib import Path
from typing import Self

from csf_scraper.download.exceptions import InvalidPdfException

#: Cabecera (magic bytes) de todo documento PDF.
_PDF_HEADER = b"%PDF-"

#: Nombre usado cuando el PDF no trae uno propio.
_DEFAULT_FILENAME = "constancia.pdf"


def _safe_filename(filename: str | None) -> str:
    """Reduce ``filename`` a un nombre de archivo seguro.

    Solo se conserva el último componente, se normalizan las barras de
    Windows y se evitan nombres vacíos, ``.`` y ``..``.
    """
    if not filename:
        return _DEFAULT_FILENAME
    name = Path(filename.replace("\\", "/")).name
    return name if name not in {"", ".", ".."} else _DEFAULT_FILENAME


class CsfPdf:
    """PDF de una CSF ya descargado, validado por su cabecera.

    Se construye desde bytes (:meth:`new_from_contents`) o desde una ruta
    (:meth:`new_from_path`); en ambos casos se valida que el contenido
    empiece por ``%PDF-``. Es el equivalente tipado del ``Stringable`` /
    ``StreamInterface`` que devuelve ``phpcfdi/csf-sat-scraper``, pero con
    validación: nunca representa bytes que no son un PDF.
    """

    __slots__ = ("_contents", "_filename")

    def __init__(self, contents: bytes, filename: str | None = None) -> None:
        if not contents:
            raise InvalidPdfException("The downloaded constancia is empty.")
        if not contents.startswith(_PDF_HEADER):
            raise InvalidPdfException(
                "The downloaded content is not a PDF document (expected %PDF- header)."
            )
        self._contents = contents
        self._filename = filename

    @classmethod
    def new_from_contents(cls, contents: bytes, *, filename: str | None = None) -> Self:
        """Valida ``contents`` como PDF y devuelve el value object."""
        return cls(contents, filename)

    @classmethod
    def new_from_path(cls, path: str) -> Self:
        """Lee y valida el PDF en ``path``; conserva su nombre."""
        try:
            contents = Path(path).read_bytes()
        except OSError as exception:
            raise InvalidPdfException(f"Cannot read PDF from path: {path}") from exception
        return cls(contents, Path(path).name)

    def as_bytes(self) -> bytes:
        """Contenido binario del PDF."""
        return self._contents

    @property
    def filename(self) -> str | None:
        """Nombre original del PDF, si se conoce."""
        return self._filename

    def save(self, path: str | Path) -> None:
        """Escribe el PDF en ``path``.

        Si ``path`` es un directorio existente, se guarda dentro con el
        nombre original del PDF (o ``constancia.pdf`` si no se conoce). Si es
        una ruta de archivo, se escribe exactamente ahí.
        """
        destination = Path(path)
        if destination.is_dir():
            destination = destination / _safe_filename(self._filename)
        destination.write_bytes(self._contents)

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
