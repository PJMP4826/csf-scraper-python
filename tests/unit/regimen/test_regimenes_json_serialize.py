import json

from csf_scraper import Regimen, Regimenes


def test_serialize_default_regimenes() -> None:
    regimenes = Regimenes()

    regimenes.add_regimen(Regimen(), Regimen())

    data = json.loads(regimenes.model_dump_json())

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
