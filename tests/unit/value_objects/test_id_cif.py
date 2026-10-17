import pytest

from csf_scraper import CsfScraperException, IdCif, InvalidIdCifFormatException


@pytest.mark.parametrize(
    "value",
    ["25020218873", "20090374035", "16090402016", "12345678", "1904014102123"],
)
def test_accepts_valid_id_cif(value: str) -> None:
    assert IdCif(value) == value


def test_is_a_string() -> None:
    assert isinstance(IdCif("1904014102123"), str)


def test_normalizes_whitespace() -> None:
    assert IdCif("  1904014102123  ") == "1904014102123"


@pytest.mark.parametrize(
    "value",
    ["", "abcdefgh", "1234567", "12345678901234", "123-456-7890", "1234 5678"],
)
def test_rejects_invalid_id_cif(value: str) -> None:
    with pytest.raises(InvalidIdCifFormatException):
        IdCif(value)


def test_exception_is_a_library_exception() -> None:
    assert issubclass(InvalidIdCifFormatException, CsfScraperException)


def test_ensure_validates_and_returns_value_object() -> None:
    assert isinstance(IdCif.ensure("25020218873"), IdCif)


def test_value_returns_plain_string() -> None:
    value = IdCif("1904014102123").value
    assert value == "1904014102123"
    assert type(value) is str
