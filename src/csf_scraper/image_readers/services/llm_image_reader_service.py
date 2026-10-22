"""Base común de los adaptadores de imagen basados en un LLM multimodal.

:class:`LlmImageReaderService` concentra exactamente cinco responsabilidades y
nada más:

1. **Armado del prompt** — el texto canónico (:data:`CSF_PROMPT`) más la
   realimentación del intento anterior cuando toca reintentar.
2. **Armado de la imagen del mensaje** — la CSF viaja como un único
   :class:`~llama_index.core.base.llms.types.ImageBlock`.
3. **Reintentos por respuestas inválidas** — cuando los value objects
   :class:`~csf_scraper.value_objects.Rfc` y
   :class:`~csf_scraper.value_objects.IdCif` rechazan el formato de negocio, se
   vuelve a interrogar al modelo pasándole el error como contexto.
4. **Reintentos por errores de API** — cuando el proveedor responde que está
   saturado, caído o inalcanzable, se vuelve a intentar tras una espera
   creciente. El adaptador traduce las excepciones de su proveedor con
   :meth:`LlmImageReaderService._translate_api_exception`, de modo que esta
   clase —y el resto de la librería— nunca importe las excepciones de Gemini,
   OpenAI, etc.
5. **Parseo al DTO** — un :class:`~csf_scraper.image_readers.RfcCifSchema` ya
   tipado se mapea a :class:`~csf_scraper.rfc_cif_data.RfcCifData`.

Lo que **no** vive aquí es el transporte hacia el proveedor ni el acceso al
sistema de archivos. Cada adaptador concreto (``GeminiImageReader``, …) crea su
cliente de LlamaIndex, lo entrega como ``llm_provider`` y expone ``read()``
delegando en el *método plantilla*
:meth:`LlmImageReaderService._run_program`. Ese método arma la imagen y el
prompt de cada intento, ejecuta el ``MultiModalLLMCompletionProgram`` mediante
:meth:`LlmImageReaderService._image_to_schema` y mapea la respuesta a
:class:`~csf_scraper.rfc_cif_data.RfcCifData`. La lectura desde una **ruta** la
hace :class:`~csf_scraper.image_readers.CsfImageExtractor`, que adapta cualquier
:class:`~csf_scraper.image_readers.ImageReaderPort` al contrato público
:class:`~csf_scraper.ports.RfcCifExtractorPort`.
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import ClassVar, cast

import httpx
from llama_index.core.base.llms.types import ImageBlock
from llama_index.core.llms.llm import LLM
from llama_index.core.program import MultiModalLLMCompletionProgram

from csf_scraper.exceptions.image_reader import (
    CifFromImageNotFoundException,
    ImageReaderApiException,
    ImageReaderUnavailableException,
    ImageReadingException,
    RfcFromImageNotFoundException,
)
from csf_scraper.exceptions.value_objects import (
    InvalidIdCifFormatException,
    InvalidRfcFormatException,
)
from csf_scraper.image_readers.adapters.llms.prompts.llm_image_reader_prompt import (
    CSF_PROMPT,
    RETRY_PROMPT,
)
from csf_scraper.image_readers.schemas.rfc_cif_schema import RfcCifSchema
from csf_scraper.rfc_cif_data import RfcCifData
from csf_scraper.value_objects.csf_image import CsfImage
from csf_scraper.value_objects.id_cif import IdCif
from csf_scraper.value_objects.rfc import Rfc

logger = logging.getLogger(__name__)

#: Número de envíos al modelo antes de rendirse.
MAX_RETRIES = 3

#: Espera inicial, en segundos, antes de reintentar tras un error de API. Se
#: duplica en cada intento (1, 2, 4, …) hasta :data:`MAX_RETRY_BACKOFF`.
RETRY_BACKOFF = 1.0

#: Tope de la espera entre reintentos, en segundos.
MAX_RETRY_BACKOFF = 30.0

#: Prompt canónico. Todos los adaptadores LLM parten de este texto.


#: Errores provocados por la *respuesta* del modelo. Se reintentan
#: realimentando el mensaje de error al prompt.
_RESPONSE_ERRORS: tuple[type[Exception], ...] = (
    InvalidRfcFormatException,
    InvalidIdCifFormatException,
    RfcFromImageNotFoundException,
    CifFromImageNotFoundException,
)

#: Errores de transporte genéricos. ``TimeoutError``/``ConnectionError`` vienen
#: de la stdlib y los de ``httpx`` los usan por igual todos los SDK de LLM que
#: esta librería puede albergar; ninguno es específico de un proveedor.
_TRANSPORT_ERRORS: tuple[type[Exception], ...] = (
    TimeoutError,
    ConnectionError,
    httpx.TimeoutException,
    httpx.TransportError,
)


class LlmImageReaderService(ABC):
    """Base de los adaptadores de imagen basados en un LLM multimodal.

    Aporta el *método plantilla* :meth:`_run_program`, que arma el prompt, arma
    la imagen, ejecuta el programa multimodal del proveedor y mapea el resultado
    a :class:`RfcCifData`, reintentando tanto cuando los value objects rechazan
    el formato de negocio de los datos obtenidos como cuando la API del
    proveedor falla de forma temporal.

    El adaptador concreto hereda de esta clase e implementa
    :class:`~csf_scraper.image_readers.ports.ImageReaderPort` exponiendo un
    ``read()`` que delega en :meth:`_run_program` con su propio
    ``llm_provider``::

        class MiImageReader(LlmImageReaderService, ImageReaderPort):
            @property
            def provider(self) -> str:
                return "mi-proveedor"

            async def read(self, image):
                return await self._run_program(
                    image=image, llm_provider=self._llm_provider
                )
    """

    #: Prompt base. Una subclase puede reescribirlo sin tocar la lógica.
    prompt: ClassVar[str] = CSF_PROMPT

    def __init__(
        self,
        *,
        model: str,
        max_retries: int = MAX_RETRIES,
        retry_backoff: float = RETRY_BACKOFF,
    ) -> None:
        if max_retries < 1:
            raise ValueError(f"max_retries must be at least 1, got {max_retries}.")
        if retry_backoff < 0:
            raise ValueError(f"retry_backoff must be zero or positive, got {retry_backoff}.")
        self._model = model
        self._max_retries = max_retries
        self._retry_backoff = retry_backoff

    @property
    def model(self) -> str:
        """Nombre del modelo con el que trabaja el adaptador."""
        return self._model

    @property
    @abstractmethod
    def provider(self) -> str:
        """Identificador del proveedor (``"gemini"``, …)."""

    async def _run_program(self, image: CsfImage, llm_provider: LLM) -> RfcCifData:
        """Lee el RFC y el idCIF de ``image``, reintentando si hace falta.

        Es el *método plantilla*: arma la imagen y el prompt de cada intento,
        delega la ejecución del programa multimodal en :meth:`_image_to_schema`
        y mapea la respuesta a :class:`RfcCifData`.

        Se reintenta en dos casos:

        - **Respuesta inválida**: los value objects rechazan el formato de
          negocio. El error viaja de vuelta al prompt para que el modelo se
          corrija.
        - **Error de API reintentable**: el proveedor está saturado, caído o no
          es alcanzable. Se espera un tiempo creciente (ver
          :data:`RETRY_BACKOFF`) y se repite el *mismo* prompt, porque el
          problema no está en la imagen ni en la respuesta.

        Un error de API no reintentable (credenciales inválidas, petición mal
        formada) o cualquier otra excepción inesperada se propaga de inmediato:
        repetirla daría el mismo resultado.
        """
        image_documents = self._build_image_documents(image)

        previous_error: str | None = None
        last_error: Exception | None = None
        last_cause: Exception | None = None

        for attempt in range(1, self._max_retries + 1):
            retry_prompt = self._build_prompt(previous_error=previous_error, attempt=attempt)

            try:
                schema = await self._image_to_schema(
                    image_documents=image_documents,
                    retry_prompt=retry_prompt,
                    llm_provider=llm_provider,
                )

                return self._to_rfc_cif_data(schema)
            except _RESPONSE_ERRORS as exception:
                last_error = exception
                previous_error = str(exception)
                self._log_retry(attempt, exception)
                # Sin espera: la corrección viaja en el prompt del reintento.
                continue
            except Exception as exception:
                api_error = self._translate_api_exception(exception)
                if api_error is None:
                    raise ImageReadingException(
                        f"The {self.provider} engine failed to read the image.",
                        provider=self.provider,
                        model=self.model,
                    ) from exception
                if not api_error.retryable:
                    raise api_error from exception

                last_error = api_error
                last_cause = exception
                # El error no proviene de la respuesta del modelo: se repite el
                # prompt canónico en lugar de realimentar el fallo de la API.
                previous_error = None
                self._log_retry(attempt, api_error)

            await self._wait_before_retry(attempt)

        if last_error is not None:
            raise last_error from last_cause
        raise ImageReadingException(  # pragma: no cover - max_retries >= 1
            f"The {self.provider} engine did not process the image.",
            provider=self.provider,
            model=self.model,
        )

    def _translate_api_exception(self, exception: Exception) -> ImageReaderApiException | None:
        """Traduce una excepción del proveedor a una de la librería.

        Es el punto de extensión de los adaptadores: cada uno mapea los tipos de
        error de su SDK a :class:`ImageReaderApiException` (o a sus derivadas
        :class:`ImageReaderUnavailableException` y
        :class:`ImageReaderAuthenticationException`), marcando ``retryable``.

        Devolver ``None`` significa «no sé qué es»: la plantilla envuelve la
        excepción original en :class:`ImageReadingException` sin reintentar.

        La implementación base solo reconoce los errores de transporte de la
        stdlib, que no pertenecen a ningún proveedor en particular.
        """
        if isinstance(exception, _TRANSPORT_ERRORS):
            return ImageReaderUnavailableException(
                f"The {self.provider} service is not reachable.",
                provider=self.provider,
                model=self.model,
            )
        return None

    async def _wait_before_retry(self, attempt: int) -> None:
        """Espera un tiempo creciente entre intentos (1, 2, 4, … segundos).

        No espera tras el último intento: ya no queda nada que reintentar.
        """
        if attempt >= self._max_retries:
            return
        delay = self._retry_delay(attempt)
        if delay > 0:
            await asyncio.sleep(delay)

    def _retry_delay(self, attempt: int) -> float:
        """Segundos de espera antes del intento ``attempt + 1``.

        Crece exponencialmente desde ``retry_backoff`` y se topa en
        :data:`MAX_RETRY_BACKOFF` para no esperar indefinidamente.
        """
        if self._retry_backoff == 0:
            return 0.0
        return min(self._retry_backoff * float(2 ** (attempt - 1)), MAX_RETRY_BACKOFF)

    async def _image_to_schema(
        self,
        image_documents: Sequence[ImageBlock],
        retry_prompt: str,
        llm_provider: LLM,
    ) -> RfcCifSchema:
        """Ejecuta el programa multimodal del proveedor para un intento."""
        program = MultiModalLLMCompletionProgram.from_defaults(
            output_cls=RfcCifSchema,
            image_documents=list(image_documents),
            prompt_template_str=retry_prompt,
            multi_modal_llm=llm_provider,
        )
        return cast(RfcCifSchema, await program.acall())

    def _build_image_documents(self, image: CsfImage) -> list[ImageBlock]:
        """Convierte la CSF en el bloque de imagen que consume el programa."""
        return [
            ImageBlock(
                image=image.as_bytes(),
                image_mimetype=image.get_mime_type(),
            )
        ]

    def _to_rfc_cif_data(self, schema: RfcCifSchema) -> RfcCifData:
        """Mapea la respuesta tipada del modelo al DTO de la librería.

        Delega el formato de negocio en :class:`Rfc` y :class:`IdCif`, cuyas
        excepciones disparan el siguiente reintento.
        """
        rfc = schema.rfc.strip()
        id_cif = schema.id_cif.strip()

        if not rfc:
            raise RfcFromImageNotFoundException("The LLM response does not contain an RFC value.")
        if not id_cif:
            raise CifFromImageNotFoundException("The LLM response does not contain an idCIF value.")

        return RfcCifData(rfc=Rfc(rfc), id_cif=IdCif(id_cif))

    def _build_prompt(self, *, previous_error: str | None, attempt: int) -> str:
        """Devuelve el prompt del intento ``attempt``, con realimentación opcional."""
        if previous_error is None:
            return self.prompt
        return self.prompt + RETRY_PROMPT.format(previous_attempt=attempt - 1, error=previous_error)

    def _log_retry(self, attempt: int, exception: Exception) -> None:
        if attempt >= self._max_retries:
            return
        logger.warning(
            "The %s engine could not read the image (attempt %d/%d): %s",
            self.provider,
            attempt,
            self._max_retries,
            exception,
        )
