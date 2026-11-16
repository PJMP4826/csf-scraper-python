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


def extract_button_name(html: str, *, form_id: str, onclick_contains: str) -> str:
    """Devuelve el ``name`` del botón cuyo ``onclick`` contiene ``onclick_contains``.

    Los botones JSF (``<button id="form:j_idt65">``) son la fuente del
    ``javax.faces.source`` de un POST AJAX. Sus identificadores ``j_idtN``
    cambian entre sesiones y versiones, así que no se pueden fijar en el
    código: hay que descubrirlos en el HTML del formulario.
    """
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form", id=form_id)
    if form is None:
        raise SatFormNotFoundException(
            f"No form found in the SAT response (expected id={form_id!r})"
        )
    for element in form.find_all(["button", "input"]):
        name = element.get("name")
        onclick = str(element.get("onclick") or "")
        if name is not None and onclick_contains in onclick:
            return str(name)
    raise SatFormNotFoundException(f"No button with {onclick_contains!r} in the {form_id!r} form")
