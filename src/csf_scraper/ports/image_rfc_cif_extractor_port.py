"""Puerto de extracción de RFC e idCIF desde una imagen en memoria."""

from abc import ABC, abstractmethod

from csf_scraper.ports.rfc_cif_extractor_port import RfcCifExtractorPort
from csf_scraper.rfc_cif_data import RfcCifData


class ImageRfcCifExtractorPort(RfcCifExtractorPort, ABC):
    """Extiende :class:`RfcCifExtractorPort` para leer imágenes desde bytes.

    Además de :meth:`~RfcCifExtractorPort.extract`, que lee desde una ruta,
    expone :meth:`extract_from_content` para cuando los bytes de la imagen ya
    están en memoria (por ejemplo, una descarga o una API web).
    """

    @abstractmethod
    async def extract_from_content(self, content: bytes) -> RfcCifData:
        """Devuelve el RFC y el idCIF de los bytes de una imagen de CSF."""
        ...
