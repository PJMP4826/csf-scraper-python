"""Value object de una CSF escaneada como imagen (JPEG o PNG)."""

import base64
from pathlib import Path
from typing import Self

from csf_scraper.exceptions.image_reader import (
    InvalidImageException,
    InvalidImageFormatException,
)

#: Firmas (magic bytes) de los formatos de imagen soportados.
_MIME_TYPES: dict[bytes, str] = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
}


class CsfImage:
    """Imagen de una Constancia de Situación Fiscal en formato JPEG o PNG.

    Se construye desde una ruta (:meth:`new_from_path`) o desde bytes
    (:meth:`new_from_contents`); en ambos casos se valida el formato por sus
    *magic bytes* y se determina su tipo MIME.
    """

    __slots__ = ("_contents", "_mime_type")

    def __init__(self, contents: bytes, mime_type: str) -> None:
        self._contents = contents
        self._mime_type = mime_type

    @classmethod
    def new_from_path(cls, path: str) -> Self:
        """Lee y valida la imagen en ``path``; lanza :class:`InvalidImageException`."""
        try:
            contents = Path(path).read_bytes()
        except OSError as exception:
            raise InvalidImageException(
                f"Cannot read image from path: {path}"
            ) from exception
        return cls.new_from_contents(contents)

    @classmethod
    def new_from_contents(cls, contents: bytes) -> Self:
        """Valida ``contents`` como imagen soportada y detecta su tipo MIME."""
        if not contents:
            raise InvalidImageException("The image is empty.")
        return cls(contents, cls._detect_mime_type(contents))

    @staticmethod
    def _detect_mime_type(contents: bytes) -> str:
        for signature, mime_type in _MIME_TYPES.items():
            if contents.startswith(signature):
                return mime_type
        raise InvalidImageFormatException(
            "The given file is not a supported image (expected JPEG or PNG).",
        )

    def as_bytes(self) -> bytes:
        """Contenido binario de la imagen."""
        return self._contents

    def as_base64(self) -> str:
        """Contenido de la imagen codificado en base64."""
        return base64.b64encode(self._contents).decode("ascii")

    def get_mime_type(self) -> str:
        """Tipo MIME detectado (``image/jpeg`` o ``image/png``)."""
        return self._mime_type
