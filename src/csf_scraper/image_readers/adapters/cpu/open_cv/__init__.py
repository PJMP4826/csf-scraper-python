from .config import DetectionConfig, EnhancementConfig, ScanConfig
from .detection import DetectionResult, detect_document
from .enhance import enhance_for_ocr, to_gray
from .errors import (
    DocumentNotFoundError,
    DocumentScannerError,
    ImageLoadError,
    ImageSaveError,
    InvalidGeometryError,
)
from .io import load_image, save_image
from .pipeline import ScanResult, scan_array
from .transform import four_point_transform, order_points, scale_points

__version__ = "0.1.0"

__all__ = [
    "DetectionConfig",
    "DetectionResult",
    "DocumentNotFoundError",
    "DocumentScannerError",
    "EnhancementConfig",
    "ImageLoadError",
    "ImageSaveError",
    "InvalidGeometryError",
    "ScanConfig",
    "ScanResult",
    "detect_document",
    "enhance_for_ocr",
    "four_point_transform",
    "load_image",
    "order_points",
    "save_image",
    "scale_points",
    "scan_array",
    "to_gray",
]
