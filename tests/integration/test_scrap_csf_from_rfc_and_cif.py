"""Migración de ``tests/Integration/ScrapCsfFromRfcAndCifTest.php``."""

from datetime import datetime

import httpx
import pytest
import respx
from stdnum.exceptions import ValidationError

from csf_scraper import CifDownloadException, CifNotFoundException, Scraper
from tests.helpers import file_contents
from tests.integration.helpers import VALIDADOR_URL_REGEX


def prepare_scraper(html_response: str) -> Scraper:
    """Equivalente a ``ScrapCsfFromRfcAndCifTest::prepareScraper()``."""
    respx.get(url__regex=VALIDADOR_URL_REGEX).mock(
        return_value=httpx.Response(200, text=file_contents(html_response)),
    )
    return Scraper(httpx.Client(follow_redirects=True, timeout=None))


def d(value: str) -> datetime:
    """Equivalente a ``DateTimeImmutable::createFromFormat('!d-m-Y', $value)``."""
    return datetime.strptime(value, "%d-%m-%Y")


@respx.mock
def test_scrap_from_idcif_and_rfc_by_moral() -> None:
    csf_scrap = prepare_scraper("scrap_moral.html")
    rfc = "DIM8701081LA"
    idcif = "1904014102123"
    expected_data = {
        "rfc": "DIM8701081LA",
        "id_cif": "1904014102123",
        "razon_social": "Mi razón social",
        "regimen_de_capital": "SA DE CV",
        "fecha_constitucion": d("21-02-2019"),
        "fecha_inicio_operaciones": d("21-02-2019"),
        "situacion_contribuyente": "ACTIVO",
        "fecha_ultimo_cambio_situacion": d("21-02-2019"),
        "entidad_federativa": "CIUDAD DE MEXICO",
        "municipio_delegacion": "CUAUHTEMOC",
        "colonia": "CUAUHTEMOC",
        "tipo_vialidad": "Tipo vialidad",
        "nombre_vialidad": "PASEO DE LA REFORMA",
        "numero_exterior": "143",
        "numero_interior": "Piso 69",
        "codigo_postal": "72055",
        "correo_electronico": "example@example.com",
        "al": "CIUDAD DE MEXICO 2",
        "regimenes": [
            {
                "regimen": "Régimen General de Ley Personas Morales",
                "regimen_id": "601",
                "fecha_alta": d("21-02-2019"),
            },
        ],
        "extra_data": {"Localidad": ""},
    }

    data = csf_scrap.obtain_from_rfc_and_cif(rfc, idcif).to_array()

    assert data == expected_data


@respx.mock
def test_scrap_from_idcif_and_rfc_by_fisica() -> None:
    csf_scrap = prepare_scraper("scrap_fisica.html")
    rfc = "COSC8001137NA"
    idcif = "1904014102123"
    expected_data = {
        "rfc": "COSC8001137NA",
        "id_cif": "1904014102123",
        "curp": "CURP",
        "nombre": "JUAN",
        "apellido_paterno": "PEREZ",
        "apellido_materno": "RODRIGUEZ",
        "fecha_nacimiento": d("01-05-1973"),
        "fecha_inicio_operaciones": d("03-11-2004"),
        "situacion_contribuyente": "ACTIVO",
        "fecha_ultimo_cambio_situacion": d("03-11-2004"),
        "entidad_federativa": "CIUDAD DE MEXICO",
        "municipio_delegacion": "IZTAPALAPA",
        "colonia": "MI COLONIA",
        "tipo_vialidad": "CALLE",
        "nombre_vialidad": "BENITO JUAREZ",
        "numero_exterior": "183",
        "numero_interior": "",
        "codigo_postal": "72000",
        "correo_electronico": "",
        "al": "CIUDAD DE MEXICO 3",
        "regimenes": [
            {
                "regimen": "Régimen de Incorporación Fiscal",
                "regimen_id": "621",
                "fecha_alta": d("01-01-2014"),
            },
        ],
        "extra_data": {"Localidad": ""},
    }

    data = csf_scrap.obtain_from_rfc_and_cif(rfc, idcif).to_array()

    assert data == expected_data


@respx.mock
def test_scrap_from_idcif_and_rfc_multiple_regimen() -> None:
    csf_scrap = prepare_scraper("scrap_regimenes.html")
    rfc = "COSC8001137NA"
    idcif = "1904014102123"
    expected_data = {
        "rfc": "COSC8001137NA",
        "id_cif": "1904014102123",
        "curp": "CURP",
        "nombre": "JUAN",
        "apellido_paterno": "PEREZ",
        "apellido_materno": "RODRIGUEZ",
        "fecha_nacimiento": d("21-07-1995"),
        "fecha_inicio_operaciones": d("01-01-2018"),
        "situacion_contribuyente": "ACTIVO",
        "fecha_ultimo_cambio_situacion": d("16-08-2018"),
        "entidad_federativa": "QUERETARO",
        "municipio_delegacion": "MUNICIPIO",
        "colonia": "MI COLONIA",
        "tipo_vialidad": "CALZADA (CALZ.)",
        "nombre_vialidad": "DEL BOSQUE",
        "numero_exterior": "19",
        "numero_interior": "",
        "codigo_postal": "72000",
        "correo_electronico": "example@example.com",
        "al": "QUERETARO 1",
        "regimenes": [
            {
                "regimen": "Régimen de Sueldos y Salarios e Ingresos Asimilados a Salarios",
                "regimen_id": "605",
                "fecha_alta": d("01-01-2018"),
            },
            {
                "regimen": "Régimen Simplificado de Confianza",
                "regimen_id": "626",
                "fecha_alta": d("09-02-2022"),
            },
        ],
        "extra_data": {"Localidad": ""},
    }

    data = csf_scrap.obtain_from_rfc_and_cif(rfc, idcif).to_array()

    assert data == expected_data


@respx.mock
def test_scrap_from_idcif_and_rfc_localidad_instead_of_colonia() -> None:
    csf_scrap = prepare_scraper("scrap_moral_without_colonia.html")
    rfc = "DIM8701081LA"
    idcif = "1904014102123"
    expected_data = {
        "rfc": "DIM8701081LA",
        "id_cif": "1904014102123",
        "razon_social": "MI RAZON",
        "regimen_de_capital": "SA DE CV",
        "fecha_constitucion": d("29-12-1997"),
        "fecha_inicio_operaciones": d("16-01-1999"),
        "situacion_contribuyente": "ACTIVO",
        "fecha_ultimo_cambio_situacion": d("16-01-1999"),
        "entidad_federativa": "CHIAPAS",
        "municipio_delegacion": "Mi Municipio",
        "colonia": "",
        "tipo_vialidad": "CALLE",
        "nombre_vialidad": "CONOCIDO",
        "numero_exterior": "SIN NUMERO",
        "numero_interior": "SIN NUMERO",
        "codigo_postal": "72030",
        "correo_electronico": "email@example.com",
        "al": "CHIAPAS 1",
        "regimenes": [
            {
                "regimen": "Régimen General de Ley Personas Morales",
                "regimen_id": "601",
                "fecha_alta": d("31-03-2001"),
            },
        ],
        "extra_data": {"Localidad": "30210010"},
    }

    data = csf_scrap.obtain_from_rfc_and_cif(rfc, idcif).to_array()

    assert data == expected_data


@respx.mock
def test_return_empty_when_not_found() -> None:
    csf_scrap = prepare_scraper("error.html")
    rfc = "COSC8001137NA"
    idcif = "1904014102123"

    with pytest.raises(CifNotFoundException):
        csf_scrap.obtain_from_rfc_and_cif(rfc, idcif)


@respx.mock
def test_throw_exception_on_download_error() -> None:
    respx.get(url__regex=VALIDADOR_URL_REGEX).mock(
        side_effect=httpx.ConnectError("Connection refused"),
    )
    csf_scrap = Scraper(httpx.Client(follow_redirects=True, timeout=None))
    rfc = "COSC8001137NA"
    idcif = "1904014102123"

    with pytest.raises(CifDownloadException):
        csf_scrap.obtain_from_rfc_and_cif(rfc, idcif)


@respx.mock(assert_all_called=False)
def test_send_invalid_rfc() -> None:
    csf_scrap = prepare_scraper("error.html")
    rfc = "bad-rfc"
    idcif = "1904014102123"

    with pytest.raises(ValidationError):
        csf_scrap.obtain_from_rfc_and_cif(rfc, idcif)
