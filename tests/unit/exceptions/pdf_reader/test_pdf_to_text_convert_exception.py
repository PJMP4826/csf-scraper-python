from pathlib import Path

from csf_scraper import CsfScraperException, PdfToTextConvertException


def test_implements_library_exception_type() -> None:
    assert issubclass(PdfToTextConvertException, CsfScraperException)


def test_properties() -> None:
    message = "exception message"
    command = [str(Path(__file__).parent), "argument"]
    exit_code = 1
    output = "output message"
    error = "error message"

    exception = PdfToTextConvertException(message, command, exit_code, output, error)

    assert str(exception) == message
    assert exception.command == command
    assert exception.exit_code == exit_code
    assert exception.output == output
    assert exception.error == error
