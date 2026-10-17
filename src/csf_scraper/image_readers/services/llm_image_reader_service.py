"""Base común de los adaptadores de imagen basados en un LLM multimodal.

:class:`LlmImageReaderService` concentra exactamente cuatro responsabilidades y
nada más:

1. **Armado del prompt** — el texto canónico (:data:`CSF_PROMPT`) más la
   realimentación del intento anterior cuando toca reintentar.
2. **Armado de la imagen del mensaje** — la CSF viaja como un único
   :class:`~llama_index.core.base.llms.types.ImageBlock`.
3. **Reintentos** — cuando los value objects :class:`~csf_scraper.value_objects.Rfc`
   y :class:`~csf_scraper.value_objects.IdCif` rechazan el formato de negocio,
   se vuelve a interrogar al modelo pasándole el error como contexto.
4. **Parseo al DTO** — un :class:`~csf_scraper.image_readers.RfcCifSchema` ya
   tipado se mapea a :class:`~csf_scraper.rfc_cif_data.RfcCifData`.

Lo que **no** vive aquí es el transporte hacia el proveedor ni el acceso al
sistema de archivos. Cada adaptador concreto (``GeminiImageReader``, …) importa
su cliente de LlamaIndex y ejecuta su propio
``MultiModalLLMCompletionProgram`` en el *hook*
:meth:`LlmImageReaderService._run_program`; y la lectura desde una **ruta** la hace
:class:`~csf_scraper.image_readers.CsfImageExtractor`, que adapta cualquier
:class:`~csf_scraper.image_readers.ImageReaderPort` al contrato público
:class:`~csf_scraper.ports.RfcCifExtractorPort`.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import ClassVar, cast

from llama_index.core.base.llms.types import ImageBlock
from llama_index.core.program import MultiModalLLMCompletionProgram
from llama_index.core.llms.llm import LLM

from csf_scraper.exceptions.image_reader import (
    CifFromImageNotFoundException,
    ImageReadingException,
    RfcFromImageNotFoundException,
)
from csf_scraper.exceptions.value_objects import (
    InvalidIdCifFormatException,
    InvalidRfcFormatException,
)
from csf_scraper.image_readers.schemas.rfc_cif_schema import RfcCifSchema
from csf_scraper.rfc_cif_data import RfcCifData
from csf_scraper.value_objects.csf_image import CsfImage
from csf_scraper.value_objects.id_cif import IdCif
from csf_scraper.value_objects.rfc import Rfc

logger = logging.getLogger(__name__)

#: Número de envíos al modelo antes de rendirse.
MAX_RETRIES = 3

#: Prompt canónico. Todos los adaptadores LLM parten de este texto.
CSF_PROMPT = (
    "Analiza la imagen adjunta, que es una Constancia de Situación Fiscal "
    "emitida por el SAT, y extrae el RFC y el idCIF que aparecen en el "
    "encabezado del documento. Transcribe ambos valores exactamente como están "
    "impresos: conserva las mayúsculas, el signo & y la Ñ si aparecen, y no "
    "elimines los ceros a la izquierda del idCIF. No inventes ni completes "
    "valores: si un dato no se distingue en la imagen, devuélvelo como cadena "
    "vacía."
)

#: Sufijo que se agrega al prompt cuando el intento anterior fue rechazado.
RETRY_PROMPT = (
    "\n\nATENCIÓN: el intento #{previous_attempt} fue descartado por este "
    "motivo:\n{error}\n\n"
    "Vuelve a revisar la imagen con cuidado, carácter por carácter, y corrige "
    "exactamente eso antes de responder."
)

#: Errores provocados por la *respuesta* del modelo. Se reintentan
#: realimentando el mensaje de error al prompt.
_RESPONSE_ERRORS: tuple[type[Exception], ...] = (
    InvalidRfcFormatException,
    InvalidIdCifFormatException,
    RfcFromImageNotFoundException,
    CifFromImageNotFoundException,
)


class LlmImageReaderService(ABC):
    """Base de los adaptadores de imagen basados en un LLM multimodal.

    Implementa el *template method* de
    :class:`~csf_scraper.image_readers.ports.ImageReaderPort`: arma el prompt,
    arma la imagen, ejecuta el programa multimodal del adaptador y mapea el
    resultado a :class:`RfcCifData`, reintentando cuando los value objects
    rechazan el formato de negocio de los datos obtenidos.

    El método público :meth:`read` es una corrutina: todo el flujo de la
    librería es asíncrono.

    Una subclase solo declara :attr:`provider` e implementa
    :meth:`_run_program`, que es donde vive el cliente de LlamaIndex::

        class MiImageReader(LlmImageReaderService):
            @property
            def provider(self) -> str:
                return "mi-proveedor"

            async def _run_program(self, image_documents, prompt):
                program = MultiModalLLMCompletionProgram.from_defaults(...)
                return cast(RfcCifSchema, await program.acall())
    """

    #: Prompt base. Una subclase puede reescribirlo sin tocar la lógica.
    prompt: ClassVar[str] = CSF_PROMPT

    def __init__(self, *, model: str, max_retries: int = MAX_RETRIES) -> None:
        if max_retries < 1:
            raise ValueError(f"max_retries must be at least 1, got {max_retries}.")
        self._model = model
        self._max_retries = max_retries

    @property
    def model(self) -> str:
        """Nombre del modelo con el que trabaja el adaptador."""
        return self._model

    @property
    @abstractmethod
    def provider(self) -> str:
        """Identificador del proveedor (``"gemini"``, ``"deepseek"``, …)."""

    async def _run_program(self, image: CsfImage, llm_provider: LLM) -> RfcCifData:
        """Lee el RFC y el idCIF de ``image``, reintentando si hace falta.

        Es el *template method*: arma la imagen, arma el prompt de cada intento,
        delega el transporte en :meth:`_run_program` y mapea la respuesta a
        :class:`RfcCifData`.
        """
        image_documents = self._build_image_documents(image)

        previous_error: str | None = None
        last_error: Exception | None = None

        for attempt in range(1, self._max_retries + 1):
            retry_prompt = self._build_prompt(
                previous_error=previous_error, attempt=attempt
            )

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
            except Exception as exception:
                raise ImageReadingException(
                    f"The {self.provider} engine failed to read the image.",
                    provider=self.provider,
                    model=self.model,
                ) from exception

        if last_error is not None:
            raise last_error
        raise ImageReadingException(  # pragma: no cover - max_retries >= 1
            f"The {self.provider} engine did not process the image.",
            provider=self.provider,
            model=self.model,
        )

    async def _image_to_schema(
        self,
        image_documents: Sequence[ImageBlock],
        retry_prompt: str,
        llm_provider: LLM,
    ) -> RfcCifSchema:
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
            raise RfcFromImageNotFoundException(
                "The LLM response does not contain an RFC value."
            )
        if not id_cif:
            raise CifFromImageNotFoundException(
                "The LLM response does not contain an idCIF value."
            )

        return RfcCifData(rfc=Rfc(rfc), id_cif=IdCif(id_cif))

    def _build_prompt(self, *, previous_error: str | None, attempt: int) -> str:
        """Devuelve el prompt del intento ``attempt``, con realimentación opcional."""
        if previous_error is None:
            return self.prompt
        return self.prompt + RETRY_PROMPT.format(
            previous_attempt=attempt - 1, error=previous_error
        )

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
