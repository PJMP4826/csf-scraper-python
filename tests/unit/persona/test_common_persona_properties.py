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


@pytest.mark.parametrize(("complement_function", "value"), STRING_PROPERTIES_PROVIDER)
def test_set_and_get_string_properties(
    person: PersonaMoral,
    complement_function: str,
    value: str,
) -> None:
    result = set_and_get_property(person, complement_function, value)
    assert result == value


@pytest.mark.parametrize(("complement_function", "value"), DATE_PROPERTIES_PROVIDER)
def test_set_and_get_date_properties(
    person: PersonaMoral,
    complement_function: str,
    value: str,
) -> None:
    result = set_and_get_property(person, complement_function, value)
    assert result == datetime.strptime(value, "%d-%m-%Y")


def test_assign_dynamic_property(person: PersonaMoral) -> None:
    dynamic_value = "foo"
    person.dynamic = dynamic_value
    assert person.dynamic == dynamic_value


def test_isset_property_method(person: PersonaMoral) -> None:
    person.dynamic = "foo"

    # isset($person->{'dynamic'}) / isset($person->{'dynamic2'})
    assert person.dynamic is not None
    assert getattr(person, "dynamic2", None) is None


def test_unset_method(person: PersonaMoral) -> None:
    person.dynamic = "foo"
    assert person.dynamic is not None

    del person.dynamic
    assert getattr(person, "dynamic", None) is None
