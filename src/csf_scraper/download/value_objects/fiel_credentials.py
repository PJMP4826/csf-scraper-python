"""Value object de las credenciales FIEL (.cer + .key + contraseña)."""

from dataclasses import dataclass
from pathlib import Path
from typing import Self

from pydantic import SecretStr

from csf_scraper.download.exceptions import FielCredentialsException


@dataclass(frozen=True)
class FielCredentials:
    """Certificado y llave privada de la FIEL, en memoria.

    La contraseña es un :class:`pydantic.SecretStr`: nunca se muestra en
    ``repr``, logs ni mensajes de error. Los bytes del certificado y de la
    llave se leen una sola vez al construir las credenciales; el flujo de
    descarga nunca toca el disco.
    """

    certificate: bytes
    key: bytes
    password: SecretStr | None = None

    def __post_init__(self) -> None:
        if not self.certificate:
            raise FielCredentialsException("The FIEL certificate is empty.")
        if not self.key:
            raise FielCredentialsException("The FIEL private key is empty.")

    @classmethod
    def from_bytes(cls, *, certificate: bytes, key: bytes, password: str | None = None) -> Self:
        """Crea las credenciales desde los bytes del .cer y del .key (DER)."""
        return cls(
            certificate=certificate,
            key=key,
            password=SecretStr(password) if password is not None else None,
        )

    @classmethod
    def from_files(
        cls, *, certificate_path: str, key_path: str, password: str | None = None
    ) -> Self:
        """Lee el .cer y el .key de disco y crea las credenciales."""
        try:
            certificate = Path(certificate_path).read_bytes()
            key = Path(key_path).read_bytes()
        except OSError as exception:
            raise FielCredentialsException(
                "Cannot read the FIEL certificate or key files."
            ) from exception
        return cls.from_bytes(certificate=certificate, key=key, password=password)

    def password_value(self) -> bytes | None:
        """Contraseña como bytes, o ``None`` si la llave no está cifrada."""
        if self.password is None:
            return None
        return self.password.get_secret_value().encode()
