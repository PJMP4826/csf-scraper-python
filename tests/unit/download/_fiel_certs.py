"""Certificados FIEL de prueba (autofirmados, solo para tests)."""

from datetime import UTC, datetime, timedelta

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import (
    BestAvailableEncryption,
    Encoding,
    PrivateFormat,
)
from cryptography.x509.oid import NameOID

RFC = "DIM8701081LA"
PASSWORD = "fiel-password"


def make_fiel_key_and_cert(password: str = PASSWORD) -> tuple[bytes, bytes]:
    """Genera una llave RSA y un certificado autofirmado con RFC en el subject.

    Devuelve ``(certificate_der, key_der_cifrada)``.
    """
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, "DIM8701081LA"),
            x509.NameAttribute(
                x509.ObjectIdentifier("2.5.4.45"),  # x500UniqueIdentifier
                f"{RFC}/ ",
            ),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "MI RAZON SOCIAL SA DE CV"),
        ]
    )
    now = datetime.now(UTC)
    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(0x1234567890ABCDEF1234)
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=365))
        .sign(key, hashes.SHA256())
    )
    return (
        certificate.public_bytes(Encoding.DER),
        key.private_bytes(
            Encoding.DER,
            PrivateFormat.PKCS8,
            BestAvailableEncryption(password.encode()),
        ),
    )
