"""Descarga del PDF de la constancia.

Equivalente a ``DocumentService`` de ``phpcfdi/csf-sat-scraper``: envía el
formulario final JSF (``formReimpAcuse``) y descarga el PDF de
``IdcGeneraConstancia.jsf``. Devuelve un :class:`CsfPdf` validado, nunca
bytes sin comprobar.
"""

import httpx

from csf_scraper.download.exceptions import (
    ConstanciaNotAvailableException,
    SatFormNotFoundException,
)
from csf_scraper.download.form_utils import extract_form
from csf_scraper.download.services._portal import get_url, post_form
from csf_scraper.download.urls import (
    CONSTANCIA_PDF_URL,
    CONSULTA_TRAMITE_URL,
    RFCAMPC_BASE_URL,
)
from csf_scraper.download.value_objects.csf_pdf import CsfPdf

#: Botón del formulario JSF que genera la constancia.
_GENERATE_BUTTON_ID = "formReimpAcuse:j_idt50"


class ConstanciaDocumentService:
    """Descarga la constancia en PDF a partir del HTML de ConsultaTramite."""

    async def download(self, client: httpx.AsyncClient, last_html: str) -> CsfPdf:
        """Envía el formulario final y devuelve el PDF validado."""
        try:
            form = extract_form(last_html, base_url=RFCAMPC_BASE_URL, form_id="formReimpAcuse")
        except SatFormNotFoundException as exception:
            raise ConstanciaNotAvailableException(
                "The SAT tramite page has no formReimpAcuse form."
            ) from exception
        await self._send_final_form(client, form.action, form.fields)
        response = await get_url(client, CONSTANCIA_PDF_URL, referer_url=CONSULTA_TRAMITE_URL)
        return CsfPdf.new_from_contents(response.content)

    async def _send_final_form(
        self, client: httpx.AsyncClient, action: str, fields: dict[str, str]
    ) -> None:
        data = {
            **fields,
            "javax.faces.partial.ajax": "true",
            "javax.faces.source": _GENERATE_BUTTON_ID,
            "javax.faces.partial.execute": "@all",
            _GENERATE_BUTTON_ID: _GENERATE_BUTTON_ID,
            "formReimpAcuse": "formReimpAcuse",
            "formReimpAcuse:tipoTramite_input": "0",
            "formReimpAcuse:tipoTramite_focus": "",
            "formReimpAcuse:fechaInicio_input:": "",
            "formReimpAcuse:fechaFin_input": "",
            "formReimpAcuse:folio": "",
        }
        await post_form(client, action=action, referer_url=CONSULTA_TRAMITE_URL, data=data)
