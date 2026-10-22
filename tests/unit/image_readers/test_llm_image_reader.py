"""Pruebas del sub-contrato común de los adaptadores LLM."""

import asyncio
from collections.abc import Sequence

import httpx
import pytest
from llama_index.core.base.llms.types import ImageBlock

from csf_scraper import (
    CSF_PROMPT,
    CifFromImageNotFoundException,
    ImageReaderApiException,
    ImageReaderAuthenticationException,
    ImageReaderUnavailableException,
    ImageReadingException,
    LlmImageReaderService,
    RfcCifData,
    RfcCifSchema,
    RfcFromImageNotFoundException,
)
from csf_scraper.value_objects.csf_image import CsfImage

PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"png-contents"


class _FakeSdkError(Exception):
    """Error genérico del SDK de un proveedor."""


class _FakeLlmReader(LlmImageReaderService):
    """Lector cuyo *hook* devuelve respuestas predefinidas o levanta errores."""

    def __init__(
        self,
        *responses: object,
        max_retries: int = 3,
        retry_backoff: float = 0.0,
        api_errors: dict[type[Exception], ImageReaderApiException] | None = None,
    ) -> None:
        super().__init__(
            model="fake-model",
            max_retries=max_retries,
            retry_backoff=retry_backoff,
        )
        self._responses = list(responses)
        self._api_errors = api_errors or {}
        self.received_documents: list[Sequence[ImageBlock]] = []
        self.received_prompts: list[str] = []

    @property
    def provider(self) -> str:
        return "fake"

    def _translate_api_exception(self, exception: Exception) -> ImageReaderApiException | None:
        for source, target in self._api_errors.items():
            if isinstance(exception, source):
                return target
        return super()._translate_api_exception(exception)

    async def _image_to_schema(
        self,
        image_documents: Sequence[ImageBlock],
        retry_prompt: str,
        llm_provider: object,
    ) -> RfcCifSchema:
        self.received_documents.append(image_documents)
        self.received_prompts.append(retry_prompt)
        response = self._responses.pop(0) if self._responses else None
        if isinstance(response, Exception):
            raise response
        if response is None:
            raise AssertionError("The test did not schedule another response.")
        assert isinstance(response, RfcCifSchema)
        return response

    async def read(self, image: CsfImage) -> RfcCifData:
        return await self._run_program(image=image, llm_provider=object())  # type: ignore[arg-type]


def _schema(rfc: str = "DIM8701081LA", id_cif: str = "12345678") -> RfcCifSchema:
    return RfcCifSchema(rfc=rfc, id_cif=id_cif)


def _image() -> CsfImage:
    return CsfImage.new_from_contents(PNG_BYTES)


def test_reader_returns_the_mapped_dto() -> None:
    reader = _FakeLlmReader(_schema())

    data = asyncio.run(reader.read(_image()))

    assert data == RfcCifData(rfc="DIM8701081LA", id_cif="12345678")


def test_reader_builds_a_single_image_block() -> None:
    reader = _FakeLlmReader(_schema())

    asyncio.run(reader.read(_image()))

    documents = reader.received_documents[0]
    assert len(documents) == 1
    assert documents[0].image_mimetype == "image/png"


def test_reader_sends_the_canonical_prompt_first() -> None:
    reader = _FakeLlmReader(_schema())

    asyncio.run(reader.read(_image()))

    assert reader.received_prompts[0] == CSF_PROMPT


def test_reader_retries_and_feeds_the_error_back() -> None:
    reader = _FakeLlmReader(
        RfcFromImageNotFoundException("no rfc in sight"),
        _schema(),
    )

    data = asyncio.run(reader.read(_image()))

    assert data.rfc == "DIM8701081LA"
    assert len(reader.received_prompts) == 2
    assert "no rfc in sight" in reader.received_prompts[1]
    assert "#1" in reader.received_prompts[1]


def test_reader_retries_on_invalid_business_format() -> None:
    reader = _FakeLlmReader(_schema(rfc="NO-ES-RFC"), _schema())

    data = asyncio.run(reader.read(_image()))

    assert data.rfc == "DIM8701081LA"
    assert len(reader.received_prompts) == 2


def test_reader_raises_the_last_error_when_attempts_run_out() -> None:
    reader = _FakeLlmReader(
        CifFromImageNotFoundException("first"),
        CifFromImageNotFoundException("last"),
        max_retries=2,
    )

    with pytest.raises(CifFromImageNotFoundException) as error:
        asyncio.run(reader.read(_image()))

    assert str(error.value) == "last"
    assert len(reader.received_prompts) == 2


def test_reader_wraps_unexpected_errors() -> None:
    reader = _FakeLlmReader(RuntimeError("boom"), max_retries=1)

    with pytest.raises(ImageReadingException) as error:
        asyncio.run(reader.read(_image()))

    assert error.value.provider == "fake"
    assert error.value.model == "fake-model"
    assert isinstance(error.value.__cause__, RuntimeError)


def test_reader_does_not_retry_unexpected_errors() -> None:
    reader = _FakeLlmReader(RuntimeError("boom"), _schema(), max_retries=3)

    with pytest.raises(ImageReadingException):
        asyncio.run(reader.read(_image()))

    assert len(reader.received_prompts) == 1


def _unavailable(status_code: int = 503) -> ImageReaderUnavailableException:
    return ImageReaderUnavailableException(
        "saturado", provider="fake", model="fake-model", status_code=status_code
    )


def test_reader_retries_on_a_retryable_api_error() -> None:
    reader = _FakeLlmReader(
        _FakeSdkError("boom"),
        _schema(),
        api_errors={_FakeSdkError: _unavailable()},
    )

    data = asyncio.run(reader.read(_image()))

    assert data.rfc == "DIM8701081LA"
    assert len(reader.received_prompts) == 2


def test_reader_repeats_the_canonical_prompt_after_an_api_error() -> None:
    reader = _FakeLlmReader(
        _FakeSdkError("boom"),
        _schema(),
        api_errors={_FakeSdkError: _unavailable()},
    )

    asyncio.run(reader.read(_image()))

    assert reader.received_prompts[1] == CSF_PROMPT


def test_reader_raises_the_api_error_when_attempts_run_out() -> None:
    reader = _FakeLlmReader(
        _FakeSdkError("boom"),
        _FakeSdkError("boom"),
        max_retries=2,
        api_errors={_FakeSdkError: _unavailable()},
    )

    with pytest.raises(ImageReaderUnavailableException) as error:
        asyncio.run(reader.read(_image()))

    assert error.value.status_code == 503
    assert isinstance(error.value.__cause__, _FakeSdkError)
    assert len(reader.received_prompts) == 2


def test_reader_does_not_retry_a_non_retryable_api_error() -> None:
    rejected = ImageReaderAuthenticationException(
        "clave inválida", provider="fake", model="fake-model", status_code=401
    )
    reader = _FakeLlmReader(
        _FakeSdkError("boom"),
        _schema(),
        api_errors={_FakeSdkError: rejected},
    )

    with pytest.raises(ImageReaderAuthenticationException):
        asyncio.run(reader.read(_image()))

    assert len(reader.received_prompts) == 1


def test_reader_retries_on_transport_errors() -> None:
    reader = _FakeLlmReader(httpx.ConnectError("connection refused"), _schema())

    data = asyncio.run(reader.read(_image()))

    assert data.rfc == "DIM8701081LA"
    assert len(reader.received_prompts) == 2


def test_reader_reports_transport_errors_as_unavailable() -> None:
    reader = _FakeLlmReader(TimeoutError("timed out"), max_retries=1)

    with pytest.raises(ImageReaderUnavailableException) as error:
        asyncio.run(reader.read(_image()))

    assert error.value.retryable is True
    assert error.value.provider == "fake"


def test_reader_grows_the_backoff_and_caps_it() -> None:
    reader = _FakeLlmReader(_schema(), max_retries=8, retry_backoff=1.0)

    delays = [reader._retry_delay(attempt) for attempt in range(1, 8)]

    assert delays == [1.0, 2.0, 4.0, 8.0, 16.0, 30.0, 30.0]


def test_reader_rejects_a_non_positive_retry_budget() -> None:
    with pytest.raises(ValueError, match="max_retries must be at least 1"):
        _FakeLlmReader(_schema(), max_retries=0)


def test_reader_rejects_a_negative_backoff() -> None:
    with pytest.raises(ValueError, match="retry_backoff must be zero or positive"):
        _FakeLlmReader(_schema(), retry_backoff=-1.0)


def test_reader_exposes_provider_and_model() -> None:
    reader = _FakeLlmReader(_schema())

    assert reader.provider == "fake"
    assert reader.model == "fake-model"


def test_reader_reads_asynchronously() -> None:
    reader = _FakeLlmReader(_schema())

    data = asyncio.run(reader.read(_image()))

    assert data.rfc == "DIM8701081LA"


def test_schema_describes_both_fields_for_the_model() -> None:
    schema = RfcCifSchema.model_json_schema()

    assert "rfc" in schema["properties"]
    assert "id_cif" in schema["properties"]
    assert schema["properties"]["rfc"]["description"]
    assert schema["properties"]["id_cif"]["description"]
