"""Modelo de persona física."""

from typing import ClassVar

from csf_scraper.date_parser import DateField
from csf_scraper.persona import Persona


class PersonaFisica(Persona):
    """Datos fiscales de una persona física."""

    curp: str = ""
    nombre: str = ""
    apellido_paterno: str = ""
    apellido_materno: str = ""
    fecha_nacimiento: DateField = None

    field_titles: ClassVar[dict[str, str]] = {
        "curp": "CURP:",
        "nombre": "Nombre:",
        "apellido_paterno": "Apellido Paterno:",
        "apellido_materno": "Apellido Materno:",
        "fecha_nacimiento": "Fecha Nacimiento:",
        **Persona.field_titles,
    }
