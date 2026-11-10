"""Extracción de formularios HTML del SAT.

Equivalente en Python de ``FormUtils`` de ``phpcfdi/csf-sat-scraper`` y de
``get_form`` de ``SAT-CFDI/python-satcfdi``: dado el HTML de una respuesta del
SAT, devuelve la URL de envío (``action``, resuelta contra la URL base) y los
campos del formulario.
"""

from dataclasses import dataclass
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from csf_scraper.download.exceptions import SatFormNotFoundException


@dataclass(frozen=True)
class FormExtractionResult:
    """Resultado de extraer un formulario: su ``action`` y sus campos."""

    action: str
    fields: dict[str, str]


def extract_form(
    html: str, base_url: str = "", *, form_id: str | None = None
) -> FormExtractionResult:
    """Extrae el primer formulario (o el de ``form_id``) de ``html``.

    Los campos son todos los ``<input>`` con atributo ``name``; los que no
    tienen ``value`` se devuelven como cadena vacía. Si no hay formulario,
    lanza :class:`SatFormNotFoundException` (nunca devuelve ``None``).
    """
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form", id=form_id) if form_id is not None else soup.find("form")
    if form is None:
        raise SatFormNotFoundException(
            "No form found in the SAT response"
            + (f" (expected id={form_id!r})" if form_id is not None else "")
        )
    action = str(form.get("action") or "")
    if base_url:
        action = urljoin(base_url, action) if action else base_url
    fields: dict[str, str] = {}
    for input_tag in form.find_all("input"):
        name = input_tag.get("name")
        if name is not None:
            fields[str(name)] = str(input_tag.get("value") or "")
    return FormExtractionResult(action=action, fields=fields)
