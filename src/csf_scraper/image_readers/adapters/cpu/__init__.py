"""Adaptadores de los lectores de imagen."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from csf_scraper.image_readers.adapters.cpu.open_cv_image_reader import OpenCvImageReader

__all__ = ["OpenCvImageReader"]


def __getattr__(name: str) -> object:
    """Reexporta los adaptadores concretos de forma perezosa."""
    if name == "OpenCvImageReader":
        from csf_scraper.image_readers.adapters.cpu.open_cv_image_reader import OpenCvImageReader

        return OpenCvImageReader

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
