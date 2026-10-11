"""Modelo de persona moral."""

from typing import ClassVar

from csf_scraper.date_parser import DateField
from csf_scraper.persona import Persona


class PersonaMoral(Persona):
    """Datos fiscales de una persona moral."""

    razon_social: str = ""
    regimen_de_capital: str = ""
    fecha_constitucion: DateField = None

    field_titles: ClassVar[dict[str, str]] = {
        "razon_social": "Denominación o Razón Social:",
        "regimen_de_capital": "Régimen de capital:",
        "fecha_constitucion": "Fecha de constitución:",
        **Persona.field_titles,
    }
