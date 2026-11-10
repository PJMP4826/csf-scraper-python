"""Firmante FIEL.

Implementación propia de :class:`SignerPort` sobre ``cryptography`` (la
misma librería que usa ``satcfdi.models.Signer`` para firmar), sin depender
del paquete ``satcfdi`` entero.

``cryptography`` es una dependencia opcional::

    pip install "csf-scraper-python[fiel]"

Se importa directamente aquí, como el adaptador de Gemini importa su SDK:
este módulo solo se carga cuando alguien lo pide (ver ``__getattr__`` en
``csf_scraper.download``).
"""

import base64
from typing import cast

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    load_der_private_key,
    pkcs12,
)
from cryptography.x509.oid import NameOID

from csf_scraper.download.exceptions import FielCredentialsException
from csf_scraper.download.value_objects.fiel_credentials import FielCredentials

#: OID del ``x500UniqueIdentifier`` del subject, donde el SAT pone el RFC.
_RFC_OID = NameOID.X500_UNIQUE_IDENTIFIER


class Signer:
    """Certificado FIEL + llave privada, listos para firmar el token del SAT."""

    def __init__(
        self, certificate: x509.Certificate, key: rsa.RSAPrivateKey, *, check: bool = True
    ) -> None:
        self._certificate = certificate
        self._key = key
        if check and not self._public_keys_match():
            raise FielCredentialsException("Private key does not match certificate.")

    @classmethod
    def load(cls, credentials: FielCredentials, *, check: bool = True) -> "Signer":
        """Carga el certificado DER (.cer) y la llave DER cifrada (.key)."""
        try:
            certificate = x509.load_der_x509_certificate(credentials.certificate)
            key = cast(
                rsa.RSAPrivateKey,
                load_der_private_key(data=credentials.key, password=credentials.password_value()),
            )
        except Exception as exception:
            raise FielCredentialsException(
                "Cannot load the FIEL certificate or private key "
                "(check the files and the password)."
            ) from exception
        return cls(certificate, key, check=check)

    @classmethod
    def load_pkcs12(cls, data: bytes, password: str | None = None) -> "Signer":
        """Carga un contenedor PKCS#12 (.pfx/.p12) con certificado y llave."""
        try:
            key, certificate, _ = pkcs12.load_key_and_certificates(
                data=data,
                password=password.encode() if password is not None else None,
            )
        except Exception as exception:
            raise FielCredentialsException("Cannot load the PKCS#12 container.") from exception
        if certificate is None or key is None:
            raise FielCredentialsException("The PKCS#12 container has no certificate or key.")
        return cls(certificate, cast(rsa.RSAPrivateKey, key), check=False)

    @property
    def rfc(self) -> str:
        """RFC del titular, del ``x500UniqueIdentifier`` del certificado."""
        attributes = self._certificate.subject.get_attributes_for_oid(_RFC_OID)
        if not attributes:
            raise FielCredentialsException("The FIEL certificate has no RFC in its subject.")
        return str(attributes[0].value).split("/")[0].strip()

    @property
    def certificate_number(self) -> str:
        """Número de serie, con la misma fórmula que ``satcfdi``."""
        return f"{self._certificate.serial_number:x}"[1::2]

    @property
    def fert(self) -> str:
        """Fecha de vencimiento en el formato que envía ``satcfdi`` al SAT.

        ``satcfdi`` usa ``get_notAfter()[2:]`` sobre el tiempo ASN.1
        generalizado (``YYYYMMDDHHMMSSZ``); eso es ``YYMMDDHHMMSSZ``.
        """
        return self._certificate.not_valid_after_utc.strftime("%y%m%d%H%M%SZ")

    def sign_sha1(self, data: bytes) -> str:
        """Firma ``data`` con PKCS1v15 + SHA-1; devuelve la firma en base64."""
        return self._sign(data, hashes.SHA1())

    def sign_sha256(self, data: bytes) -> str:
        """Firma ``data`` con PKCS1v15 + SHA-256; devuelve la firma en base64."""
        return self._sign(data, hashes.SHA256())

    def _sign(self, data: bytes, algorithm: hashes.HashAlgorithm) -> str:
        signature = self._key.sign(data=data, padding=padding.PKCS1v15(), algorithm=algorithm)
        return base64.b64encode(signature).decode()

    def _public_keys_match(self) -> bool:
        def _key_bytes(key: rsa.RSAPublicKey) -> bytes:
            return key.public_bytes(encoding=Encoding.DER, format=PublicFormat.SubjectPublicKeyInfo)

        return _key_bytes(self._key.public_key()) == _key_bytes(
            self._certificate.public_key()  # type: ignore[arg-type]
        )
