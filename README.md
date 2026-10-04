# csf-scraper

Port a Python de [phpcfdi/csf-scraper](https://github.com/phpcfdi/csf-scraper):
obtiene los datos fiscales actuales de una persona moral o física dado su RFC y
su idCIF (SAT, Constancia de Situación Fiscal).

## Requisitos

- Python >= 3.11
- [`pdftotext`](https://poppler.freedesktop.org/) (paquete del sistema
  `poppler-utils`), necesario **solo** para leer la CSF desde un archivo PDF
  (`obtain_from_pdf_path`). Mismo requisito que el original en PHP.
- Dependencias: `httpx`, `beautifulsoup4`, `lxml`, `python-stdnum`, `pydantic`.

## Instalación

Desde el código fuente:

```bash
pip install .
```

## Ejemplo de uso

```python
from csf_scraper import Scraper

scraper = Scraper.create()

# RFC + idCIF directamente (el RFC se valida con python-stdnum)
person = scraper.obtain_from_rfc_and_cif("DIM8701081LA", "1904014102123")

# También puedes obtener los datos directamente de un archivo local PDF
# (requiere pdftotext / poppler-utils instalado)
person = scraper.obtain_from_pdf_path("ruta/al/csf.pdf")

# Acceso a los datos de la persona (moral o física) por atributos
if len(person.rfc) == 13:  # persona física
    print(person.nombre)
else:  # persona moral
    print(person.razon_social)

# Dict de datos (equivalente a toArray()) o JSON (ISO-8601 en fechas)
data = person.to_dict()
json_text = person.model_dump_json()
```

Salida de `person.to_dict()` para una persona moral (fechas como `datetime`):

```python
{
    "razon_social": "Mi razón social",
    "regimen_de_capital": "SA DE CV",
    "fecha_constitucion": datetime(2019, 2, 21),
    # …
    "rfc": "DIM8701081LA",
    "id_cif": "12345678",
    "regimenes": [
        {"regimen": "Régimen General de Ley Personas Morales", "regimen_id": "601", "fecha_alta": datetime(2019, 2, 21)},
    ],
    "extra_data": {"Localidad": ""},
}
```

### Excepciones

Todas heredan de `CsfScraperException`:

- `CifDownloadException` (la petición HTTP falló; conserva `url` y `previous`)
- `CifNotFoundException` (el SAT no devolvió información del CIF)
- `RfcFromPdfNotFoundException` / `CifFromPdfNotFoundException` (el PDF no
  contiene RFC / idCIF)
- `EmptyPdfContentException` / `PdfToTextConvertException` (problemas con
  `pdftotext`)
- La validación del RFC lanza `stdnum.exceptions.ValidationError`.

## Desarrollo

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/ruff check .
.venv/bin/mypy src
.venv/bin/pytest
```

Los tests usan fixtures de `tests/_files/` (copias literales de las del original
en PHP) y mockean HTTP con `respx`: **ningún test contacta al SAT**.

## Documentación de la migración

- `docs/migration-map.md`: correspondencia archivo a archivo PHP → Python.
- `docs/differences.md`: diferencias de comportamiento deliberadas.

## Licencia

MIT — ver `LICENSE` (heredado del original) y `NOTICE.md`.
