# Mapa de migración: phpcfdi/csf-scraper → Python

- **Origen**: <https://github.com/phpcfdi/csf-scraper>
- **Commit migrado**: `c66aab5fc1997da5de0ace9cea38274b86bfeaaf` (`main`, mensaje: _Rename file LICENCE to LICENSE_)
- **Tag de referencia**: `v0.2.0` = `162c63cfc22c36e50b2358a29e9cae74140da22d` (el commit migrado es `v0.2.0-1-gc66aab5`)
- **Licencia origen**: MIT
- **Clon local del origen** (para copiar fixtures): `/tmp/opencode/csf-scraper-upstream`
- **Paquete Python destino**: `csf-scraper` (import: `csf_scraper`), raíz `src/csf_scraper/`

Estados históricos: `pendiente` → `migrado`. **Todos los archivos están `migrado` al cierre de la Fase 5.**

Archivos auxiliares sin origen PHP (necesarios para el port):
`src/csf_scraper/date_parser.py` (emulación de `DateTimeImmutable::createFromFormat('!d-m-Y')`),
`src/csf_scraper/pdf_reader/__init__.py`, `tests/helpers.py` (lectura de fixtures).

## 1. Archivos de `src/` (100%)

| Archivo PHP origen                                                                    | Archivo Python destino                                                                                                                      | Estado  | Notas                                                                                                                                        |
| ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/DataExtractor.php`                                                               | `src/csf_scraper/data_extractor.py`                                                                                                         | migrado | DomCrawler/CSS+XPath → BeautifulSoup4+lxml                                                                                                   |
| `src/Interfaces/DataExtractorInterface.php`                                           | `src/csf_scraper/data_extractor.py` (`DataExtractor`)                                                                                       | migrado | interfaz eliminada; la clase concreta conserva el método `extract`                                                                          |
| `src/Interfaces/ScraperInterface.php`                                                 | `src/csf_scraper/scraper.py` (`Scraper`)                                                                                                    | migrado | interfaz eliminada; la clase concreta expone los métodos públicos                                                                             |
| `src/Exceptions/CsfScraperException.php`                                              | `src/csf_scraper/exceptions/__init__.py` (`CsfScraperException`)                                                                            | migrado | interfaz Throwable → clase base de excepción                                                                                                 |
| `src/Exceptions/CifDownloadException.php`                                             | `src/csf_scraper/exceptions/__init__.py`                                                                                                    | migrado | conserva `url` y `previous`                                                                                                                  |
| `src/Exceptions/CifNotFoundException.php`                                             | `src/csf_scraper/exceptions/__init__.py`                                                                                                    | migrado |                                                                                                                                              |
| `src/Exceptions/PdfReader/CifFromPdfNotFoundException.php`                            | `src/csf_scraper/exceptions/pdf_reader.py`                                                                                                  | migrado |                                                                                                                                              |
| `src/Exceptions/PdfReader/EmptyPdfContentException.php`                               | `src/csf_scraper/exceptions/pdf_reader.py`                                                                                                  | migrado |                                                                                                                                              |
| `src/Exceptions/PdfReader/PdfToTextConvertException.php`                              | `src/csf_scraper/exceptions/pdf_reader.py`                                                                                                  | migrado | conserva `command`, `exit_code`, `output`, `error`                                                                                           |
| `src/Exceptions/PdfReader/RfcFromPdfNotFoundException.php`                            | `src/csf_scraper/exceptions/pdf_reader.py`                                                                                                  | migrado |                                                                                                                                              |
| `src/PdfReader/CsfExtractor.php`                                                      | `src/csf_scraper/pdf_reader/csf_pdf_extractor.py` (`CsfPdfExtractor`) + `pdf_csf_text_parser.py` (`PdfCsfTextParser`)                       | migrado | renombrado y dividido; `CsfPdfExtractor` implementa `RfcCifExtractorPort.extract(path)` (asíncrono) y delega el parseo en `PdfCsfTextParser` |
| `src/PdfReader/PdfToText.php`                                                         | `src/csf_scraper/pdf_reader/pdf_to_text.py`                                                                                                 | migrado | **symfony/process → `subprocess`** (ver §3)                                                                                                  |
| `src/Persona.php`                                                                     | `src/csf_scraper/persona.py`                                                                                                                | migrado | modelo pydantic + comportamiento dinámico (`__set`/`__get`/`__isset`/`__unset`)                                                              |
| `src/PersonaFisica.php`                                                               | `src/csf_scraper/persona_fisica.py`                                                                                                         | migrado | modelo pydantic                                                                                                                              |
| `src/PersonaMoral.php`                                                                | `src/csf_scraper/persona_moral.py`                                                                                                          | migrado | modelo pydantic                                                                                                                              |
| `src/Regimen.php`                                                                     | `src/csf_scraper/regimen.py`                                                                                                                | migrado | modelo pydantic + catálogo de regímenes + `set_regimen`                                                                                      |
| `src/Regimenes.php`                                                                   | `src/csf_scraper/regimenes.py`                                                                                                              | migrado | modelo pydantic (colección)                                                                                                                  |
| `src/Scraper.php`                                                                     | `src/csf_scraper/scraper.py`                                                                                                                | migrado | flujo HTTP con httpx; `Scraper::$url` → atributo de clase                                                                                    |
| _(externo)_ `GuzzleHttp\ClientInterface` / `Psr\Http\Client\ClientExceptionInterface` | `httpx.AsyncClient` concreto (inyectado por constructor en `scraper.py`)                                                                    | migrado | no se creó `HttpClientInterface`: el original tampoco define una interfaz propia de cliente                                                  |
| _(externo)_ `PhpCfdi\Rfc\Rfc`                                                         | `src/csf_scraper/value_objects/rfc.py` (`Rfc`)                                                                                              | migrado | reimplementado sin dependencias (regex + `InvalidRfcFormatException`); reemplaza a `python-stdnum`                                           |
| — (no existe)                                                                         | `src/csf_scraper/value_objects/id_cif.py` (`IdCif`)                                                                                         | nuevo   | valida solo dígitos y longitud 8–13                                                                                                          |
| — (no existe)                                                                         | `src/csf_scraper/value_objects/csf_image.py` (`CsfImage`)                                                                                   | nuevo   | valida JPEG/PNG por magic bytes                                                                                                              |
| — (no existe)                                                                         | `src/csf_scraper/rfc_cif_data.py` (`RfcCifData`)                                                                                            | nuevo   | DTO compartido por las estrategias de extracción                                                                                             |
| — (no existe)                                                                         | `src/csf_scraper/ports/rfc_cif_extractor_port.py`, `src/csf_scraper/image_readers/ports/image_reader_port.py`                               | nuevo   | puertos (`ABC`): origen por ruta (`async extract(path)`) y motor sobre imagen en memoria (`async read(image)`)                               |
| — (no existe)                                                                         | `src/csf_scraper/image_readers/csf_image_extractor.py` (`CsfImageExtractor`)                                                                | nuevo   | puente `RfcCifExtractorPort` → `ImageReaderPort` (ruta → `CsfImage`)                                                                         |
| — (no existe)                                                                         | `src/csf_scraper/image_readers/schemas/rfc_cif_schema.py` (`RfcCifSchema`)                                                                  | nuevo   | esquema pydantic de la respuesta del LLM; los `description` guían al modelo sobre el aspecto del RFC y del idCIF                             |
| — (no existe)                                                                         | `src/csf_scraper/image_readers/services/llm_image_reader_service.py` (`LlmImageReaderService`, `CSF_PROMPT`, `RETRY_PROMPT`, `MAX_RETRIES`) | nuevo   | sub-contrato común de los adaptadores LLM: plantilla `_run_program(image, llm_provider)`, prompt, `ImageBlock`, reintentos, ejecución del programa y mapeo a `RfcCifData` |
| — (no existe)                                                                         | `src/csf_scraper/image_readers/adapters/gemini_image_reader.py` (`GeminiImageReader`)                                                       | nuevo   | hereda de `LlmImageReaderService` e implementa `ImageReaderPort.read()`; crea `GoogleGenAI` y delega en la plantilla                      |
| — (no existe)                                                                         | `src/csf_scraper/exceptions/value_objects.py`, `src/csf_scraper/exceptions/image_reader.py`                                                 | nuevo   | excepciones de los nuevos value objects y del lector de imágenes                                                                             |

## 2. Archivos de `tests/` (100%)

| Archivo PHP origen                                                    | Archivo Python destino                                                             | Estado  | Notas                                                                    |
| --------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ------- | ------------------------------------------------------------------------ |
| `tests/bootstrap.php`                                                 | `[tool.pytest.ini_options]` en `pyproject.toml` (`testpaths`, `pythonpath`)        | migrado | autoload de composer → configuración de pytest (sin `conftest.py`)       |
| `tests/TestCase.php`                                                  | `tests/helpers.py` (`file_path` / `file_contents`, funciones)                      | migrado | métodos estáticos → funciones en módulo de ayuda                         |
| `tests/Integration/Helpers/ScraperHelper.php`                         | `tests/integration/helpers.py` (`ScraperHelper`)                                   | migrado | subclase que inyecta un `CsfPdfExtractor` con texto de fixture           |
| `tests/Integration/ScrapCsfFromRfcAndCifTest.php`                     | `tests/integration/test_scrap_csf_from_rfc_and_cif.py`                             | migrado | MockHandler → respx (7 tests)                                            |
| `tests/Integration/ScrapFromCsfFileTest.php`                          | `tests/integration/test_scrap_from_csf_file.py`                                    | migrado | 2 tests con red real → respx (§4); 3 tests con `pdftotext`               |
| `tests/Unit/ScraperTest.php`                                          | `tests/unit/test_scraper.py`                                                       | migrado | `getConfig('curl')` → introspección del `SSLContext` (§5)                |
| `tests/Unit/Exceptions/CifDownloadExceptionTest.php`                  | `tests/unit/exceptions/test_cif_download_exception.py`                             | migrado |                                                                          |
| `tests/Unit/Exceptions/CifNotFoundExceptionTest.php`                  | `tests/unit/exceptions/test_cif_not_found_exception.py`                            | migrado |                                                                          |
| `tests/Unit/Exceptions/PdfReader/CifFromPdfNotFoundExceptionTest.php` | `tests/unit/exceptions/pdf_reader/test_cif_from_pdf_not_found_exception.py`        | migrado |                                                                          |
| `tests/Unit/Exceptions/PdfReader/EmptyPdfContentExceptionTest.php`    | `tests/unit/exceptions/pdf_reader/test_empty_pdf_content_exception.py`             | migrado |                                                                          |
| `tests/Unit/Exceptions/PdfReader/PdfToTextConvertExceptionTest.php`   | `tests/unit/exceptions/pdf_reader/test_pdf_to_text_convert_exception.py`           | migrado |                                                                          |
| `tests/Unit/Exceptions/PdfReader/RfcFromPdfNotFoundExceptionTest.php` | `tests/unit/exceptions/pdf_reader/test_rfc_from_pdf_not_found_exception.py`        | migrado |                                                                          |
| `tests/Unit/PdfReader/CsfExtractor/GetCifIdTest.php`                  | `tests/unit/pdf_reader/pdf_csf_text_extractor/test_get_cif_id.py`                  | migrado | ejercita `PdfCsfTextParser`                                              |
| `tests/Unit/PdfReader/CsfExtractor/GetRfcTest.php`                    | `tests/unit/pdf_reader/pdf_csf_text_extractor/test_get_rfc.py`                     | migrado | ejercita `PdfCsfTextParser`                                              |
| — (no existe)                                                         | `tests/unit/pdf_reader/pdf_csf_text_extractor/test_extract.py`                     | nuevo   | cubre `PdfCsfTextParser` y `CsfPdfExtractor.extract(path)`               |
| — (no existe)                                                         | `tests/unit/image_readers/test_llm_image_reader.py`, `test_csf_image_extractor.py` | nuevo   | sub-contrato LLM (parseo, errores) y puente ruta → motor                 |
| — (no existe)                                                         | `tests/unit/value_objects/test_rfc.py`, `test_id_cif.py`, `test_csf_image.py`      | nuevo   | value objects                                                            |
| `tests/Unit/PdfReader/PdfToText/PdfToTextConstructorTest.php`         | `tests/unit/pdf_reader/pdf_to_text/test_pdf_to_text_constructor.py`                | migrado | `RuntimeException` de Symfony → `FileNotFoundError` (§5)                 |
| `tests/Unit/Persona/CommonPersonaPropertiesTest.php`                  | `tests/unit/persona/test_common_persona_properties.py`                             | migrado | data providers → `@pytest.mark.parametrize`                              |
| `tests/Unit/Persona/PersonaFisicaPropertiesTest.php`                  | `tests/unit/persona/test_persona_fisica_properties.py`                             | migrado |                                                                          |
| `tests/Unit/Persona/PersonaMoralPropertiesTest.php`                   | `tests/unit/persona/test_persona_moral_properties.py`                              | migrado |                                                                          |
| `tests/Unit/Persona/PersonaJsonSerializeTest.php`                     | `tests/unit/persona/test_persona_json_serialize.py`                                | migrado |                                                                          |
| `tests/Unit/Persona/Traits/PersonaTrait.php`                          | `tests/unit/persona/traits/persona_trait.py`                                       | migrado | trait con tests → módulo cuyas funciones se importan en cada test module |
| `tests/Unit/RegimenesTest.php`                                        | `tests/unit/test_regimenes.py`                                                     | migrado |                                                                          |
| `tests/Unit/Regimen/RegimenJsonSerializeTest.php`                     | `tests/unit/regimen/test_regimen_json_serialize.py`                                | migrado |                                                                          |
| `tests/Unit/Regimen/RegimenesJsonSerializeTest.php`                   | `tests/unit/regimen/test_regimenes_json_serialize.py`                              | migrado |                                                                          |
| `tests/Unit/Regimen/SetRegimenTest.php`                               | `tests/unit/regimen/test_set_regimen.py`                                           | migrado | 28 casos del data provider → parametrize                                 |
| `tests/_files/csf-bad-content.txt`                                    | `tests/_files/csf-bad-content.txt`                                                 | migrado | copia literal                                                            |
| `tests/_files/csf-content.txt`                                        | `tests/_files/csf-content.txt`                                                     | migrado | copia literal                                                            |
| `tests/_files/csf-correct-but-invalid.pdf`                            | `tests/_files/csf-correct-but-invalid.pdf`                                         | migrado | copia literal                                                            |
| `tests/_files/csf-without-cif.pdf`                                    | `tests/_files/csf-without-cif.pdf`                                                 | migrado | copia literal                                                            |
| `tests/_files/csf-without-rfc.pdf`                                    | `tests/_files/csf-without-rfc.pdf`                                                 | migrado | copia literal                                                            |
| `tests/_files/error.html`                                             | `tests/_files/error.html`                                                          | migrado | copia literal                                                            |
| `tests/_files/scrap_fisica.html`                                      | `tests/_files/scrap_fisica.html`                                                   | migrado | copia literal                                                            |
| `tests/_files/scrap_moral.html`                                       | `tests/_files/scrap_moral.html`                                                    | migrado | copia literal                                                            |
| `tests/_files/scrap_moral_without_colonia.html`                       | `tests/_files/scrap_moral_without_colonia.html`                                    | migrado | copia literal                                                            |
| `tests/_files/scrap_regimenes.html`                                   | `tests/_files/scrap_regimenes.html`                                                | migrado | copia literal                                                            |

**Recuento de tests origen**: 53 métodos de test → **90 casos de test** (40 expandidos por data providers/traits).
Desglose: Integration 12, Persona 31 (17+7+5 de las 3 clases con trait +2 json), Regimén 30 (28+2 json), Regimenes 1, Scraper 1, Exceptions 8, PdfReader 7.

## 3. Uso de `Symfony\Component\Process` en `src/` (Fase 0.c)

Un único punto de uso: **`src/PdfReader/PdfToText.php`**.

| Elemento                                       | Detalle                                                                                                                                                     |
| ---------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Qué ejecuta                                    | binario externo `pdftotext` (paquete del sistema `poppler-utils`), por defecto buscado en el `PATH` (constructor permite ruta alternativa)                  |
| Por qué                                        | convertir el PDF de la _Constancia de Situación Fiscal_ a texto plano para extraer RFC y idCIF (`CsfPdfExtractor`)                                          |
| Comando construido (`buildCommand`)            | `['pdftotext', '-eol', 'unix', '-raw', '-q', <ruta pdf>, '-']` (lista, sin shell)                                                                           |
| Entrada                                        | ruta de un archivo PDF local (`extract(string $path)`)                                                                                                      |
| Salida                                         | `stdout` del proceso como texto; en error: excepción `PdfToTextConvertException` con `command`, `exitCode`, `stdout`, `stderr`                              |
| Comportamiento en error de binario inexistente | Symfony `Process::run()` lanza `RuntimeException` (no es una excepción de la librería; los tests la esperan con `expectException(RuntimeException::class)`) |

**Reemplazabilidad**: NO es reemplazable con `httpx` ni con la stdlib pura (no hay extracción de texto de PDF en la stdlib). Requiere **`subprocess`** (stdlib) invocando el mismo binario externo `pdftotext` (poppler-utils), idéntico requisito de despliegue que el original.
**Mapeo de excepción**: `RuntimeException` de Symfony (binario no encontrado) → `FileNotFoundError` de la stdlib (lanzada por `subprocess.run`), documentado en `docs/differences.md`.

## 4. Tests, fixtures y cómo se mockea HTTP (Fase 0.d)

### Fixtures (`tests/_files/`, 10 archivos, se copian literales; no se inventa ninguno)

- HTML: `scrap_moral.html`, `scrap_fisica.html`, `scrap_moral_without_colonia.html`, `scrap_regimenes.html` (páginas SAT "ok"), `error.html` (página SAT sin información; contiene `span.ui-messages-info-detail`).
- Texto de `pdftotext`: `csf-content.txt` (contenido válido, rfc `DIM8701081LA`, idCIF `12345678`), `csf-bad-content.txt` (sin líneas `RFC:`/`idCIF:`).
- PDFs: `csf-correct-but-invalid.pdf`, `csf-without-rfc.pdf`, `csf-without-cif.pdf` (se procesan con `pdftotext` real en los tests Linux-only).

### Cómo mockean HTTP los tests originales

| Test                                                                | Mecanismo                                                                    | Replicación prevista con respx                                                                   |
| ------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `ScrapCsfFromRfcAndCifTest` (6 tests vía `prepareScraper`)          | `GuzzleHttp\Handler\MockHandler` con `Response(200, [], fileContents(html))` | `respx` ruta GET al URL exacto del validador SAT devolviendo 200 + contenido del fixture         |
| `ScrapCsfFromRfcAndCifTest::test_throw_exception_on_download_error` | `MockHandler` con excepción `GuzzleException` mockeada                       | `respx` con `side_effect=httpx.ConnectError(...)`                                                |
| `ScrapFromCsfFileTest::test_scrap_from_idcif_and_rfc_by_moral`      | igual que arriba (usa `ScraperHelper`)                                       | igual que arriba                                                                                 |
| `ScrapFromCsfFileTest::test_obtain_from_pdf_with_invalid_url`       | **RED REAL** (`Scraper::create()` contra `sat.gob.mx`)                       | respx: `side_effect=httpx.ConnectError(...)` en el URL con host alterno (decidido, sin red real) |
| `ScrapFromCsfFileTest::test_obtain_from_pdf_with_invalid_data`      | **RED REAL** (`Scraper::create()` contra `siat.sat.gob.mx`)                  | respx: 200 con fixture `error.html` (decidido, sin red real)                                     |
| El resto (unit/exceptions/pdf/persona/regimen)                      | sin HTTP                                                                     | sin HTTP                                                                                         |

Ningún test del original afirma el URL construido (el `MockHandler` responde sin importar la URL); en la portación la ruta respx se fija por prefijo con regex al URL del validador SAT (`^https://siat.sat.gob\.mx/…/validadorqr.jsf`), manteniendo la misma flexibilidad que el `MockHandler` original.

## 5. TLS, headers, cookies, user-agent, reintentos, timeouts (Fase 0.e)

| Aspecto                   | Original                                                                                                                          | Mapeo Python                                                                                                                                                                                                                              |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| TLS cipher                | `Scraper::create()` configura Guzzle `'curl' => [CURLOPT_SSL_CIPHER_LIST => 'DEFAULT@SECLEVEL=1']` (SAT exige cipher chain débil) | `ssl.create_default_context()` + `set_ciphers('DEFAULT@SECLEVEL=1')` pasado a `httpx.AsyncClient(verify=...)`; verificado en este entorno: `ctx.security_level == 1` después de aplicarlo (OpenSSL 3.5.8). Los tests mockeados no lo necesitan |
| Verificación certificados | Guzzle `verify=true` (CA del sistema) por defecto                                                                                 | `httpx` `verify=True` por defecto ✓                                                                                                                                                                                                       |
| Headers                   | ninguno personalizado; el `User-Agent` es el por defecto de Guzzle (`GuzzleHttp/7`)                                               | ninguno personalizado; `User-Agent` por defecto de httpx (`python-httpx/…`). Sin impacto en tests; documentar en `differences.md`                                                                                                         |
| Cookies                   | sin middleware de cookies → cada petición independiente                                                                           | `httpx.AsyncClient` tiene jar de cookies; el flujo hace **una** petición por invocación, sin impacto. Documentar                                                                                                                          |
| Redirecciones             | Guzzle: sigue redirecciones por defecto (máx 5)                                                                                   | `Scraper.create()` usará `follow_redirects=True` para equivalencia; clientes inyectados dependen de su configuración (igual que en el original)                                                                                           |
| Reintentos                | ninguno                                                                                                                           | ninguno ✓                                                                                                                                                                                                                                 |
| Timeout                   | Guzzle: sin timeout (0) por defecto                                                                                               | `Scraper.create()` usará `timeout=None` (sin timeout) para equivalencia; un cliente inyectado usa su propia config                                                                                                                        |
| `http_errors`             | Guzzle lanza excepción en 4xx/5xx → capturado como `CifDownloadException`                                                         | `response.raise_for_status()` + captura de `httpx.HTTPError` → `CifDownloadException`                                                                                                                                                     |
| Codificación cuerpo       | cast `(string) $response->getBody()` (bytes) → se parsea como HTML                                                                | `response.text` (httpx asume UTF-8 sin `charset`; los fixtures son UTF-8)                                                                                                                                                                 |

## 6. Comportamientos reportados y resueltos (Fase 0)

1. **Dos tests originales usan red real contra el SAT** (prohibido por la regla 5) — **resuelto**: se migran con respx conservando intención y nombre:
   - `test_obtain_from_pdf_with_invalid_url`: respx lanza `httpx.ConnectError` en el URL con host alterno → espera `CifDownloadException`.
   - `test_obtain_from_pdf_with_invalid_data`: respx devuelve el fixture `error.html` → espera `CifNotFoundException`.
2. **`symfony/process` → `subprocess` + binario externo `pdftotext`** (§3): fuera del stack "pip" pero permitido como stdlib; el binario externo era requisito ya del original.
3. **`test_create_with_specific_openssl_cipher_list`** depende del deprecado `Client::getConfig('curl')`: se sustituye por asertar sobre el `SSLContext` resultante (`security_level == 1` y ciphers configurados) — adaptación documentada.
4. **`test_throw_exception_when_path_not_found`** espera `RuntimeException` (Symfony): en Python espera `FileNotFoundError` (stdlib).
5. **JSON de fechas**: `json_encode` de PHP produce `{"date": …, "timezone_type": 3, "timezone": "UTC"}`; el port usará ISO-8601 (pydantic). Los tests JSON del original solo usan fechas `null`, por lo que no hay conflicto de expectativas.
6. **`test_return_empty_when_not_found`** tiene código muerto tras `expectException` (`assertSame([], $data)` nunca se ejecuta) y una variable `$expectedData` sin uso: se migra solo la parte viva (`pytest.raises`).

## 7. Refactor posterior al port (no presente en el original)

Cambios de diseño sobre el port, sin contraparte en el PHP:

1. **`python-stdnum` eliminado**: `Rfc` es un value object propio (subclase de
   `str` con `__get_pydantic_core_schema__`), por lo que la dependencia y su
   `[[tool.mypy.overrides]]` ya no son necesarios.
2. **Patrón strategy para la extracción**: `RfcCifExtractorPort` (origen por
   ruta, `extract(path)`) e `ImageReaderPort` (motor sobre una imagen en
   memoria, `read(image)`) devuelven `RfcCifData`, y `Scraper` consume solo el
   primero, sin conocer el motor. `CsfImageExtractor` hace de puente entre
   ambos y `obtain_from_image_path` es nuevo.
3. **`CsfExtractor` → `CsfPdfExtractor`** (y `PdfCsfTextParser` para el parseo
   del texto) y `tests/unit/pdf_reader/csf_extractor/` →
   `tests/unit/pdf_reader/pdf_csf_text_extractor/` (carpeta renombrada).
4. **`Persona.rfc` / `Persona.id_cif`** pasan de `str = ""` a `Rfc | None = None` /
   `IdCif | None = None`; el JSON por omisión serializa `null` en lugar de `""`.
5. **Sub-contrato LLM**: `LlmImageReaderService` centraliza el prompt, el armado
   del `ImageBlock`, los reintentos, la ejecución del programa y el mapeo a
   `RfcCifData`. Cada adaptador crea su cliente de LlamaIndex y expone `read()`
   delegando en el método plantilla `_run_program(image, llm_provider)`;
   `_image_to_schema(...)` construye y ejecuta el
   `MultiModalLLMCompletionProgram`. `RfcCifSchema` describe con
   `Field(description=…)` el aspecto del RFC y del idCIF para el modelo, y sus
   fallos de formato de negocio —los que levantan `Rfc` e `IdCif`— son los que
   disparan los reintentos. `GeminiImageReader` implementa `read()` con
   `GoogleGenAI`; el adaptador de DeepSeek queda pendiente.
6. **Flujo asíncrono**: los puertos `extract`/`read` son corrutinas, `Scraper`
   envuelve un `httpx.AsyncClient` y expone `__aenter__`/`__aexit__`/`aclose`.
   El E/S bloqueante (`pdftotext`, lectura de la imagen) se delega con
   `asyncio.to_thread` para no bloquear el bucle de eventos.
