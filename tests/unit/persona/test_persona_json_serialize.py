import json

from csf_scraper import PersonaFisica, PersonaMoral


def test_serialize_default_person_moral() -> None:
    person = PersonaMoral()

    data = json.loads(person.model_dump_json())

    assert data == {
        "razon_social": "",
        "regimen_de_capital": "",
        "fecha_constitucion": None,
        "rfc": None,
        "id_cif": None,
        "fecha_inicio_operaciones": None,
        "situacion_contribuyente": "",
        "fecha_ultimo_cambio_situacion": None,
        "entidad_federativa": "",
        "municipio_delegacion": "",
        "colonia": "",
        "tipo_vialidad": "",
        "nombre_vialidad": "",
        "numero_exterior": "",
        "numero_interior": "",
        "codigo_postal": "",
        "correo_electronico": "",
        "al": "",
        "regimenes": [],
        "extra_data": {},
    }


def test_serialize_default_person_fisica() -> None:
    person = PersonaFisica()

    data = json.loads(person.model_dump_json())

    assert data == {
        "curp": "",
        "nombre": "",
        "apellido_paterno": "",
        "apellido_materno": "",
        "fecha_nacimiento": None,
        "rfc": None,
        "id_cif": None,
        "fecha_inicio_operaciones": None,
        "situacion_contribuyente": "",
        "fecha_ultimo_cambio_situacion": None,
        "entidad_federativa": "",
        "municipio_delegacion": "",
        "colonia": "",
        "tipo_vialidad": "",
        "nombre_vialidad": "",
        "numero_exterior": "",
        "numero_interior": "",
        "codigo_postal": "",
        "correo_electronico": "",
        "al": "",
        "regimenes": [],
        "extra_data": {},
    }
