from datetime import datetime

import pytest

from csf_scraper import PersonaMoral
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
    ("razon_social", "MI TIENDITA"),
    ("regimen_de_capital", "SA de SV"),
]

DATE_PROPERTIES_PROVIDER = [
    ("fecha_constitucion", "16-05-1996"),
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
