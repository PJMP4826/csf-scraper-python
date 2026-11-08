"""Puente entre una imagen de CSF y un motor de lectura de imágenes."""

import asyncio

from csf_scraper.image_readers.ports.image_reader_port import ImageReaderPort
from csf_scraper.ports.image_rfc_cif_extractor_port import ImageRfcCifExtractorPort
from csf_scraper.rfc_cif_data import RfcCifData
from csf_scraper.value_objects.csf_image import CsfImage


class CsfImageExtractor(ImageRfcCifExtractorPort):
    """Implementa :class:`ImageRfcCifExtractorPort` con un motor de lectura.

    Construye una :class:`CsfImage` desde una ruta (:meth:`extract`) o desde
    bytes (:meth:`extract_from_content`), la valida y delega en el
    :class:`~csf_scraper.image_readers.ports.ImageReaderPort` inyectado. Sirve
    para cualquier motor (LLM u OCR) y así todos los extractores de imagen
    comparten el mismo contrato público.

    La lectura del archivo se hace con :func:`asyncio.to_thread` para no
    bloquear el bucle de eventos, y el motor se espera con ``await``.
    """

    def __init__(self, reader: ImageReaderPort) -> None:
        self._reader = reader

    async def extract(self, path: str) -> RfcCifData:
        """Devuelve el RFC y el idCIF de la imagen de CSF en ``path``."""
        image = await asyncio.to_thread(CsfImage.new_from_path, path)
        return await self._reader.read(image)

    async def extract_from_content(self, content: bytes) -> RfcCifData:
        """Devuelve el RFC y el idCIF de los bytes de una imagen de CSF."""
        image = await asyncio.to_thread(CsfImage.new_from_contents, content)
        return await self._reader.read(image)
