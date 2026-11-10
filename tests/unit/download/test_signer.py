import base64

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import (
    BestAvailableEncryption,
    pkcs12,
)
from tests.unit.download._fiel_certs import PASSWORD, RFC, make_fiel_key_and_cert

from csf_scraper.download import FielCredentials, Signer
from csf_scraper.download.exceptions import FielCredentialsException


def _credentials() -> tuple[bytes, bytes]:
    return make_fiel_key_and_cert()


def _load_signer() -> Signer:
    certificate, key = _credentials()
    return Signer.load(
        FielCredentials.from_bytes(certificate=certificate, key=key, password=PASSWORD)
    )


def test_load_reads_rfc_serial_and_expiry_from_the_certificate() -> None:
    signer = _load_signer()

    assert signer.rfc == RFC
    assert signer.certificate_number == f"{0x1234567890ABCDEF1234:x}"[1::2]
    assert signer.fert  # formato SAT, sin los dos primeros caracteres de notAfter


def test_sign_sha1_verifies_with_the_certificate_public_key() -> None:
    certificate, key = _credentials()
    signer = Signer.load(
        FielCredentials.from_bytes(certificate=certificate, key=key, password=PASSWORD)
    )
    data = b"guid-1|DIM8701081LA|12345"

    signature = signer.sign_sha1(data)

    public_key = x509.load_der_x509_certificate(certificate).public_key()
    public_key.verify(
        base64.b64decode(signature),
        data,
        padding.PKCS1v15(),
        hashes.SHA1(),
    )


def test_load_rejects_a_key_that_does_not_match_the_certificate() -> None:
    certificate, _ = _credentials()
    _, other_key = _credentials()

    with pytest.raises(FielCredentialsException):
        Signer.load(
            FielCredentials.from_bytes(certificate=certificate, key=other_key, password=PASSWORD)
        )


def test_load_rejects_a_wrong_password() -> None:
    certificate, key = _credentials()

    with pytest.raises(FielCredentialsException):
        Signer.load(FielCredentials.from_bytes(certificate=certificate, key=key, password="wrong"))


def test_load_pkcs12_roundtrip() -> None:
    certificate, key = _credentials()
    signer = Signer.load(
        FielCredentials.from_bytes(certificate=certificate, key=key, password=PASSWORD)
    )
    x509_cert = x509.load_der_x509_certificate(certificate)
    p12 = pkcs12.serialize_key_and_certificates(
        name=RFC.encode(),
        key=signer._key,
        cert=x509_cert,
        cas=None,
        encryption_algorithm=BestAvailableEncryption(PASSWORD.encode()),
    )

    loaded = Signer.load_pkcs12(p12, PASSWORD)

    assert loaded.rfc == RFC
    assert loaded.certificate_number == signer.certificate_number
