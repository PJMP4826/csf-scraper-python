import pytest

from csf_scraper.download.exceptions import SatFormNotFoundException
from csf_scraper.download.form_utils import extract_form

_LOGIN_HTML = """<html><body>
<form action="/nidp/app/login?id=fiel" method="post">
  <input type="hidden" name="guid" value="abc-123" />
  <input type="hidden" name="SAMLRequest" value="xyz" />
  <input type="text" name="other" />
</form>
</body></html>"""

_CERT_HTML = """<html><body>
<form id="certform" action="https://login.siat.sat.gob.mx/nidp/app/login" method="post">
  <input type="hidden" name="guid" value="g-1" />
</form>
<form action="/other" method="post"><input name="x" value="y" /></form>
</body></html>"""


def test_extract_form_returns_action_and_hidden_fields() -> None:
    result = extract_form(_LOGIN_HTML, "https://login.siat.sat.gob.mx/nidp/app/login")

    assert result.action == "https://login.siat.sat.gob.mx/nidp/app/login?id=fiel"
    assert result.fields == {"guid": "abc-123", "SAMLRequest": "xyz", "other": ""}


def test_extract_form_prefers_absolute_action() -> None:
    result = extract_form(_CERT_HTML, "https://login.siat.sat.gob.mx/")

    assert result.action == "https://login.siat.sat.gob.mx/nidp/app/login"


def test_extract_form_by_id_selects_the_certform() -> None:
    result = extract_form(_CERT_HTML, "https://login.siat.sat.gob.mx/", form_id="certform")

    assert result.action == "https://login.siat.sat.gob.mx/nidp/app/login"
    assert result.fields == {"guid": "g-1"}


def test_extract_form_without_form_raises() -> None:
    with pytest.raises(SatFormNotFoundException):
        extract_form("<html><body>no form here</body></html>")


def test_extract_form_by_missing_id_raises() -> None:
    with pytest.raises(SatFormNotFoundException):
        extract_form(_LOGIN_HTML, form_id="certform")
