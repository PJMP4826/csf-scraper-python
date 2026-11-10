import base64

from csf_scraper.download import generate_token


class _FakeSigner:
    """Firmante de prueba que devuelve una firma fija."""

    rfc = "DIM8701081LA"
    certificate_number = "123456"
    fert = "310101000000Z"

    def sign_sha1(self, data: bytes) -> str:
        return base64.b64encode(b"signed:" + data).decode()


def test_generate_token_encodes_guid_rfc_and_serial_signed() -> None:
    token = generate_token(_FakeSigner(), "guid-abc")  # type: ignore[arg-type]

    outer = base64.b64decode(token)
    encoded_co, encoded_signature = outer.split(b"#")
    assert base64.b64decode(encoded_co) == b"guid-abc|DIM8701081LA|123456"
    assert base64.b64decode(encoded_signature) == base64.b64encode(
        b"signed:guid-abc|DIM8701081LA|123456"
    )


def test_generate_token_uses_the_signer_rfc_and_serial() -> None:
    signer = _FakeSigner()
    signer.rfc = "GODE561231GR8"

    token = generate_token(signer, "g-1")  # type: ignore[arg-type]

    encoded_co, _ = base64.b64decode(token).split(b"#")
    assert base64.b64decode(encoded_co) == b"g-1|GODE561231GR8|123456"


def test_generate_token_with_a_real_signer_verifies() -> None:
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    from tests.unit.download._fiel_certs import PASSWORD, make_fiel_key_and_cert

    from csf_scraper.download import FielCredentials, Signer

    certificate, key = make_fiel_key_and_cert()
    signer = Signer.load(
        FielCredentials.from_bytes(certificate=certificate, key=key, password=PASSWORD)
    )

    token = generate_token(signer, "guid-real")

    outer = base64.b64decode(token)
    encoded_co, encoded_signature = outer.split(b"#")
    co = base64.b64decode(encoded_co)
    assert co.startswith(b"guid-real|DIM8701081LA|")
    signature = base64.b64decode(base64.b64decode(encoded_signature))
    public_key = x509.load_der_x509_certificate(certificate).public_key()
    public_key.verify(signature, co, padding.PKCS1v15(), hashes.SHA1())
