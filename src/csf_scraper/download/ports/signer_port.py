"""Puerto del firmante FIEL.

Contrato mínimo que necesita el login del SAT: el RFC y el número de serie
del certificado, y firmar con SHA-1. Cualquier implementación que lo cumpla
—el :class:`~csf_scraper.download.adapters.signer.Signer` propio o un
adaptador sobre ``satcfdi.models.Signer``— sirve para autenticarse.
"""

from typing import Protocol


class SignerPort(Protocol):
    """Firmante FIEL: certificado + llave privada."""

    @property
    def rfc(self) -> str:
        """RFC del titular, tomado del certificado."""
        ...

    @property
    def certificate_number(self) -> str:
        """Número de serie del certificado, como lo espera el SAT."""
        ...

    @property
    def fert(self) -> str:
        """Fecha de vencimiento del certificado en el formato del SAT."""
        ...

    def sign_sha1(self, data: bytes) -> str:
        """Firma ``data`` con PKCS1v15 + SHA-1; devuelve la firma en base64."""
        ...
