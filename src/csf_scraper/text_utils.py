"""Utilidades de compatibilidad con las funciones de texto de PHP.

Equivalencias:
- ``php_trim()`` → ``trim()`` con su charlist por omisión.
- ``normalize_white_spaces()`` → ``preg_replace('/\\s+/', ' ', trim($str))``.
- ``xml_normalize_space()`` → la función ``normalize-space()`` de XPath.
"""

import re

#: Charlist por omisión de ``trim()`` de PHP (no incluye ``\\f`` ni ``\\xA0``).
_PHP_TRIM_CHARS = " \t\n\r\x00\x0b"
#: Clase ``\\s`` de PCRE: espacio, ``\\t``, ``\\n``, ``\\f``, ``\\v``, ``\\r``.
_PCRE_WHITESPACE = re.compile(r"[ \t\n\r\f\v]+")
#: Espacios del conjunto de espacios en blanco de XML.
_XML_WHITESPACE = re.compile(r"[ \t\n\r]+")


def php_trim(value: str) -> str:
    """Equivalente a ``trim($value)`` de PHP con su charlist por omisión."""
    return value.strip(_PHP_TRIM_CHARS)


def normalize_white_spaces(value: str) -> str:
    """Equivalente a ``preg_replace('/\\s+/', ' ', trim($value))``."""
    return _PCRE_WHITESPACE.sub(" ", php_trim(value))


def xml_normalize_space(value: str) -> str:
    """Equivalente a la función ``normalize-space()`` de XPath."""
    return _XML_WHITESPACE.sub(" ", value).strip(" \t\n\r")
