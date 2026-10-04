"""Extracción de datos del HTML del CSF (migración de ``src/DataExtractor.php``)."""

import re

from bs4 import BeautifulSoup, Tag

from csf_scraper.exceptions import CifNotFoundException
from csf_scraper.interfaces import DataExtractorInterface
from csf_scraper.persona_fisica import PersonaFisica
from csf_scraper.persona_moral import PersonaMoral
from csf_scraper.regimen import Regimen

_XML_DECLARATION = '<?xml version="1.0" encoding="UTF-8" ?>'
#: Charlist por omisión de ``trim()`` de PHP (no incluye ``\\f`` ni ``\\xA0``).
_PHP_TRIM_CHARS = " \t\n\r\x00\x0b"
#: Clase ``\\s`` de PCRE: espacio, ``\\t``, ``\\n``, ``\\f``, ``\\v``, ``\\r``.
_PCRE_WHITESPACE = re.compile(r"[ \t\n\r\f\v]+")
#: Espacios del conjunto de espacios en blanco de XML (``normalize-space()``).
_XML_WHITESPACE = re.compile(r"[ \t\n\r]+")


def _php_trim(value: str) -> str:
    """Equivalente a ``trim($value)`` de PHP con su charlist por omisión."""
    return value.strip(_PHP_TRIM_CHARS)


def _normalize_white_spaces(value: str) -> str:
    """Equivalente a ``DataExtractor::normalizeWhiteSpaces()`` (``trim`` + ``\\s+``)."""
    return _PCRE_WHITESPACE.sub(" ", _php_trim(value))


def _xml_normalize_space(value: str) -> str:
    """Equivalente a la función ``normalize-space()`` de XPath."""
    return _XML_WHITESPACE.sub(" ", value).strip(" \t\n\r")


def _text_content(node: Tag) -> str:
    """Equivalente a ``DOMNode::$textContent`` del nodo."""
    return node.get_text()


def _row_text_content(node: Tag) -> str:
    """Equivalente a ``$node->parentNode->parentNode->textContent ?? ''``."""
    parent = node.parent
    row = parent.parent if parent is not None else None
    return "" if row is None else _text_content(row)


class DataExtractor(DataExtractorInterface):
    """Extrae los datos de una persona a partir del HTML de la consulta del CSF.

    Equivalente a ``PhpCfdi\\CsfScraper\\DataExtractor`` (clase ``final readonly``).
    """

    def __init__(self, html: str) -> None:
        self.html = html

    def extract(self, is_fisica: bool) -> PersonaMoral | PersonaFisica:
        """Equivalente a ``DataExtractor::extract()``; lanza ``CifNotFoundException``."""
        html = self._clear_html(self.html)
        person: PersonaMoral | PersonaFisica = PersonaFisica() if is_fisica else PersonaMoral()

        soup = BeautifulSoup(html, "lxml")
        error_element = soup.select("span[class=ui-messages-info-detail]")
        if len(error_element) == 1:
            raise CifNotFoundException("Failed to found CIF info.")

        for property_name, text in person.get_td_titles_text_to_search().items():
            setattr(person, property_name, self._get_value_by_td_title_text(soup, text))

        regimenes = self._get_regimenes(soup)
        if regimenes:
            person.add_regimenes(*regimenes)

        return person

    def _get_value_by_td_title_text(self, soup: BeautifulSoup, value_to_search: str) -> str:
        """Equivalente a ``DataExtractor::getValueByTdTitleText()``."""
        node: Tag | None = None
        for element in soup.select('td[role="gridcell"] > span'):
            if value_to_search in _xml_normalize_space(_text_content(element)):
                node = element
                break
        if node is None:
            return ""
        return _php_trim(
            _normalize_white_spaces(_row_text_content(node)).replace(value_to_search, " "),
        )

    def _clear_html(self, html: str) -> str:
        """Equivalente a ``DataExtractor::clearHtml()``."""
        return html.replace(_XML_DECLARATION, "")

    def _get_regimenes(self, soup: BeautifulSoup) -> list[Regimen]:
        """Equivalente a ``DataExtractor::getRegimenes()`` (la quinta tabla ``tbody``)."""
        regimenes: list[Regimen] = []
        values_count = 0
        tbodies = soup.select('tbody[class="ui-datatable-data ui-widget-content"]')
        for index, element in enumerate(tbodies):
            if index != 4:
                continue
            for child in element.select('td[role="gridcell"]'):
                if child.select("span"):
                    continue
                value = _normalize_white_spaces(_text_content(child))
                local_index = values_count // 2
                if values_count % 2 == 0:
                    regimen = Regimen()
                    regimen.set_regimen(value)
                    regimenes.append(regimen)
                else:
                    regimenes[local_index].set_fecha_alta(value)
                values_count += 1
        return regimenes
