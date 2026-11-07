class DocumentScannerError(Exception):
    pass


class ImageLoadError(DocumentScannerError):
    pass


class ImageSaveError(DocumentScannerError):
    pass


class DocumentNotFoundError(DocumentScannerError):
    pass


class InvalidGeometryError(DocumentScannerError):
    pass
