"""Adaptadores de los lectores de imagen."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from csf_scraper.image_readers.adapters.llms import GeminiImageReader

__all__ = ["GeminiImageReader"]


def __getattr__(name: str) -> object:
    """Reexporta los adaptadores concretos de forma perezosa."""
    if name == "GeminiImageReader":
        from csf_scraper.image_readers.adapters.llms import GeminiImageReader

        return GeminiImageReader

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
