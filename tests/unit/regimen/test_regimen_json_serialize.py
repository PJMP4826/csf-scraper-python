import json

from csf_scraper import Regimen


def test_serialize_default_regimen() -> None:
    regimen = Regimen()

    data = json.loads(regimen.model_dump_json())

    assert data == {
        "regimen": "",
        "regimen_id": "",
        "fecha_alta": None,
    }
