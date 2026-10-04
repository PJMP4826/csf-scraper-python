"""Traducción de ``tests/Unit/Persona/Traits/PersonaTrait.php``.

El trait de PHPUnit se comparte entre ``CommonPersonaPropertiesTest``,
``PersonaFisicaPropertiesTest`` y ``PersonaMoralPropertiesTest``; aquí los tests
compartidos se importan en cada módulo de test (pytest los recolecta por nombre).
"""

from typing import Any

from csf_scraper import Persona, Regimen


def set_and_get_property(person: Persona, complement_function: str, value: Any) -> Any:
    """Equivalente a ``PersonaTrait::setAndGetProperty`` (asigna y lee la propiedad)."""
    setattr(person, complement_function, value)
    return getattr(person, complement_function)


def test_allows_more_than_one_regimen(person: Persona) -> None:
    first = Regimen()
    first.set_regimen("Simplificado de confianza")
    second = Regimen()
    second.set_regimen("Demás ingresos")

    person.add_regimenes(first, second)

    result = person.regimenes.get_regimenes()
    assert len(result) == 2
    assert result[0] is first
    assert result[1] is second


def test_assign_dynamic_property(person: Persona) -> None:
    person.dynamic = "dynamic"
    assert person.dynamic == "dynamic"
