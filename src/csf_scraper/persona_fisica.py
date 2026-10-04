"""Modelo de persona física (migración de ``src/PersonaFisica.php``)."""

from typing import Any

from csf_scraper.date_parser import DateField
from csf_scraper.persona import Persona


class PersonaFisica(Persona):
    """Datos fiscales de una persona física.

    Equivalente a ``PhpCfdi\\CsfScraper\\PersonaFisica``.
    """

    curp: str = ""
    nombre: str = ""
    apellido_paterno: str = ""
    apellido_materno: str = ""
    fecha_nacimiento: DateField = None

    def get_td_titles_text_to_search(self) -> dict[str, str]:
        """Equivalente a ``PersonaFisica::getTdTitlesTextToSearch``."""
        return {
            "Curp": "CURP:",
            "Nombre": "Nombre:",
            "ApellidoPaterno": "Apellido Paterno:",
            "ApellidoMaterno": "Apellido Materno:",
            "FechaNacimiento": "Fecha Nacimiento:",
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

    def to_dict(self) -> dict[str, Any]:
        """Equivalente a ``PersonaFisica::toArray()`` (campos propios + los de ``Persona``)."""
        return {
            "curp": self.curp,
            "nombre": self.nombre,
            "apellido_paterno": self.apellido_paterno,
            "apellido_materno": self.apellido_materno,
            "fecha_nacimiento": self.fecha_nacimiento,
            **super().to_dict(),
        }
