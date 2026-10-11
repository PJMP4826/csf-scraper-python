from datetime import datetime

import pytest

from csf_scraper import PersonaFisica
from tests.unit.persona.traits.persona_trait import (
    set_and_get_property,
    test_allows_more_than_one_regimen,
    test_assign_dynamic_property,
)

__all__ = [
    "test_allows_more_than_one_regimen",
    "test_assign_dynamic_property",
]

STRING_PROPERTIES_PROVIDER = [
    ("curp", "MI CURP"),
    ("nombre", "JUANITO"),
    ("apellido_paterno", "PEREZ"),
    ("apellido_materno", "RODRIGUEZ"),
]

DATE_PROPERTIES_PROVIDER = [
    ("fecha_nacimiento", "16-05-1996"),
]


@pytest.fixture
def person() -> PersonaFisica:
    return PersonaFisica()


@pytest.mark.parametrize(("attribute", "value"), STRING_PROPERTIES_PROVIDER)
def test_set_and_get_string_properties(
    person: PersonaFisica,
    attribute: str,
    value: str,
) -> None:
    result = set_and_get_property(person, attribute, value)
    assert result == value


@pytest.mark.parametrize(("attribute", "value"), DATE_PROPERTIES_PROVIDER)
def test_set_and_get_date_properties(
    person: PersonaFisica,
    attribute: str,
    value: str,
) -> None:
    result = set_and_get_property(person, attribute, value)
    assert result == datetime.strptime(value, "%d-%m-%Y")
