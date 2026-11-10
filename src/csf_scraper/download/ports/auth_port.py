"""Puerto de autenticación contra el portal del SAT."""

from abc import ABC, abstractmethod

import httpx


class AuthPort(ABC):
    """Autentica una sesión del SAT con el cliente HTTP compartido.

    La implementación concreta decide el mecanismo (FIEL hoy; CIEC +
    CAPTCHA en el futuro). El orquestador solo conoce este contrato, así
    que cambiar de mecanismo no toca el resto del flujo de descarga.
    """

    @abstractmethod
    async def login(self, client: httpx.AsyncClient) -> None:
        """Inicia sesión en el SAT con ``client`` (cookies compartidas)."""
        ...

    @abstractmethod
    async def logout(self, client: httpx.AsyncClient) -> None:
        """Cierra la sesión en el SAT. Se llama siempre, incluso si falla la descarga."""
        ...
