# Diferencias PHP → Python (phpcfdi/csf-scraper)

Adaptaciones de comportamiento de la migración a Python. La intención de cada test
y de cada flujo se conserva salvo donde se indica explícitamente.

## 1. API pública

| Aspecto                         | PHP                                                                       | Python                                                                                                                                                     |
| ------------------------------- | ------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RFC como parámetro              | `obtainFromRfcAndCif(Rfc $rfc, string $idCIF)` (objeto de `phpcfdi/rfc`)  | `obtain_from_rfc_and_cif(rfc: str, id_cif: str)`; los value objects `Rfc` / `IdCif` se construyen dentro del método (y también aceptan instancias)         |
| Validación del RFC              | `Rfc::parse()` lanza `InvalidExpressionToParseException`                  | `Rfc(str)` valida con expresión regular y lanza `InvalidRfcFormatException` (subclase de `CsfScraperException` y `ValueError`)                             |
| Validación del idCIF            | no existe (cadena libre)                                                  | `IdCif(str)` exige solo dígitos y longitud 8–13; lanza `InvalidIdCifFormatException`                                                                       |
| ¿Es persona física?             | `$rfc->isFisica()`                                                        | `Rfc(...).is_fisica()` → `len(self) == 13` (idéntico al original)                                                                                          |
| Getters/setters                 | `getRfc()` / `setRfc()` …                                                 | atributos directos: `person.rfc`, `person.id_cif`, … (los getters/setters de PHP se colapsan a atributos)                                                  |
| `toArray()` / `jsonSerialize()` | `to_dict()` / `json`                                                      | `to_dict()` / `person.model_dump_json()`                                                                                                                   |
| Datos dinámicos                 | `Persona::$data` vía `__set`/`__get`                                      | `Persona.extra_data` (dict) vía `__setattr__`/`__getattr__`/`__delattr__`                                                                                  |
| Resolución de nombres           | `is_callable` (insensible a mayúsculas) sobre `set{Nombre}`/`get{Nombre}` | normalización `nombre.replace("_", "").lower()` contra los campos del modelo (admite `Curp` → `curp`, `ApellidoPaterno` → `apellido_paterno`, `Al` → `al`) |
| `__isset($person->x)`           | `isset()` → `__isset()`                                                   | `getattr(person, "x", None) is not None` (los ausentes lanzan `AttributeError`)                                                                            |
| `__unset($person->x)`           | borra de `$data`                                                          | `del person.x`                                                                                                                                             |
| Interfaces                      | `DataExtractorInterface`, `ScraperInterface`                              | no se conservan: `DataExtractor` y `Scraper` exponen sus métodos directamente                                                                              |
| Cliente HTTP                    | `GuzzleHttp\ClientInterface` inyectado                                    | `httpx.AsyncClient` concreto inyectado (no hay `HttpClientInterface`; el original tampoco define una interfaz propia)                                      |
| URL del validador               | `public static string $url`                                               | `Scraper.url: ClassVar[str]` (mutable por clase, como en PHP)                                                                                              |
| Inmutabilidad                   | `final readonly` (`DataExtractor`, `CsfExtractor`, `PdfToText`)           | clases normales; Python no lo impone (los atributos solo se escriben en `__init__` o internamente)                                                         |

### 1.1 Value objects

Los value objects son subclases de `str` (`__slots__ = ()`): se comportan como
cadenas, se comparan y serializan como texto plano y no necesitan
`BeforeValidator` porque exponen `__get_pydantic_core_schema__`.

| Value object | PHP                                  | Python                                                                                        |
| ------------ | ------------------------------------ | --------------------------------------------------------------------------------------------- |
| RFC          | `PhpCfdi\Rfc\Rfc` (librería externa) | `csf_scraper.value_objects.Rfc` (propio; sin dependencias externas)                           |
| idCIF        | — (cadena)                           | `csf_scraper.value_objects.IdCif`                                                             |
| Imagen CSF   | —                                    | `csf_scraper.value_objects.CsfImage` (magic bytes JPEG/PNG, `as_base64()`, `get_mime_type()`) |

### 1.2 Estrategias de extracción

Se introduce un patrón _strategy_ con puertos (`ABC`) y un DTO compartido,
separando dos responsabilidades que suelen confundirse:

- **Origen** (contrato público de `Scraper`): `RfcCifExtractorPort`, que recibe
  una **ruta** de archivo.
- **Motor** (cómo se lee una imagen ya cargada): `ImageReaderPort`, que recibe
  una `CsfImage` en memoria.

| Puerto                | Implementación                                                | Firma                                       |
| --------------------- | ------------------------------------------------------------- | ------------------------------------------- |
| `RfcCifExtractorPort` | `CsfPdfExtractor` (texto de `pdftotext` + `PdfCsfTextParser`) | `async extract(path: str) -> RfcCifData`    |
| `RfcCifExtractorPort` | `CsfImageExtractor` (puente ruta → motor)                     | `async extract(path: str) -> RfcCifData`    |
| `ImageReaderPort`     | `GeminiImageReader` (hereda de `LlmImageReaderService`), OCR  | `async read(image: CsfImage) -> RfcCifData` |

Decisiones asociadas:

- La ruta viaja **en el método** (`extract(path)`), no en el constructor: los
  extractores son sin estado y reutilizables; el constructor queda reservado
  para la configuración del motor (API key, modelo, binario alternativo…).
- `CsfImageExtractor` adapta cualquier `ImageReaderPort` al contrato de ruta,
  de modo que OCR y LLM comparten la misma firma pública y `Scraper` nunca
  distingue motores.

Los adaptadores basados en LLM (Gemini, DeepSeek…) heredan de la clase abstracta
`LlmImageReaderService` e implementan `ImageReaderPort`. La base aporta el
método plantilla `_run_program(image, llm_provider) -> RfcCifData`, que arma el
prompt y el `ImageBlock`, ejecuta el programa multimodal mediante
`_image_to_schema(...)` y mapea el `RfcCifSchema` a `RfcCifData`. El adaptador
solo crea su cliente de LlamaIndex y expone `read()` delegando en esa plantilla.
Así todos comparten el prompt (`CSF_PROMPT`), el armado del `ImageBlock`, los
reintentos, la validación con los value objects y el mapeo del esquema tipado a
`RfcCifData`.

La respuesta del modelo se modela con `RfcCifSchema`, un `BaseModel` cuyos
`Field` llevan `description` para que el modelo multimodal sepa qué aspecto
tienen el RFC y el idCIF en la Constancia de Situación Fiscal. Pydantic valida
la forma; los value objects validan el formato de negocio, y sus excepciones son
las que disparan los reintentos (`MAX_RETRIES = 3`). Los fallos de transporte se
envuelven en `ImageReadingException` sin reintentarse.

`Scraper.__init__` acepta `pdf_extractor` e `image_extractor`, ambos
`RfcCifExtractorPort`; el modo por omisión sigue siendo únicamente PDF. Sin
`image_extractor`, `obtain_from_image_path` lanza
`ImageExtractorNotConfiguredException`.

> `CsfExtractor` se renombra a `CsfPdfExtractor` porque su responsabilidad
> real es extraer texto de PDF; el nuevo nombre deja espacio al extractor de
> imágenes. El parseo del texto se separó a `PdfCsfTextParser` para poder
> probarlo sin tocar el sistema de archivos.

## 2. Excepciones

| PHP                                                                                                                                | Python                                                                                                                                                                                                                   |
| ---------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `interface CsfScraperException extends Throwable`                                                                                  | clase base `CsfScraperException(Exception)`                                                                                                                                                                              |
| `CifDownloadException extends RuntimeException`                                                                                    | `CifDownloadException` (hereda de `CsfScraperException`)                                                                                                                                                                 |
| `PdfToTextConvertException extends RuntimeException`                                                                               | `PdfToTextConvertException`                                                                                                                                                                                              |
| `CifNotFoundException`, `CifFromPdfNotFoundException`, `EmptyPdfContentException`, `RfcFromPdfNotFoundException extends Exception` | mismos nombres, heredando de `CsfScraperException`                                                                                                                                                                       |
| `$exception->getPrevious()`                                                                                                        | atributo `previous` **y** encadenamiento `raise ... from` (`__cause__`)                                                                                                                                                  |
| `RuntimeException` de Symfony `Process` (binario `pdftotext` inexistente)                                                          | `FileNotFoundError` de la stdlib (lanzado por `subprocess.run`)                                                                                                                                                          |
| `InvalidExpressionToParseException` (`phpcfdi/rfc`)                                                                                | `InvalidRfcFormatException` (value object `Rfc`)                                                                                                                                                                         |
| — (no existe)                                                                                                                      | `InvalidIdCifFormatException`, `InvalidImageException`, `InvalidImageFormatException`, `ImageExtractorNotConfiguredException`, `ImageReadingException`, `RfcFromImageNotFoundException`, `CifFromImageNotFoundException` |
| `CifDownloadException` captura 4xx/5xx (`http_errors` de Guzzle)                                                                   | `response.raise_for_status()` dentro del `try` → `httpx.HTTPStatusError` → `CifDownloadException`                                                                                                                        |

Todos los códigos/atributos originales se conservan: `CifDownloadException` mantiene
`url` y `previous`; `PdfToTextConvertException` mantiene `command`, `exit_code`,
`output` y `error`.

## 3. JSON y fechas

- PHP `json_encode($person)` serializa `DateTimeImmutable` como
  `{"date": "…", "timezone_type": 3, "timezone": "UTC"}`.
- Python `model_dump_json()` serializa las fechas como ISO-8601
  (`"2019-02-21T00:00:00"`) y los `None` como `null`.
- `to_dict()` en ambos devuelve objetos fecha (no cadenas): `DateTimeImmutable`
  vs `datetime` de Python (naive, construido con `strptime('%d-%m-%Y')`).
- Los tests JSON del original solo comparan fechas `null`, por lo que no hay
  expectativas en conflicto.

## 4. Infraestructura

| Aspecto         | PHP                                                  | Python                                                                                                                                             |
| --------------- | ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| HTTP            | Guzzle (`follow_redirects` por defecto, sin timeout) | `httpx.AsyncClient(follow_redirects=True, timeout=None)` en `Scraper.create()`                                                                     |
| Cifrado TLS     | `CURLOPT_SSL_CIPHER_LIST => 'DEFAULT@SECLEVEL=1'`    | `ssl.SSLContext.set_ciphers('DEFAULT@SECLEVEL=1')` (verificado: `security_level == 1`)                                                             |
| User-Agent      | `GuzzleHttp/7`                                       | `python-httpx/…` (sin impacto en el flujo)                                                                                                         |
| Cookies         | sin middleware                                       | `httpx.AsyncClient` tiene jar; el flujo hace una petición por invocación                                                                           |
| PDF → texto     | `symfony/process` (`Process::run`)                   | `subprocess.run` (misma lista de argumentos, sin shell)                                                                                            |
| Binario externo | `pdftotext` (`poppler-utils`)                        | idéntico requisito de despliegue                                                                                                                   |
| Parsing HTML    | `symfony/dom-crawler` (CSS + XPath)                  | `BeautifulSoup` + `lxml` (selectores CSS; el XPath `contains(normalize-space(.), …)` se emula con normalización en Python)                         |
| Texto           | `trim()`/`preg_replace` nativos                      | normalización nativa en `data_extractor.py` (`" ".join(value.split())`), equivalente a `trim` y `\s` de PHP                                        |

## 5. Adaptaciones de tests (solo tests)

1. `test_obtain_from_pdf_with_invalid_url` y
   `test_obtain_from_pdf_with_invalid_data` usaban **red real** contra el SAT;
   se migran con respx conservando nombre e intención (ConnectError en el host
   alterno → `CifDownloadException`; fixture `error.html` → `CifNotFoundException`).
2. `test_create_with_specific_openssl_cipher_list` usaba el deprecado
   `Client::getConfig('curl')`; en Python se introspecciona el `SSLContext`
   resultante y se afirma `security_level == 1` (el equivalente del cipher).
3. `test_throw_exception_when_path_not_found` esperaba `RuntimeException` de
   Symfony; en Python espera `FileNotFoundError`.
4. `test_return_empty_when_not_found` arrastra código muerto en PHP
   (`$expectedData` sin usar y `assertSame` tras `expectException`); se migra
   solo la parte viva (`pytest.raises(CifNotFoundException)`).
5. Los atributos `#[RequiresOperatingSystem('Linux')]` se traducen a
   `@pytest.mark.skipif(platform.system() != "Linux")`.
6. El original no tiene tests unitarios de `DataExtractor` (sus tests son los de
   integración); la portación no añade tests nuevos para no alterar el recuento
   de casos.
7. `tests/TestCase.php` (lectura de fixtures) se implementa como funciones en
   `tests/helpers.py`; el trait `PersonaTrait` como módulo cuyas funciones se
   importan en cada módulo de test.
