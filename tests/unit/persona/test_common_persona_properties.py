from datetime import datetime

import pytest

from csf_scraper import PersonaMoral
from tests.unit.persona.traits.persona_trait import (
    set_and_get_property,
    test_allows_more_than_one_regimen,
)

__all__ = ["test_allows_more_than_one_regimen"]

STRING_PROPERTIES_PROVIDER = [
    ("situacion_contribuyente", "ACTIVO"),
    ("entidad_federativa", "Puebla"),
    ("municipio_delegacion", "Municipio"),
    ("colonia", "Mi Colonia"),
    ("tipo_vialidad", "Vialidad"),
    ("nombre_vialidad", "Nombre Calle"),
    ("numero_exterior", "1"),
    ("numero_interior", "2"),
    ("codigo_postal", "72000"),
    ("correo_electronico", "correo@example.com"),
    ("al", "Puebla 1"),
]

DATE_PROPERTIES_PROVIDER = [
    ("fecha_inicio_operaciones", "12-01-2017"),
    ("fecha_ultimo_cambio_situacion", "12-01-2018"),
]


@pytest.fixture
def person() -> PersonaMoral:
    return PersonaMoral()


@pytest.mark.parametrize(("attribute", "value"), STRING_PROPERTIES_PROVIDER)
def test_set_and_get_string_properties(
    person: PersonaMoral,
    attribute: str,
    value: str,
) -> None:
    result = set_and_get_property(person, attribute, value)
    assert result == value


@pytest.mark.parametrize(("attribute", "value"), DATE_PROPERTIES_PROVIDER)
def test_set_and_get_date_properties(
    person: PersonaMoral,
    attribute: str,
    value: str,
) -> None:
    result = set_and_get_property(person, attribute, value)
    assert result == datetime.strptime(value, "%d-%m-%Y")


def test_assign_extra_data(person: PersonaMoral) -> None:
    person.extra_data["dynamic"] = "foo"
    assert person.extra_data["dynamic"] == "foo"


def test_extra_data_membership(person: PersonaMoral) -> None:
    person.extra_data["dynamic"] = "foo"

    assert person.extra_data.get("dynamic") is not None
    assert person.extra_data.get("dynamic2") is None


def test_delete_extra_data(person: PersonaMoral) -> None:
    person.extra_data["dynamic"] = "foo"
    assert person.extra_data.get("dynamic") is not None

    del person.extra_data["dynamic"]
    assert person.extra_data.get("dynamic") is None
