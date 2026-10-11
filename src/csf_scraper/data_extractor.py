"""Extracción de datos fiscales a partir del HTML de la consulta del CSF."""

from bs4 import BeautifulSoup, Tag

from csf_scraper.exceptions import CifNotFoundException
from csf_scraper.persona_fisica import PersonaFisica
from csf_scraper.persona_moral import PersonaMoral
from csf_scraper.regimen import Regimen

_XML_DECLARATION = '<?xml version="1.0" encoding="UTF-8" ?>'


def _normalize_whitespace(value: str) -> str:
    """Colapsa cualquier espacio en blanco en un único espacio y recorta los extremos."""
    return " ".join(value.split())


class DataExtractor:
    """Extrae los datos de una persona desde el HTML de la consulta del CSF."""

    def __init__(self, html: str) -> None:
        self.html = html

    def extract(self, is_fisica: bool) -> PersonaMoral | PersonaFisica:
        """Construye la persona correspondiente; lanza :class:`CifNotFoundException`."""
        person: PersonaMoral | PersonaFisica = PersonaFisica() if is_fisica else PersonaMoral()
        soup = BeautifulSoup(self._clear_html(self.html), "lxml")

        if soup.select("span[class=ui-messages-info-detail]"):
            raise CifNotFoundException("Failed to found CIF info.")

        fields = type(person).model_fields
        for field, title in person.field_titles.items():
            value = self._find_value(soup, title)
            if field in fields:
                setattr(person, field, value)
            else:
                person.extra_data[field] = value

        person.regimenes = self._get_regimenes(soup)
        return person

    def _find_value(self, soup: BeautifulSoup, title: str) -> str:
        for element in soup.select('td[role="gridcell"] > span'):
            if title not in _normalize_whitespace(element.get_text()):
                continue
            row = element.find_parent("tr")
            text = _normalize_whitespace(row.get_text()) if isinstance(row, Tag) else ""
            return text.replace(title, " ").strip()
        return ""

    @staticmethod
    def _clear_html(html: str) -> str:
        return html.replace(_XML_DECLARATION, "")

    @staticmethod
    def _get_regimenes(soup: BeautifulSoup) -> list[Regimen]:
        tables = soup.select('tbody[class="ui-datatable-data ui-widget-content"]')
        if len(tables) < 5:
            return []

        values = [
            _normalize_whitespace(cell.get_text())
            for cell in tables[4].select('td[role="gridcell"]')
            if not cell.select("span")
        ]

        regimenes: list[Regimen] = []
        for index in range(0, len(values), 2):
            regimen = Regimen(regimen=values[index])
            if index + 1 < len(values):
                regimen.fecha_alta = values[index + 1]  # type: ignore[assignment]
            regimenes.append(regimen)
        return regimenes
