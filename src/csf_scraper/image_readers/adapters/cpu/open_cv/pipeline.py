from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .config import ScanConfig
from .detection import DetectionResult, detect_document
from .enhance import enhance_for_ocr
from .errors import DocumentNotFoundError, InvalidGeometryError
from .qr import decode_qr
from .transform import four_point_transform


@dataclass(slots=True)
class ScanResult:
    image: np.ndarray
    warped: np.ndarray
    source: np.ndarray
    detection: DetectionResult
    method: str
    confidence: float
    config: ScanConfig = field(repr=False)
    qr_code: str | None = None


def _full_image_quad(image: np.ndarray) -> np.ndarray:
    height, width = image.shape[:2]
    return np.array(
        [
            [0, 0],
            [width - 1, 0],
            [width - 1, height - 1],
            [0, height - 1],
        ],
        dtype=np.float32,
    )


def scan_array(image: np.ndarray, config: ScanConfig | None = None) -> ScanResult:
    cfg = config or ScanConfig()
    if image is None or image.size == 0:
        raise ValueError("image cannot be empty")

    detection = detect_document(image, cfg.detection)
    used_fallback = detection.quad is None

    if not used_fallback:
        try:
            warped, _ = four_point_transform(image, detection.quad)
        except InvalidGeometryError:
            if not cfg.allow_full_image_fallback:
                raise
            used_fallback = True

    if used_fallback:
        if not cfg.allow_full_image_fallback:
            raise DocumentNotFoundError("document boundary not found")
        warped = image.copy()
        quad = _full_image_quad(image)
        method = "full_image_fallback"
        confidence = 0.0
    else:
        quad = detection.quad
        method = detection.method
        confidence = detection.confidence

    qr_code = decode_qr(warped, image)
    enhanced = enhance_for_ocr(warped, cfg.enhancement)
    detection_out = DetectionResult(
        quad=quad,
        confidence=confidence,
        method=method,
        scale=detection.scale,
        debug=detection.debug,
        variant=detection.variant,
    )
    return ScanResult(
        image=enhanced,
        warped=warped,
        source=image,
        detection=detection_out,
        method=method,
        confidence=confidence,
        config=cfg,
        qr_code=qr_code,
    )
