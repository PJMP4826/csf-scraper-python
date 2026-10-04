"""Conversión de PDF a texto con ``pdftotext`` (migración de ``src/PdfReader/PdfToText.php``)."""

import subprocess

from csf_scraper.exceptions.pdf_reader import PdfToTextConvertException


class PdfToText:
    """Extrae el contenido de un PDF usando ``pdftotext`` (paquete ``poppler-utils``).

    Equivalente a ``PhpCfdi\\CsfScraper\\PdfReader\\PdfToText`` (clase ``final readonly``).
    """

    def __init__(self, path_pdf_to_text: str = "") -> None:
        self._pdftotext = path_pdf_to_text if path_pdf_to_text != "" else "pdftotext"

    def extract(self, path: str) -> str:
        """Equivalente a ``extract()``; lanza ``PdfToTextConvertException`` si falla."""
        command = self.build_command(path)
        result = subprocess.run(command, capture_output=True, check=False)
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
        """Equivalente a ``buildCommand()``: argumentos de ``pdftotext``."""
        return [self._pdftotext, "-eol", "unix", "-raw", "-q", pdf_file, "-"]
