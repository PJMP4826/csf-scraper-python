"""Pruebas del sub-contrato común de los adaptadores LLM."""

import asyncio
from collections.abc import Sequence

import pytest
from llama_index.core.base.llms.types import ImageBlock

from csf_scraper import (
    CSF_PROMPT,
    CifFromImageNotFoundException,
    ImageReadingException,
    LlmImageReaderService,
    RfcCifData,
    RfcCifSchema,
    RfcFromImageNotFoundException,
)
from csf_scraper.value_objects.csf_image import CsfImage

PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"png-contents"


class _FakeLlmReader(LlmImageReaderService):
    """Lector cuyo *hook* devuelve respuestas predefinidas o levanta errores."""

    def __init__(
        self,
        *responses: object,
        max_retries: int = 3,
    ) -> None:
        super().__init__(model="fake-model", max_retries=max_retries)
        self._responses = list(responses)
        self.received_documents: list[Sequence[ImageBlock]] = []
        self.received_prompts: list[str] = []

    @property
    def provider(self) -> str:
        return "fake"

    async def _run_program(
        self, image_documents: Sequence[ImageBlock], prompt: str
    ) -> RfcCifSchema:
        self.received_documents.append(image_documents)
        self.received_prompts.append(prompt)
        response = self._responses.pop(0) if self._responses else None
        if isinstance(response, Exception):
            raise response
        if response is None:
            raise AssertionError("The test did not schedule another response.")
        assert isinstance(response, RfcCifSchema)
        return response


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


def test_reader_wraps_transport_errors() -> None:
    reader = _FakeLlmReader(RuntimeError("boom"), max_retries=1)

    with pytest.raises(ImageReadingException) as error:
        asyncio.run(reader.read(_image()))

    assert error.value.provider == "fake"
    assert error.value.model == "fake-model"
    assert isinstance(error.value.__cause__, RuntimeError)


def test_reader_does_not_retry_transport_errors() -> None:
    reader = _FakeLlmReader(RuntimeError("boom"), _schema(), max_retries=3)

    with pytest.raises(ImageReadingException):
        asyncio.run(reader.read(_image()))

    assert len(reader.received_prompts) == 1


def test_reader_rejects_a_non_positive_retry_budget() -> None:
    with pytest.raises(ValueError, match="max_retries must be at least 1"):
        _FakeLlmReader(_schema(), max_retries=0)


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
