import pytest

from csf_scraper import Regimen

REGIMENES_PROVIDER = [
    ("General de Ley Personas Morales", "601"),
    ("Personas Morales con Fines no Lucrativos", "603"),
    ("Sueldos y Salarios e Ingresos Asimilados a Salarios", "605"),
    ("Arrendamiento", "606"),
    ("Régimen de Enajenación o Adquisición de Bienes", "607"),
    ("Demás ingresos", "608"),
    ("Residentes en el Extranjero sin Establecimiento Permanente en México", "610"),
    ("Ingresos por Dividendos (socios y accionistas)", "611"),
    ("Personas Físicas con Actividades Empresariales y Profesionales", "612"),
    ("Ingresos por intereses", "614"),
    ("Régimen de los ingresos por obtención de premios", "615"),
    ("Sin obligaciones fiscales", "616"),
    ("Sociedades Cooperativas de Producción que optan por diferir sus ingresos", "620"),
    ("Incorporación Fiscal", "621"),
    ("Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras", "622"),
    ("Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras PM", "622"),
    ("Opcional para Grupos de Sociedades", "623"),
    ("Coordinados", "624"),
    (
        "Régimen de las Actividades Empresariales con ingresos a través de "
        "Plataformas Tecnológicas",
        "625",
    ),
    (
        "Régimen de las Actividades Empresariales con ingresos a través de "
        "Plataformas Tecnológicas.",
        "625",
    ),
    ("Régimen Simplificado de Confianza", "626"),
]


@pytest.mark.parametrize(("regimen_text", "regimen_id_expected"), REGIMENES_PROVIDER)
def test_check_regimenes_are_well_assigned(regimen_text: str, regimen_id_expected: str) -> None:
    regimen = Regimen(regimen=regimen_text)

    assert regimen.regimen == regimen_text
    assert regimen.regimen_id == regimen_id_expected


def test_detect_correct_regimen_case_insensitive() -> None:
    regimen = Regimen(regimen="DEMÁS INGRESOS")

    assert regimen.regimen_id == "608"


def test_returns_empty_when_not_found() -> None:
    regimen = Regimen(regimen="regimen no incluido")

    assert regimen.regimen_id == ""


def test_fecha_alta_with_valid_value() -> None:
    input_value = "01-02-2001"
    regimen = Regimen(fecha_alta=input_value)
    fecha_alta = regimen.fecha_alta
    if fecha_alta is None:
        pytest.fail(f"Fecha alta {input_value} was not interpreted")
    assert fecha_alta.day == 1
    assert fecha_alta.month == 2
    assert fecha_alta.year == 2001
    assert fecha_alta.hour == 0
    assert fecha_alta.minute == 0
    assert fecha_alta.second == 0


def test_fecha_alta_with_empty_value() -> None:
    regimen = Regimen(fecha_alta="")
    assert regimen.fecha_alta is None


@pytest.mark.parametrize(
    "input_value",
    [
        pytest.param("", id="empty"),
        pytest.param("2022-12-31", id="incorrect-format"),
        pytest.param("1-1", id="incomplete"),
    ],
)
def test_fecha_alta_with_invalid_value(input_value: str) -> None:
    regimen = Regimen(fecha_alta=input_value)
    assert regimen.fecha_alta is None
