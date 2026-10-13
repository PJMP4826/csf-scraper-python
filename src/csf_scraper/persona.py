"""Modelo base para los datos fiscales de una persona."""

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field

from csf_scraper.date_parser import DateField
from csf_scraper.regimen import Regimen
from csf_scraper.value_objects.id_cif import IdCif
from csf_scraper.value_objects.rfc import Rfc


class Persona(BaseModel):
    """Datos fiscales comunes a una persona moral o física."""

    model_config = ConfigDict(validate_assignment=True)

    rfc: Rfc | None = None
    id_cif: IdCif | None = None
    fecha_inicio_operaciones: DateField = None
    situacion_contribuyente: str = ""
    fecha_ultimo_cambio_situacion: DateField = None
    entidad_federativa: str = ""
    municipio_delegacion: str = ""
    colonia: str = ""
    tipo_vialidad: str = ""
    nombre_vialidad: str = ""
    numero_exterior: str = ""
    numero_interior: str = ""
    codigo_postal: str = ""
    correo_electronico: str = ""
    al: str = ""
    regimenes: list[Regimen] = Field(default_factory=list)
    extra_data: dict[str, Any] = Field(default_factory=dict)

    #: Títulos del HTML que se buscan y el campo (o clave de ``extra_data``) que alimentan.
    field_titles: ClassVar[dict[str, str]] = {
        "fecha_inicio_operaciones": "Fecha de Inicio de operaciones:",
        "situacion_contribuyente": "Situación del contribuyente:",
        "fecha_ultimo_cambio_situacion": "Fecha del último cambio de situación:",
        "entidad_federativa": "Entidad Federativa:",
        "municipio_delegacion": "Municipio o delegación:",
        "colonia": "Colonia:",
        "localidad": "Localidad:",
        "tipo_vialidad": "Tipo de vialidad:",
        "nombre_vialidad": "Nombre de la vialidad:",
        "numero_exterior": "Número exterior:",
        "numero_interior": "Número interior:",
        "codigo_postal": "CP:",
        "correo_electronico": "Correo electrónico:",
        "al": "AL:",
    }

    def is_fisica(self) -> bool:
        """Indica si la persona es física (RFC de 13 caracteres)."""
        return self.rfc.is_fisica() if self.rfc is not None else False

    def is_moral(self) -> bool:
        """Indica si la persona es moral (RFC de 12 caracteres)."""
        return self.rfc.is_moral() if self.rfc is not None else False

    def to_dict(self) -> dict[str, Any]:
        """Devuelve los datos como un diccionario plano (envoltura de :meth:`model_dump`)."""
        return self.model_dump()
