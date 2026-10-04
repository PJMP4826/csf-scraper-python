"""Utilidades para leer los archivos de ``tests/_files`` (equivalente a ``TestCase``)."""

from pathlib import Path

_FILES_DIR = Path(__file__).parent / "_files"


def file_path(filename: str) -> Path:
    """Equivalente a ``TestCase::filePath()``."""
    return _FILES_DIR / filename


def file_contents(filename: str) -> str:
    """Equivalente a ``TestCase::fileContents()`` (vacío si el archivo no existe)."""
    path = file_path(filename)
    return path.read_text(encoding="utf-8") if path.is_file() else ""
