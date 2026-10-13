"""DTO con el RFC y el idCIF extraídos de una CSF (PDF o imagen)."""

from pydantic import BaseModel, ConfigDict

from csf_scraper.value_objects.id_cif import IdCif
from csf_scraper.value_objects.rfc import Rfc


class RfcCifData(BaseModel):
    """Par validado de RFC e idCIF obtenido por cualquier extractor."""

    model_config = ConfigDict(validate_assignment=True)

    rfc: Rfc
    id_cif: IdCif
