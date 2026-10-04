from csf_scraper import Regimen, Regimenes


def test_add_regimenes() -> None:
    first = Regimen()
    first.set_regimen("Sin obligaciones fiscales")
    second = Regimen()
    second.set_regimen("Demás ingresos")

    regimenes = Regimenes()
    regimenes.add_regimen(first, second)

    result = regimenes.get_regimenes()
    assert len(result) == 2
    assert result[0] is first
    assert result[1] is second
