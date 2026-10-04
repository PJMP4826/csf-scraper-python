"""Modelo base de persona fiscal (migración de ``src/Persona.php``)."""

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from csf_scraper.date_parser import DateField
from csf_scraper.regimen import Regimen
from csf_scraper.regimenes import Regimenes


def _resolve_field_name(field_names: Iterable[str], name: str) -> str | None:
    """Resuelve el nombre de propiedad a un campo del modelo.

    Reproduce el comportamiento de ``Persona::__set``/``__get`` de PHP, donde la
    búsqueda del método ``set{Nombre}``/``get{Nombre}`` es case-insensitive: se
    comparan los nombres sin importar mayúsculas/minúsculas ni guiones bajos, lo
    que permite tanto los nombres camelCase usados por ``DataExtractor`` como los
    snake_case del API Python.
    """
    if name in field_names:
        return name
    normalized = name.replace("_", "").lower()
    for field_name in field_names:
        if field_name.replace("_", "").lower() == normalized:
            return field_name
    return None


class Persona(BaseModel, ABC):
    """Datos fiscales de una persona moral o física.

    Equivalente a ``PhpCfdi\\CsfScraper\\Persona`` (clase abstracta).
    """

    model_config = ConfigDict(validate_assignment=True)

    rfc: str = ""
    id_cif: str = ""
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
    regimenes: Regimenes = Field(default_factory=Regimenes)
    extra_data: dict[str, Any] = Field(default_factory=dict)

    @abstractmethod
    def get_td_titles_text_to_search(self) -> dict[str, str]:
        """Textos de los títulos (celda) a buscar en el HTML.

        Equivalente a ``Persona::getTdTitlesTextToSearch``: los valores deben ser
        textos simples buscables con ``contains(normalize-space(.), {value})``.
        """

    def add_regimenes(self, *regimenes: Regimen) -> None:
        """Equivalente a ``Persona::addRegimenes(Regimen ...$regimenes)``."""
        self.regimenes.add_regimen(*regimenes)

    def to_array(self) -> dict[str, Any]:
        """Equivalente a ``Persona::toArray()``."""
        return {
            "rfc": self.rfc,
            "id_cif": self.id_cif,
            "fecha_inicio_operaciones": self.fecha_inicio_operaciones,
            "situacion_contribuyente": self.situacion_contribuyente,
            "fecha_ultimo_cambio_situacion": self.fecha_ultimo_cambio_situacion,
            "entidad_federativa": self.entidad_federativa,
            "municipio_delegacion": self.municipio_delegacion,
            "colonia": self.colonia,
            "tipo_vialidad": self.tipo_vialidad,
            "nombre_vialidad": self.nombre_vialidad,
            "numero_exterior": self.numero_exterior,
            "numero_interior": self.numero_interior,
            "codigo_postal": self.codigo_postal,
            "correo_electronico": self.correo_electronico,
            "al": self.al,
            "regimenes": self.regimenes.to_array(),
            "extra_data": self.extra_data,
        }

    def __setattr__(self, name: str, value: Any) -> None:
        """Equivalente a ``Persona::__set``: campo del modelo o dato dinámico."""
        if name.startswith("_"):
            super().__setattr__(name, value)
            return
        field_name = _resolve_field_name(type(self).model_fields, name)
        if field_name is not None:
            super().__setattr__(field_name, value)
            return
        self.extra_data[name] = value

    def __getattr__(self, name: str) -> Any:
        """Equivalente a ``Persona::__get``: campo del modelo o dato dinámico."""
        if not name.startswith("_"):
            field_name = _resolve_field_name(type(self).model_fields, name)
            if field_name is not None and field_name in self.__dict__:
                return self.__dict__[field_name]
        extra_data = self.__dict__.get("extra_data")
        if isinstance(extra_data, dict) and name in extra_data:
            return extra_data[name]
        raise AttributeError(f"{type(self).__name__} object has no attribute {name!r}")

    def __delattr__(self, name: str) -> None:
        """Equivalente a ``Persona::__unset``."""
        if not name.startswith("_"):
            field_name = _resolve_field_name(type(self).model_fields, name)
            if field_name is not None:
                super().__delattr__(field_name)
                return
        extra_data = self.__dict__.get("extra_data")
        if isinstance(extra_data, dict) and name in extra_data:
            del extra_data[name]
            return
        super().__delattr__(name)
