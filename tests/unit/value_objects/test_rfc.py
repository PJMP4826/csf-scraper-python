import pytest

from csf_scraper import CsfScraperException, InvalidRfcFormatException, Rfc

VALID_MORAL = "DIM8701081LA"
VALID_FISICA = "COSC8001137NA"


def test_accepts_moral_rfc() -> None:
    rfc = Rfc(VALID_MORAL)
    assert rfc == VALID_MORAL
    assert rfc.is_moral()
    assert not rfc.is_fisica()


def test_accepts_fisica_rfc() -> None:
    rfc = Rfc(VALID_FISICA)
    assert rfc == VALID_FISICA
    assert rfc.is_fisica()
    assert not rfc.is_moral()


def test_normalizes_whitespace_and_case() -> None:
    assert Rfc("  dim8701081la  ") == VALID_MORAL


def test_is_a_string() -> None:
    assert isinstance(Rfc(VALID_MORAL), str)
    assert f"{Rfc(VALID_FISICA)}" == VALID_FISICA


@pytest.mark.parametrize(
    "value",
    [
        "",
        "bad-rfc",
        "ABC",
        "DIM8701081L",
        "DIM8701081LAX",
        "12AB8701081LA",
        "DIM8701081L-",
    ],
)
def test_rejects_invalid_rfc(value: str) -> None:
    with pytest.raises(InvalidRfcFormatException):
        Rfc(value)


def test_exception_is_a_library_exception() -> None:
    assert issubclass(InvalidRfcFormatException, CsfScraperException)


def test_ensure_validates_and_returns_value_object() -> None:
    assert isinstance(Rfc.ensure("cosc8001137na"), Rfc)


def test_value_returns_plain_string() -> None:
    value = Rfc(VALID_MORAL).value
    assert value == VALID_MORAL
    assert type(value) is str
