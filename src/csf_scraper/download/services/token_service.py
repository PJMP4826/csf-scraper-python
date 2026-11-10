"""Generación del token de autenticación FIEL del SAT.

Copia tipada de ``generate_token`` de ``SAT-CFDI/python-satcfdi``
(``satcfdi/portal/utils.py``): el token es ``guid|RFC|nº de serie``,
firmado con SHA-1 y codificado en doble base64. Es una función pura, sin
red, por lo que se puede probar con un certificado de prueba.
"""

import base64

from csf_scraper.download.ports.signer_port import SignerPort


def generate_token(signer: SignerPort, code: str) -> bytes:
    """Genera el token FIEL para el ``guid`` que entregó el SAT."""
    signed = f"{code}|{signer.rfc}|{signer.certificate_number}"
    signature = signer.sign_sha1(data=signed.encode())
    return base64.b64encode(
        base64.b64encode(signed.encode()) + b"#" + base64.b64encode(signature.encode())
    )
