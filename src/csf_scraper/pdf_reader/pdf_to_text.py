"""Conversión de PDF a texto mediante el binario ``pdftotext``."""

import asyncio
import subprocess

from csf_scraper.exceptions.pdf_reader import PdfToTextConvertException


class PdfToText:
    """Extrae el contenido de un PDF usando ``pdftotext`` (paquete ``poppler-utils``)."""

    def __init__(self, executable: str = "pdftotext") -> None:
        self._executable = executable

    async def extract(self, path: str) -> str:
        """Devuelve el texto del PDF; lanza :class:`PdfToTextConvertException` si falla.

        ``pdftotext`` es un proceso externo y bloqueante, así que se ejecuta en
        un hilo aparte con :func:`asyncio.to_thread`; el bucle de eventos sigue
        libre mientras el binario convierte el archivo.
        """
        command = self.build_command(path)
        result = await asyncio.to_thread(subprocess.run, command, capture_output=True, check=False)
        if result.returncode != 0:
            raise PdfToTextConvertException(
                f"Running pdftotext exit with error (exit code {result.returncode})",
                command,
                result.returncode,
                result.stdout.decode("utf-8", errors="replace"),
                result.stderr.decode("utf-8", errors="replace"),
            )
        return result.stdout.decode("utf-8", errors="replace")

    def build_command(self, pdf_file: str) -> list[str]:
        """Argumentos con los que se invoca a ``pdftotext``."""
        return [self._executable, "-eol", "unix", "-raw", "-q", pdf_file, "-"]
