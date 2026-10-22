"""Adaptadores de lectura de imágenes basados en LLMs multimodales.

Este paquete es el único lugar de la librería que conoce el SDK de un
proveedor concreto. Por eso **no** se importa ningún adaptador al cargar el
paquete: :class:`GeminiImageReader` requiere el extra ``llm-gemini`` y debe
resolverse solo cuando se usa (:pep:`562`), para que ``import csf_scraper``
funcione sin instalar extras.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from csf_scraper.image_readers.adapters.llms.gemini_image_reader import (
        GeminiImageReader,
    )

__all__ = ["GeminiImageReader"]


def __getattr__(name: str) -> object:
    """Resuelve :class:`GeminiImageReader` de forma perezosa.

    Levanta ``ModuleNotFoundError`` (del paquete ``llama-index-llms-google-genai``)
    si se pide el adaptador sin haber instalado el extra ``llm-gemini``.
    """
    if name == "GeminiImageReader":
        from csf_scraper.image_readers.adapters.llms.gemini_image_reader import (
            GeminiImageReader,
        )

        return GeminiImageReader

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
