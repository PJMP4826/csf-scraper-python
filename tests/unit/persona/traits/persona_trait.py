"""Utilidades y casos de prueba compartidos por los modelos de persona."""

from typing import Any

from csf_scraper import Persona, Regimen


def set_and_get_property(person: Persona, attribute: str, value: Any) -> Any:
    """Asigna una propiedad y devuelve el valor leído."""
    setattr(person, attribute, value)
    return getattr(person, attribute)


def test_allows_more_than_one_regimen(person: Persona) -> None:
    first = Regimen(regimen="Simplificado de confianza")
    second = Regimen(regimen="Demás ingresos")

    person.regimenes = [first, second]

    assert len(person.regimenes) == 2
    assert person.regimenes[0] is first
    assert person.regimenes[1] is second


def test_assign_dynamic_property(person: Persona) -> None:
    person.extra_data["dynamic"] = "dynamic"
    assert person.extra_data["dynamic"] == "dynamic"
