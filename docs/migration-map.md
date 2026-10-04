# Mapa de migración: phpcfdi/csf-scraper → Python

- **Origen**: <https://github.com/phpcfdi/csf-scraper>
- **Commit migrado**: `c66aab5fc1997da5de0ace9cea38274b86bfeaaf` (`main`, mensaje: *Rename file LICENCE to LICENSE*)
- **Tag de referencia**: `v0.2.0` = `162c63cfc22c36e50b2358a29e9cae74140da22d` (el commit migrado es `v0.2.0-1-gc66aab5`)
- **Licencia origen**: MIT
- **Clon local del origen** (para copiar fixtures): `/tmp/opencode/csf-scraper-upstream`
- **Paquete Python destino**: `csf-scraper` (import: `csf_scraper`), raíz `src/csf_scraper/`

Estados: `pendiente` → `migrado` (se actualizan conforme avanza cada fase).

## 1. Archivos de `src/` (100%)

| Archivo PHP origen | Archivo Python destino | Estado | Notas |
|---|---|---|---|
| `src/DataExtractor.php` | `src/csf_scraper/data_extractor.py` | pendiente | DomCrawler/CSS+XPath → BeautifulSoup4+lxml |
| `src/Interfaces/DataExtractorInterface.php` | `src/csf_scraper/interfaces.py` (`DataExtractorInterface`) | pendiente | interfaz → `typing.Protocol` |
| `src/Interfaces/ScraperInterface.php` | `src/csf_scraper/interfaces.py` (`ScraperInterface`) | pendiente | interfaz → `typing.Protocol` |
| `src/Exceptions/CsfScraperException.php` | `src/csf_scraper/exceptions/__init__.py` (`CsfScraperException`) | pendiente | interfaz Throwable → clase base de excepción |
| `src/Exceptions/CifDownloadException.php` | `src/csf_scraper/exceptions/__init__.py` | pendiente | conserva `url` y `previous` |
| `src/Exceptions/CifNotFoundException.php` | `src/csf_scraper/exceptions/__init__.py` | pendiente | |
| `src/Exceptions/PdfReader/CifFromPdfNotFoundException.php` | `src/csf_scraper/exceptions/pdf_reader.py` | pendiente | |
| `src/Exceptions/PdfReader/EmptyPdfContentException.php` | `src/csf_scraper/exceptions/pdf_reader.py` | pendiente | |
| `src/Exceptions/PdfReader/PdfToTextConvertException.php` | `src/csf_scraper/exceptions/pdf_reader.py` | pendiente | conserva `command`, `exit_code`, `output`, `error` |
| `src/Exceptions/PdfReader/RfcFromPdfNotFoundException.php` | `src/csf_scraper/exceptions/pdf_reader.py` | pendiente | |
| `src/PdfReader/CsfExtractor.php` | `src/csf_scraper/pdf_reader/csf_extractor.py` | pendiente | parsing de texto plano (sin dependencias) |
| `src/PdfReader/PdfToText.php` | `src/csf_scraper/pdf_reader/pdf_to_text.py` | pendiente | **symfony/process → `subprocess`** (ver §3) |
| `src/Persona.php` | `src/csf_scraper/persona.py` | pendiente | modelo pydantic + comportamiento dinámico (`__set`/`__get`/`__isset`/`__unset`) |
| `src/PersonaFisica.php` | `src/csf_scraper/persona_fisica.py` | pendiente | modelo pydantic |
| `src/PersonaMoral.php` | `src/csf_scraper/persona_moral.py` | pendiente | modelo pydantic |
| `src/Regimen.php` | `src/csf_scraper/regimen.py` | pendiente | modelo pydantic + catálogo de regímenes + `set_regimen` |
| `src/Regimenes.php` | `src/csf_scraper/regimenes.py` | pendiente | modelo pydantic (colección) |
| `src/Scraper.php` | `src/csf_scraper/scraper.py` | pendiente | flujo HTTP con httpx; `Scraper::$url` → atributo de clase |
| *(externo)* `GuzzleHttp\ClientInterface` / `Psr\Http\Client\ClientExceptionInterface` | `src/csf_scraper/interfaces.py` (`HttpClientInterface`) | pendiente | Protocol inyectado por constructor (regla 4) |
| *(externo)* `PhpCfdi\Rfc\Rfc` | `python-stdnum` → `stdnum.mx.rfc` (uso directo en `scraper.py`) | pendiente | sin wrapper propio; ver §5 |

## 2. Archivos de `tests/` (100%)

| Archivo PHP origen | Archivo Python destino | Estado | Notas |
|---|---|---|---|
| `tests/bootstrap.php` | `tests/conftest.py` (+ `[tool.pytest.ini_options]` en `pyproject.toml`) | pendiente | autoload de composer → pytest |
| `tests/TestCase.php` | `tests/conftest.py` (`file_path` / `file_contents`) | pendiente | métodos estáticos → fixtures |
| `tests/Integration/Helpers/ScraperHelper.php` | `tests/integration/helpers.py` (`ScraperHelper`) | pendiente | subclase que pisa `pdf_to_text_content` |
| `tests/Integration/ScrapCsfFromRfcAndCifTest.php` | `tests/integration/test_scrap_csf_from_rfc_and_cif.py` | pendiente | MockHandler → respx (7 tests) |
| `tests/Integration/ScrapFromCsfFileTest.php` | `tests/integration/test_scrap_from_csf_file.py` | pendiente | 2 tests con red real → respx (§4); 3 tests con `pdftotext` |
| `tests/Unit/ScraperTest.php` | `tests/unit/test_scraper.py` | pendiente | `getConfig('curl')` → introspección del `SSLContext` (§5) |
| `tests/Unit/Exceptions/CifDownloadExceptionTest.php` | `tests/unit/exceptions/test_cif_download_exception.py` | pendiente | |
| `tests/Unit/Exceptions/CifNotFoundExceptionTest.php` | `tests/unit/exceptions/test_cif_not_found_exception.py` | pendiente | |
| `tests/Unit/Exceptions/PdfReader/CifFromPdfNotFoundExceptionTest.php` | `tests/unit/exceptions/pdf_reader/test_cif_from_pdf_not_found_exception.py` | pendiente | |
| `tests/Unit/Exceptions/PdfReader/EmptyPdfContentExceptionTest.php` | `tests/unit/exceptions/pdf_reader/test_empty_pdf_content_exception.py` | pendiente | |
| `tests/Unit/Exceptions/PdfReader/PdfToTextConvertExceptionTest.php` | `tests/unit/exceptions/pdf_reader/test_pdf_to_text_convert_exception.py` | pendiente | |
| `tests/Unit/Exceptions/PdfReader/RfcFromPdfNotFoundExceptionTest.php` | `tests/unit/exceptions/pdf_reader/test_rfc_from_pdf_not_found_exception.py` | pendiente | |
| `tests/Unit/PdfReader/CsfExtractor/GetCifIdTest.php` | `tests/unit/pdf_reader/csf_extractor/test_get_cif_id.py` | pendiente | |
| `tests/Unit/PdfReader/CsfExtractor/GetRfcTest.php` | `tests/unit/pdf_reader/csf_extractor/test_get_rfc.py` | pendiente | |
| `tests/Unit/PdfReader/PdfToText/PdfToTextConstructorTest.php` | `tests/unit/pdf_reader/pdf_to_text/test_pdf_to_text_constructor.py` | pendiente | `RuntimeException` de Symfony → `FileNotFoundError` (§5) |
| `tests/Unit/Persona/CommonPersonaPropertiesTest.php` | `tests/unit/persona/test_common_persona_properties.py` | pendiente | data providers → `@pytest.mark.parametrize` |
| `tests/Unit/Persona/PersonaFisicaPropertiesTest.php` | `tests/unit/persona/test_persona_fisica_properties.py` | pendiente | |
| `tests/Unit/Persona/PersonaMoralPropertiesTest.php` | `tests/unit/persona/test_persona_moral_properties.py` | pendiente | |
| `tests/Unit/Persona/PersonaJsonSerializeTest.php` | `tests/unit/persona/test_persona_json_serialize.py` | pendiente | |
| `tests/Unit/Persona/Traits/PersonaTrait.php` | `tests/unit/persona/traits/persona_trait.py` | pendiente | trait con tests → módulo cuyas funciones se importan en cada test module |
| `tests/Unit/RegimenesTest.php` | `tests/unit/test_regimenes.py` | pendiente | |
| `tests/Unit/Regimen/RegimenJsonSerializeTest.php` | `tests/unit/regimen/test_regimen_json_serialize.py` | pendiente | |
| `tests/Unit/Regimen/RegimenesJsonSerializeTest.php` | `tests/unit/regimen/test_regimenes_json_serialize.py` | pendiente | |
| `tests/Unit/Regimen/SetRegimenTest.php` | `tests/unit/regimen/test_set_regimen.py` | pendiente | 21+3 casos del data provider → parametrize |
| `tests/_files/csf-bad-content.txt` | `tests/_files/csf-bad-content.txt` | pendiente | copia literal |
| `tests/_files/csf-content.txt` | `tests/_files/csf-content.txt` | pendiente | copia literal |
| `tests/_files/csf-correct-but-invalid.pdf` | `tests/_files/csf-correct-but-invalid.pdf` | pendiente | copia literal |
| `tests/_files/csf-without-cif.pdf` | `tests/_files/csf-without-cif.pdf` | pendiente | copia literal |
| `tests/_files/csf-without-rfc.pdf` | `tests/_files/csf-without-rfc.pdf` | pendiente | copia literal |
| `tests/_files/error.html` | `tests/_files/error.html` | pendiente | copia literal |
| `tests/_files/scrap_fisica.html` | `tests/_files/scrap_fisica.html` | pendiente | copia literal |
| `tests/_files/scrap_moral.html` | `tests/_files/scrap_moral.html` | pendiente | copia literal |
| `tests/_files/scrap_moral_without_colonia.html` | `tests/_files/scrap_moral_without_colonia.html` | pendiente | copia literal |
| `tests/_files/scrap_regimenes.html` | `tests/_files/scrap_regimenes.html` | pendiente | copia literal |

**Recuento de tests origen**: 53 métodos de test → **90 casos de test** (40 expandidos por data providers/traits).
Desglose: Integration 12, Persona 31 (17+7+5 de las 3 clases con trait +2 json), Regimén 30 (28+2 json), Regimenes 1, Scraper 1, Exceptions 8, PdfReader 7.

## 3. Uso de `Symfony\Component\Process` en `src/` (Fase 0.c)

Un único punto de uso: **`src/PdfReader/PdfToText.php`**.

| Elemento | Detalle |
|---|---|
| Qué ejecuta | binario externo `pdftotext` (paquete del sistema `poppler-utils`), por defecto buscado en el `PATH` (constructor permite ruta alternativa) |
| Por qué | convertir el PDF de la *Constancia de Situación Fiscal* a texto plano para extraer RFC y idCIF (`CsfExtractor`) |
| Comando construido (`buildCommand`) | `['pdftotext', '-eol', 'unix', '-raw', '-q', <ruta pdf>, '-']` (lista, sin shell) |
| Entrada | ruta de un archivo PDF local (`extract(string $path)`) |
| Salida | `stdout` del proceso como texto; en error: excepción `PdfToTextConvertException` con `command`, `exitCode`, `stdout`, `stderr` |
| Comportamiento en error de binario inexistente | Symfony `Process::run()` lanza `RuntimeException` (no es una excepción de la librería; los tests la esperan con `expectException(RuntimeException::class)`) |

**Reemplazabilidad**: NO es reemplazable con `httpx` ni con la stdlib pura (no hay extracción de texto de PDF en la stdlib). Requiere **`subprocess`** (stdlib) invocando el mismo binario externo `pdftotext` (poppler-utils), idéntico requisito de despliegue que el original.
**Mapeo de excepción**: `RuntimeException` de Symfony (binario no encontrado) → `FileNotFoundError` de la stdlib (lanzada por `subprocess.run`), documentado en `docs/differences.md`.

## 4. Tests, fixtures y cómo se mockea HTTP (Fase 0.d)

### Fixtures (`tests/_files/`, 10 archivos, se copian literales; no se inventa ninguno)
- HTML: `scrap_moral.html`, `scrap_fisica.html`, `scrap_moral_without_colonia.html`, `scrap_regimenes.html` (páginas SAT "ok"), `error.html` (página SAT sin información; contiene `span.ui-messages-info-detail`).
- Texto de `pdftotext`: `csf-content.txt` (contenido válido, rfc `DIM8701081LA`, idCIF `12345678`), `csf-bad-content.txt` (sin líneas `RFC:`/`idCIF:`).
- PDFs: `csf-correct-but-invalid.pdf`, `csf-without-rfc.pdf`, `csf-without-cif.pdf` (se procesan con `pdftotext` real en los tests Linux-only).

### Cómo mockean HTTP los tests originales
| Test | Mecanismo | Replicación prevista con respx |
|---|---|---|
| `ScrapCsfFromRfcAndCifTest` (6 tests vía `prepareScraper`) | `GuzzleHttp\Handler\MockHandler` con `Response(200, [], fileContents(html))` | `respx` ruta GET al URL exacto del validador SAT devolviendo 200 + contenido del fixture |
| `ScrapCsfFromRfcAndCifTest::test_throw_exception_on_download_error` | `MockHandler` con excepción `GuzzleException` mockeada | `respx` con `side_effect=httpx.ConnectError(...)` |
| `ScrapFromCsfFileTest::test_scrap_from_idcif_and_rfc_by_moral` | igual que arriba (usa `ScraperHelper`) | igual que arriba |
| `ScrapFromCsfFileTest::test_obtain_from_pdf_with_invalid_url` | **RED REAL** (`Scraper::create()` contra `sat.gob.mx`) | ver §6 — pendiente de confirmación |
| `ScrapFromCsfFileTest::test_obtain_from_pdf_with_invalid_data` | **RED REAL** (`Scraper::create()` contra `siat.sat.gob.mx`) | ver §6 — pendiente de confirmación |
| El resto (unit/exceptions/pdf/persona/regimen) | sin HTTP | sin HTTP |

Ningún test del original afirma el URL construido (el `MockHandler` responde sin importar la URL); en la portación la ruta respx se fija al URL completo esperado (`?D1=10&D2=1&D3=<idCIF>_<RFC>`), lo cual además valida el formateo.

## 5. TLS, headers, cookies, user-agent, reintentos, timeouts (Fase 0.e)

| Aspecto | Original | Mapeo Python |
|---|---|---|
| TLS cipher | `Scraper::create()` configura Guzzle `'curl' => [CURLOPT_SSL_CIPHER_LIST => 'DEFAULT@SECLEVEL=1']` (SAT exige cipher chain débil) | `ssl.create_default_context()` + `set_ciphers('DEFAULT@SECLEVEL=1')` pasado a `httpx.Client(verify=...)`; verificado en este entorno: `ctx.security_level == 1` después de aplicarlo (OpenSSL 3.5.8). Los tests mockeados no lo necesitan |
| Verificación certificados | Guzzle `verify=true` (CA del sistema) por defecto | `httpx` `verify=True` por defecto ✓ |
| Headers | ninguno personalizado; el `User-Agent` es el por defecto de Guzzle (`GuzzleHttp/7`) | ninguno personalizado; `User-Agent` por defecto de httpx (`python-httpx/…`). Sin impacto en tests; documentar en `differences.md` |
| Cookies | sin middleware de cookies → cada petición independiente | `httpx.Client` tiene jar de cookies; el flujo hace **una** petición por invocación, sin impacto. Documentar |
| Redirecciones | Guzzle: sigue redirecciones por defecto (máx 5) | `Scraper.create()` usará `follow_redirects=True` para equivalencia; clientes inyectados dependen de su configuración (igual que en el original) |
| Reintentos | ninguno | ninguno ✓ |
| Timeout | Guzzle: sin timeout (0) por defecto | `Scraper.create()` usará `timeout=None` (sin timeout) para equivalencia; un cliente inyectado usa su propia config |
| `http_errors` | Guzzle lanza excepción en 4xx/5xx → capturado como `CifDownloadException` | `response.raise_for_status()` + captura de `httpx.HTTPError` → `CifDownloadException` |
| Codificación cuerpo | cast `(string) $response->getBody()` (bytes) → se parsea como HTML | `response.text` (httpx asume UTF-8 sin `charset`; los fixtures son UTF-8) |

## 6. Comportamientos que requieren decisión (Fase 0 — reportados)

1. **Dos tests originales usan red real contra el SAT** (prohibido por la regla 5):
   - `test_obtain_from_pdf_with_invalid_url`: cambia `Scraper::$url` a `sat.gob.mx` y espera `CifDownloadException` de una petición real.
   - `test_obtain_from_pdf_with_invalid_data`: pide a `siat.sat.gob.mx` con el RFC/CIF extraídos de `csf-correct-but-invalid.pdf` y espera `CifNotFoundException` de la página de error real.
   - Propuesta: mockear con respx conservando la intención (URL alterno → `ConnectError`; respuesta = fixture `error.html` → `CifNotFoundException`) sin tocar red. **Pendiente de confirmación.**
2. **`symfony/process` → `subprocess` + binario externo `pdftotext`** (§3): fuera del stack "pip" pero permitido como stdlib; el binario externo era requisito ya del original.
3. **`test_create_with_specific_openssl_cipher_list`** depende del deprecado `Client::getConfig('curl')`: se sustituye por asertar sobre el `SSLContext` resultante (`security_level == 1` y ciphers configurados) — adaptación documentada.
4. **`test_throw_exception_when_path_not_found`** espera `RuntimeException` (Symfony): en Python espera `FileNotFoundError` (stdlib).
5. **JSON de fechas**: `json_encode` de PHP produce `{"date": …, "timezone_type": 3, "timezone": "UTC"}`; el port usará ISO-8601 (pydantic). Los tests JSON del original solo usan fechas `null`, por lo que no hay conflicto de expectativas.
6. **`test_return_empty_when_not_found`** tiene código muerto tras `expectException` (`assertSame([], $data)` nunca se ejecuta) y una variable `$expectedData` sin uso: se migra solo la parte viva (`pytest.raises`).
