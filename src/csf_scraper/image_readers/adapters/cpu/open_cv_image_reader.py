import asyncio
import re

import cv2
import numpy as np

from csf_scraper.exceptions.image_reader import ImageReadingException
from csf_scraper.image_readers.adapters.cpu.open_cv.errors import ImageLoadError
from csf_scraper.image_readers.adapters.cpu.open_cv.pipeline import scan_array
from csf_scraper.image_readers.ports.image_reader_port import ImageReaderPort
from csf_scraper.rfc_cif_data import RfcCifData
from csf_scraper.value_objects.csf_image import CsfImage
from csf_scraper.value_objects.id_cif import IdCif
from csf_scraper.value_objects.rfc import Rfc


class OpenCvImageReader(ImageReaderPort):
    ID_CIF_RFC_PATTERN = r"D3=(\d+)_([A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3})"

    def __init__(self) -> None:
        super().__init__()

    def _decode_image(self, image: bytes | bytearray | memoryview) -> np.ndarray:
        if not isinstance(image, (bytes, bytearray, memoryview)):
            raise TypeError("image must be bytes")
        if len(image) == 0:
            raise ImageLoadError("image cannot be empty")

        buffer = np.frombuffer(image, dtype=np.uint8)
        decoded = cv2.imdecode(buffer, cv2.IMREAD_COLOR)

        if decoded is None:
            raise ImageLoadError("could not decode image bytes")
        return decoded

    def _parse_id_cif_and_rfc(self, url: str) -> tuple[str, str]:
        coincidence = re.search(self.ID_CIF_RFC_PATTERN, url)

        if coincidence:
            id_cif = coincidence.group(1)
            rfc = coincidence.group(2)
            return (id_cif, rfc)
        raise ValueError("No se encontraron los datos en la URL.")

    async def read(self, image: CsfImage) -> RfcCifData:
        decoded = await asyncio.to_thread(self._decode_image, image.as_bytes())
        result = await asyncio.to_thread(scan_array, decoded)

        if not result.qr_code:
            raise ImageReadingException(
                "No fue posible leer el codigo QR, verifique la calidad de la imagen"
            )

        id_cif, rfc = self._parse_id_cif_and_rfc(result.qr_code)

        return RfcCifData(id_cif=IdCif(id_cif), rfc=Rfc(rfc))
