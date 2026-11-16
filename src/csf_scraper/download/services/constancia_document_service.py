"""Descarga del PDF de la constancia.

Equivalente a ``DocumentService`` de ``phpcfdi/csf-sat-scraper``: envía el
formulario final JSF (``formReimpAcuse``) y descarga el PDF de
``IdcGeneraConstancia.jsf``. Devuelve un :class:`CsfPdf` validado, nunca
bytes sin comprobar.
"""

from email.message import Message

import httpx

from csf_scraper.download.exceptions import (
    ConstanciaNotAvailableException,
    SatFormNotFoundException,
)
from csf_scraper.download.form_utils import extract_button_name, extract_form
from csf_scraper.download.services._portal import get_url, post_form
from csf_scraper.download.urls import (
    CONSTANCIA_PDF_URL,
    CONSULTA_TRAMITE_URL,
    RFCAMPC_BASE_URL,
)
from csf_scraper.download.value_objects.csf_pdf import CsfPdf

#: Marca del ``onclick`` del botón JSF que genera la constancia. El ``j_idtN``
#: del botón cambia entre sesiones, así que se descubre en el HTML.
_GENERATE_BUTTON_ONCLICK = "IdcGeneraConstancia.jsf"

#: Cabeceras que PrimeFaces envía en un POST AJAX de JSF.
_JSF_AJAX_HEADERS = {
    "Faces-Request": "partial/ajax",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/xml, text/xml, */*; q=0.01",
}


def _filename_from_content_disposition(value: str | None) -> str | None:
    """Extrae el ``filename`` de una cabecera ``Content-Disposition``."""
    if not value:
        return None
    message = Message()
    message["content-disposition"] = value
    return message.get_filename() or None


class ConstanciaDocumentService:
    """Descarga la constancia en PDF a partir del HTML de ConsultaTramite."""

    async def download(self, client: httpx.AsyncClient, last_html: str) -> CsfPdf:
        """Envía el formulario final y devuelve el PDF validado."""
        try:
            form = extract_form(last_html, base_url=RFCAMPC_BASE_URL, form_id="formReimpAcuse")
            button_name = extract_button_name(
                last_html,
                form_id="formReimpAcuse",
                onclick_contains=_GENERATE_BUTTON_ONCLICK,
            )
        except SatFormNotFoundException as exception:
            raise ConstanciaNotAvailableException(
                "The SAT tramite page has no formReimpAcuse form or generate button."
            ) from exception
        await self._send_final_form(client, form.action, form.fields, button_name)
        response = await get_url(client, CONSTANCIA_PDF_URL, referer_url=CONSULTA_TRAMITE_URL)
        filename = _filename_from_content_disposition(response.headers.get("content-disposition"))
        return CsfPdf.new_from_contents(response.content, filename=filename)

    async def _send_final_form(
        self,
        client: httpx.AsyncClient,
        action: str,
        fields: dict[str, str],
        button_name: str,
    ) -> None:
        data = {
            **fields,
            "javax.faces.partial.ajax": "true",
            "javax.faces.source": button_name,
            "javax.faces.partial.execute": "@all",
            button_name: button_name,
            "formReimpAcuse": "formReimpAcuse",
            "formReimpAcuse:tipoTramite_input": "0",
            "formReimpAcuse:tipoTramite_focus": "",
            "formReimpAcuse:fechaInicio_input": "",
            "formReimpAcuse:fechaFin_input": "",
            "formReimpAcuse:folio": "",
        }
        await post_form(
            client,
            action=action,
            referer_url=CONSULTA_TRAMITE_URL,
            data=data,
            extra_headers=_JSF_AJAX_HEADERS,
        )
