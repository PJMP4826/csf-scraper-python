"""Adaptador del lector de imágenes basado en Gemini (Google GenAI).

Aquí sí se importan las librerías de LlamaIndex y del SDK de Google, porque el
transporte hacia el proveedor es responsabilidad exclusiva del adaptador::

    from llama_index.llms.google_genai import GoogleGenAI

    reader = GeminiImageReader(api_key="…", model_name="gemini-2.5-flash")

El paquete ``llama-index-llms-google-genai`` es una dependencia opcional
(``pip install csf-scraper[llm-gemini]``).

Las excepciones de ``google.genai.errors`` se traducen en
:meth:`GeminiImageReader._translate_api_exception` a excepciones de la librería,
de modo que fuera de este archivo nadie necesita conocer el SDK de Google.
"""

from __future__ import annotations

from google.genai import errors
from llama_index.llms.google_genai import GoogleGenAI

from csf_scraper.exceptions.image_reader import (
    ImageReaderApiException,
    ImageReaderAuthenticationException,
    ImageReaderUnavailableException,
)
from csf_scraper.rfc_cif_data import RfcCifData
from csf_scraper.value_objects.csf_image import CsfImage
from csf_scraper.image_readers.ports.image_reader_port import ImageReaderPort
from csf_scraper.image_readers.schemas.rfc_cif_schema import RfcCifSchema
from csf_scraper.image_readers.services.llm_image_reader_service import (
    MAX_RETRIES,
    RETRY_BACKOFF,
    LlmImageReaderService,
)

#: Códigos HTTP de Google que indican una falla temporal del servicio: el
#: límite de peticiones (429), los errores del servidor (5xx) y los timeouts de
#: la propia API (408).
_RETRYABLE_STATUS_CODES = frozenset({408, 429, 500, 502, 503, 504})

#: Estados de Google que también indican una falla temporal, por si la
#: respuesta llega sin un código HTTP reconocible.
_RETRYABLE_STATUSES = frozenset(
    {
        "RESOURCE_EXHAUSTED",
        "INTERNAL",
        "UNAVAILABLE",
        "DEADLINE_EXCEEDED",
        "ABORTED",
        "UNKNOWN",
    }
)

#: Estados que indican que las credenciales no sirven: reintentar con la misma
#: clave daría exactamente el mismo error.
_AUTHENTICATION_STATUSES = frozenset({"UNAUTHENTICATED", "PERMISSION_DENIED"})


class GeminiImageReader(LlmImageReaderService, ImageReaderPort):
    """Lee el RFC y el idCIF de una imagen de CSF usando Gemini.

    Hereda de :class:`~csf_scraper.image_readers.services.LlmImageReaderService`
    el prompt, el armado de la imagen, los reintentos, la ejecución del
    programa multimodal y el mapeo a
    :class:`~csf_scraper.rfc_cif_data.RfcCifData`. Lo propio de este adaptador
    es crear el cliente ``GoogleGenAI``, traducir los errores del SDK y exponer
    ``read()`` delegando en el método plantilla de la clase base.

    Args:
        api_key: Clave de la API de Google GenAI.
        model_name: Modelo de Gemini a utilizar.
        max_retries: Intentos totales antes de rendirse.
        retry_backoff: Espera inicial, en segundos, entre reintentos por errores
            de API; se duplica en cada intento.
    """

    def __init__(
        self,
        api_key: str,
        model_name: str,
        *,
        max_retries: int = MAX_RETRIES,
        retry_backoff: float = RETRY_BACKOFF,
    ) -> None:
        if not api_key:
            raise ValueError("The Gemini image reader requires an API key.")

        if not model_name:
            raise ValueError("The Gemini image reader requires an Model Name.")
        super().__init__(
            model=model_name,
            max_retries=max_retries,
            retry_backoff=retry_backoff,
        )
        self._llm_provider = GoogleGenAI(api_key=api_key, model=model_name)

    @property
    def provider(self) -> str:
        """Identificador del proveedor."""
        return "gemini"

    async def read(self, image: CsfImage) -> RfcCifData:
        """Delega el flujo de reintentos y mapeo en el método plantilla."""
        return await self._run_program(image=image, llm_provider=self._llm_provider)

    def _translate_api_exception(
        self, exception: Exception
    ) -> ImageReaderApiException | None:
        """Traduce ``google.genai.errors`` a excepciones de la librería.

        - Credenciales rechazadas (401/403) →
          :class:`ImageReaderAuthenticationException`, **sin** reintentar.
        - Saturación, caída o timeout (429, 408, 5xx) →
          :class:`ImageReaderUnavailableException`, **con** reintento.
        - Cualquier otro error de la API →
          :class:`ImageReaderApiException` con ``retryable=False``.

        Los errores de transporte genéricos (``httpx``, timeouts) los resuelve
        la implementación base.
        """
        translated = super()._translate_api_exception(exception)
        if translated is not None:
            return translated

        if not isinstance(exception, errors.APIError):
            return None

        status_code = exception.code or None
        status = (exception.status or "").upper()
        print(status_code)
        print(status)

        if status_code in {401, 403} or status in _AUTHENTICATION_STATUSES:
            return ImageReaderAuthenticationException(
                f"The {self.provider} API rejected the credentials: "
                f"{exception.message or status_code}",
                provider=self.provider,
                model=self.model,
                status_code=status_code,
            )

        if status_code in _RETRYABLE_STATUS_CODES or status in _RETRYABLE_STATUSES:
            return ImageReaderUnavailableException(
                f"The {self.provider} API is temporarily unavailable: "
                f"{exception.message or status_code}",
                provider=self.provider,
                model=self.model,
                status_code=status_code,
            )

        return ImageReaderApiException(
            f"The {self.provider} API returned an error: "
            f"{exception.message or status_code}",
            provider=self.provider,
            model=self.model,
            status_code=status_code,
            retryable=False,
        )
