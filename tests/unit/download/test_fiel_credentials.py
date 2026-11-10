import pytest
from tests.unit.download._fiel_certs import PASSWORD, make_fiel_key_and_cert

from csf_scraper.download import FielCredentials
from csf_scraper.download.exceptions import FielCredentialsException


def test_from_bytes_stores_the_password_as_a_secret() -> None:
    certificate, key = make_fiel_key_and_cert()

    credentials = FielCredentials.from_bytes(certificate=certificate, key=key, password=PASSWORD)

    assert credentials.password_value() == PASSWORD.encode()
    assert PASSWORD not in repr(credentials)


def test_from_bytes_rejects_empty_certificate_or_key() -> None:
    with pytest.raises(FielCredentialsException):
        FielCredentials.from_bytes(certificate=b"", key=b"key")
    with pytest.raises(FielCredentialsException):
        FielCredentials.from_bytes(certificate=b"cert", key=b"")


def test_from_files_reads_both_files(tmp_path) -> None:  # type: ignore[no-untyped-def]
    certificate, key = make_fiel_key_and_cert()
    cert_path = tmp_path / "fiel.cer"
    key_path = tmp_path / "fiel.key"
    cert_path.write_bytes(certificate)
    key_path.write_bytes(key)

    credentials = FielCredentials.from_files(
        certificate_path=str(cert_path), key_path=str(key_path), password=PASSWORD
    )

    assert credentials.certificate == certificate
    assert credentials.key == key


def test_from_files_with_a_missing_file_raises() -> None:
    with pytest.raises(FielCredentialsException):
        FielCredentials.from_files(certificate_path="/no/existe.cer", key_path="/no/existe.key")
