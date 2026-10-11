"""Modelo de un régimen fiscal."""

import re

from pydantic import BaseModel, ConfigDict, computed_field

from csf_scraper.date_parser import DateField

_REGIMEN_CATALOG: dict[str, str] = {
    "601": "General de Ley Personas Morales",
    "603": "Personas Morales con Fines no Lucrativos",
    "605": "Sueldos y Salarios e Ingresos Asimilados a Salarios",
    "606": "Arrendamiento",
    "607": "Enajenación o Adquisición de Bienes",
    "608": "Demás ingresos",
    "610": "Residentes en el Extranjero sin Establecimiento Permanente en México",
    "611": "Ingresos por Dividendos (socios y accionistas)",
    "612": "Personas Físicas con Actividades Empresariales y Profesionales",
    "614": "Ingresos por intereses",
    "615": "ingresos por obtención de premios",
    "616": "Sin obligaciones fiscales",
    "620": "Sociedades Cooperativas de Producción que optan por diferir sus ingresos",
    "621": "Incorporación Fiscal",
    "622": "Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras",
    "623": "Opcional para Grupos de Sociedades",
    "624": "Coordinados",
    "625": "Actividades Empresariales con ingresos a través de Plataformas Tecnológicas",
    "626": "Simplificado de Confianza",
}

_REGIMEN_BY_TEXT: dict[str, str] = {
    text.upper(): regimen_id for regimen_id, text in _REGIMEN_CATALOG.items()
}

_PREFIX = re.compile(r"^Régimen (?:de (?:las |los )?)?")
_SUFFIX_PM = re.compile(r" PM$")
_SUFFIX_DOT = re.compile(r"\.$")


def _normalize_text(regimen: str) -> str:
    text = _PREFIX.sub("", regimen)
    text = _SUFFIX_PM.sub("", text)
    return _SUFFIX_DOT.sub("", text)


def _search_regimen_id(regimen: str) -> str:
    return _REGIMEN_BY_TEXT.get(_normalize_text(regimen).upper(), "")


class Regimen(BaseModel):
    """Un régimen fiscal con su id derivado del texto y su fecha de alta."""

    model_config = ConfigDict(validate_assignment=True)

    regimen: str = ""
    fecha_alta: DateField = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def regimen_id(self) -> str:
        """Id del catálogo que corresponde al texto de :attr:`regimen`."""
        return _search_regimen_id(self.regimen)
