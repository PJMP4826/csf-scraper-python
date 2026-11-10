"""Puerto del descargador de la Constancia de Situación Fiscal."""

from abc import ABC, abstractmethod

from csf_scraper.download.value_objects.csf_pdf import CsfPdf


class ConstanciaDownloaderPort(ABC):
    """Descarga la CSF en PDF desde el portal del SAT."""

    @abstractmethod
    async def download(self) -> CsfPdf:
        """Autentica, descarga y devuelve la constancia como :class:`CsfPdf` validado."""
        ...
