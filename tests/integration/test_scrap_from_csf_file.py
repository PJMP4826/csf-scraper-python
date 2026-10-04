"""Migración de ``tests/Integration/ScrapFromCsfFileTest.php``."""

import platform
from datetime import datetime

import httpx
import pytest
import respx

from csf_scraper import CifDownloadException, CifNotFoundException, Scraper
from csf_scraper.exceptions.pdf_reader import (
    CifFromPdfNotFoundException,
    RfcFromPdfNotFoundException,
)
from tests.helpers import file_contents, file_path
from tests.integration.helpers import VALIDADOR_URL_REGEX, ScraperHelper


def prepare_scraper(html_response: str) -> Scraper:
    """Equivalente a ``ScrapFromCsfFileTest::prepareScraper()`` (usa ``ScraperHelper``)."""
    respx.get(url__regex=VALIDADOR_URL_REGEX).mock(
        return_value=httpx.Response(200, text=file_contents(html_response)),
    )
    return ScraperHelper(httpx.Client(follow_redirects=True, timeout=None))


def d(value: str) -> datetime:
    """Equivalente a ``DateTimeImmutable::createFromFormat('!d-m-Y', $value)``."""
    return datetime.strptime(value, "%d-%m-%Y")


@respx.mock
def test_scrap_from_idcif_and_rfc_by_moral() -> None:
    csf_scrap = prepare_scraper("scrap_moral.html")
    expected_data = {
        "rfc": "DIM8701081LA",
        "id_cif": "12345678",
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

    data = csf_scrap.obtain_from_pdf_path("my-path").to_dict()

    assert data == expected_data


@respx.mock
def test_obtain_from_pdf_with_invalid_url() -> None:
    previous_url = Scraper.url
    Scraper.url = previous_url.replace("siat.sat.gob.mx", "sat.gob.mx")

    try:
        respx.get(host="sat.gob.mx").mock(
            side_effect=httpx.ConnectError("Connection refused"),
        )
        csf_scrap = Scraper.create()

        with pytest.raises(CifDownloadException):
            csf_scrap.obtain_from_pdf_path(str(file_path("csf-correct-but-invalid.pdf")))
    finally:
        Scraper.url = previous_url


@respx.mock
def test_obtain_from_pdf_with_invalid_data() -> None:
    respx.get(url__regex=VALIDADOR_URL_REGEX).mock(
        return_value=httpx.Response(200, text=file_contents("error.html")),
    )
    csf_scrap = Scraper.create()

    with pytest.raises(CifNotFoundException):
        csf_scrap.obtain_from_pdf_path(str(file_path("csf-correct-but-invalid.pdf")))


@pytest.mark.skipif(
    platform.system() != "Linux",
    reason="RequiresOperatingSystem('Linux')",
)
@respx.mock
def test_obtain_from_pdf_without_rfc() -> None:
    csf_scrap = Scraper.create()

    with pytest.raises(RfcFromPdfNotFoundException):
        csf_scrap.obtain_from_pdf_path(str(file_path("csf-without-rfc.pdf")))


@pytest.mark.skipif(
    platform.system() != "Linux",
    reason="RequiresOperatingSystem('Linux')",
)
@respx.mock
def test_obtain_from_pdf_without_cif() -> None:
    csf_scrap = Scraper.create()

    with pytest.raises(CifFromPdfNotFoundException):
        csf_scrap.obtain_from_pdf_path(str(file_path("csf-without-cif.pdf")))
