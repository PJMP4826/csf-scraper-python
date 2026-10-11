"""Utilidades para leer los archivos de ``tests/_files``."""

from pathlib import Path

_FILES_DIR = Path(__file__).parent / "_files"


def file_path(filename: str) -> Path:
    return _FILES_DIR / filename


def file_contents(filename: str) -> str:
    """Contenido del archivo (cadena vacía si no existe)."""
    path = file_path(filename)
    return path.read_text(encoding="utf-8") if path.is_file() else ""
