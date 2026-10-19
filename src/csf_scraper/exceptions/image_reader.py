"""Excepciones del lector de imágenes (CSF escaneada)."""

from csf_scraper.exceptions import CsfScraperException


class InvalidImageException(CsfScraperException):
    """La ruta de la imagen no existe o no puede leerse."""


class InvalidImageFormatException(CsfScraperException):
    """El archivo recibido no es una imagen soportada (JPEG o PNG)."""


class ImageExtractorNotConfiguredException(CsfScraperException):
    """No se inyectó un extractor de imágenes (motor LLM/OCR)."""

    def __init__(self) -> None:
        super().__init__(
            "An image extractor is required to obtain the data from an image; "
            "inject one via Scraper(..., image_extractor=...).",
        )


class ImageReadingException(CsfScraperException):
    """El motor de lectura de imágenes (LLM/OCR) falló al procesar la CSF.

    ``provider`` y ``model`` identifican el motor que falló, de modo que un
    adaptador pueda reportar el origen del error sin exponer credenciales.
    """

    def __init__(
        self,
        message: str = "The image reader failed to process the CSF.",
        *,
        provider: str | None = None,
        model: str | None = None,
    ) -> None:
        super().__init__(message)
        self.provider = provider
        self.model = model


class ImageReaderApiException(ImageReadingException):
    """La API del proveedor del modelo respondió con un error.

    Es la traducción propia de las excepciones de cada proveedor: el resto de
    la librería no importa ni conoce las librerías de Gemini, OpenAI, etc.

    ``status_code`` es el código HTTP devuelto por el proveedor (``None`` si no
    hubo respuesta, por ejemplo en un fallo de red) y ``retryable`` indica si
    vale la pena volver a intentarlo: los fallos temporales (saturación,
    indisponibilidad, límite de peticiones, red) sí lo son; los de credenciales
    o de petición mal formada, no.
    """

    def __init__(
        self,
        message: str = "The model provider API returned an error.",
        *,
        provider: str | None = None,
        model: str | None = None,
        status_code: int | None = None,
        retryable: bool = False,
    ) -> None:
        super().__init__(message, provider=provider, model=model)
        self.status_code = status_code
        self.retryable = retryable


class ImageReaderUnavailableException(ImageReaderApiException):
    """El servicio del proveedor está saturado, caído o no es alcanzable.

    Siempre es reintentable: la misma imagen y las mismas credenciales pueden
    funcionar una vez que el proveedor se recupere.
    """

    def __init__(
        self,
        message: str = "The model provider is temporarily unavailable.",
        *,
        provider: str | None = None,
        model: str | None = None,
        status_code: int | None = None,
    ) -> None:
        super().__init__(
            message,
            provider=provider,
            model=model,
            status_code=status_code,
            retryable=True,
        )


class ImageReaderAuthenticationException(ImageReaderApiException):
    """El proveedor rechazó las credenciales (API key inválida, vencida o sin permiso).

    No es reintentable: repetir la petición con la misma clave fallará igual.
    """


class RfcFromImageNotFoundException(CsfScraperException):
    """No se pudo obtener el RFC de la imagen procesada."""


class CifFromImageNotFoundException(CsfScraperException):
    """No se pudo obtener el idCIF de la imagen procesada."""
