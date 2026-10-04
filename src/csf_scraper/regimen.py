"""Modelo de régimen fiscal (migración de ``src/Regimen.php``)."""

import re
from typing import Any

from pydantic import BaseModel, ConfigDict

from csf_scraper.date_parser import DateField, parse_date

#: Catálogo de regímenes con su id (datos de ``Regimen::$regimenes`` en PHP).
_REGIMEN_CATALOG: list[tuple[str, str]] = [
    ("601", "General de Ley Personas Morales"),
    ("603", "Personas Morales con Fines no Lucrativos"),
    ("605", "Sueldos y Salarios e Ingresos Asimilados a Salarios"),
    ("606", "Arrendamiento"),
    ("607", "Enajenación o Adquisición de Bienes"),
    ("608", "Demás ingresos"),
    ("610", "Residentes en el Extranjero sin Establecimiento Permanente en México"),
    ("611", "Ingresos por Dividendos (socios y accionistas)"),
    ("612", "Personas Físicas con Actividades Empresariales y Profesionales"),
    ("614", "Ingresos por intereses"),
    ("615", "ingresos por obtención de premios"),
    ("616", "Sin obligaciones fiscales"),
    ("620", "Sociedades Cooperativas de Producción que optan por diferir sus ingresos"),
    ("621", "Incorporación Fiscal"),
    ("622", "Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras"),
    ("623", "Opcional para Grupos de Sociedades"),
    ("624", "Coordinados"),
    ("625", "Actividades Empresariales con ingresos a través de Plataformas Tecnológicas"),
    ("626", "Simplificado de Confianza"),
]


def _normalize_regimen_text(regimen: str) -> str:
    """Aplica las mismas tres sustituciones de ``Regimen::setRegimen`` (en orden)."""
    text = re.sub(r"^Régimen( de las| de los| de|) ", "", regimen)
    text = re.sub(r" PM$", "", text)
    return re.sub(r"\.$", "", text)


def _search_regimen_id_by_text(text: str) -> str:
    for regimen_id, catalog_text in _REGIMEN_CATALOG:
        if text.upper() == catalog_text.upper():
            return regimen_id
    return ""


class Regimen(BaseModel):
    """Un régimen fiscal con su id derivado del texto y su fecha de alta.

    Equivalente a ``PhpCfdi\\CsfScraper\\Regimen``.
    """

    model_config = ConfigDict(validate_assignment=True)

    regimen: str = ""
    regimen_id: str = ""
    fecha_alta: DateField = None

    def set_regimen(self, regimen: str) -> None:
        """Asigna el texto del régimen y calcula ``regimen_id`` con el catálogo."""
        self.regimen = regimen
        self.regimen_id = _search_regimen_id_by_text(_normalize_regimen_text(regimen))

    def set_fecha_alta(self, fecha_alta: str) -> None:
        """Asigna la fecha de alta desde ``dd-mm-yyyy`` (``None`` si no es válida)."""
        self.fecha_alta = parse_date(fecha_alta)

    def to_dict(self) -> dict[str, Any]:
        """Equivalente a ``Regimen::toArray()``."""
        return {
            "regimen": self.regimen,
            "regimen_id": self.regimen_id,
            "fecha_alta": self.fecha_alta,
        }
