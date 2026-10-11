from csf_scraper import PersonaMoral, Regimen


def test_add_regimenes() -> None:
    person = PersonaMoral()
    first = Regimen(regimen="Sin obligaciones fiscales")
    second = Regimen(regimen="Demás ingresos")

    person.regimenes.extend([first, second])

    assert len(person.regimenes) == 2
    assert person.regimenes[0] is first
    assert person.regimenes[1] is second
