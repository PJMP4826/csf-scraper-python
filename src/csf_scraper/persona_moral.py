"""Modelo de persona moral (migración de ``src/PersonaMoral.php``)."""

from typing import Any

from csf_scraper.date_parser import DateField
from csf_scraper.persona import Persona


class PersonaMoral(Persona):
    """Datos fiscales de una persona moral.

    Equivalente a ``PhpCfdi\\CsfScraper\\PersonaMoral``.
    """

    razon_social: str = ""
    regimen_de_capital: str = ""
    fecha_constitucion: DateField = None

    def get_td_titles_text_to_search(self) -> dict[str, str]:
        """Equivalente a ``PersonaMoral::getTdTitlesTextToSearch``."""
        return {
            "RazonSocial": "Denominación o Razón Social:",
            "RegimenDeCapital": "Régimen de capital:",
            "FechaConstitucion": "Fecha de constitución:",
            "FechaInicioOperaciones": "Fecha de Inicio de operaciones:",
            "SituacionContribuyente": "Situación del contribuyente:",
            "FechaUltimoCambioSituacion": "Fecha del último cambio de situación:",
            "EntidadFederativa": "Entidad Federativa:",
            "MunicipioDelegacion": "Municipio o delegación:",
            "Colonia": "Colonia:",
            "Localidad": "Localidad:",
            "TipoVialidad": "Tipo de vialidad:",
            "NombreVialidad": "Nombre de la vialidad:",
            "NumeroExterior": "Número exterior:",
            "NumeroInterior": "Número interior:",
            "CodigoPostal": "CP:",
            "CorreoElectronico": "Correo electrónico:",
            "Al": "AL:",
        }

    def to_array(self) -> dict[str, Any]:
        """Equivalente a ``PersonaMoral::toArray()`` (campos propios + los de ``Persona``)."""
        return {
            "razon_social": self.razon_social,
            "regimen_de_capital": self.regimen_de_capital,
            "fecha_constitucion": self.fecha_constitucion,
            **super().to_array(),
        }
