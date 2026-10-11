import json

from pydantic import TypeAdapter

from csf_scraper import Regimen


def test_serialize_default_regimenes() -> None:
    regimenes = [Regimen(), Regimen()]

    data = json.loads(TypeAdapter(list[Regimen]).dump_json(regimenes))

    assert data == [
        {
            "regimen": "",
            "regimen_id": "",
            "fecha_alta": None,
        },
        {
            "regimen": "",
            "regimen_id": "",
            "fecha_alta": None,
        },
    ]
