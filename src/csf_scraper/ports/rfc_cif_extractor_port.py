"""Puerto que unifica la extracción de RFC e idCIF de una CSF desde una ruta."""

from abc import ABC, abstractmethod

from csf_scraper.rfc_cif_data import RfcCifData


class RfcCifExtractorPort(ABC):
    """Extrae el :class:`RfcCifData` de una Constancia de Situación Fiscal.

    Contrato público de los adaptadores que leen una CSF *desde una ruta*
    (PDF, imagen o cualquier formato futuro). ``Scraper`` solo depende de este
    puerto, así que todos los adaptadores son intercambiables entre sí.

    Reglas del contrato:

    - La ruta se recibe en :meth:`extract`, **no** en el constructor: los
      adaptadores son sin estado y reutilizables entre archivos.
    - El constructor se reserva a la configuración del motor (credenciales,
      modelo, binarios o dependencias inyectadas).
    - El adaptador valida y devuelve :class:`RfcCifData` con los value objects
      ya construidos (``rfc: Rfc``, ``id_cif: IdCif``); nunca cadenas crudas.
    - Los fallos se reportan con subclases de
      :class:`~csf_scraper.exceptions.CsfScraperException`; no se filtran
      errores del motor ni de validación de terceros.

    Implementaciones: :class:`~csf_scraper.pdf_reader.CsfPdfExtractor` (texto
    del PDF) y :class:`~csf_scraper.image_readers.CsfImageExtractor` (cualquier
    :class:`~csf_scraper.image_readers.ports.ImageReaderPort`).

    El contrato es **asíncrono**: ``extract`` es una corrutina para que las
    implementaciones puedan delegar E/S (procesos, disco, red) sin bloquear el
    bucle de eventos. ``Scraper`` la consume con ``await``.
    """

    @abstractmethod
    async def extract(self, path: str) -> RfcCifData:
        """Devuelve el RFC y el idCIF leídos del archivo en ``path``."""
        ...
