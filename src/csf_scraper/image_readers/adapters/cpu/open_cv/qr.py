from __future__ import annotations

from urllib.parse import urlparse

import cv2
import numpy as np

SAT_QR_HOST = "siat.sat.gob.mx"
QR_MIN_SIDE = 1000
QR_MAX_SIDE = 2200


def _is_sat_qr(code: str) -> bool:
    host = (urlparse(code).hostname or "").lower()
    return host == SAT_QR_HOST or host.endswith("." + SAT_QR_HOST)


def _resize_for_qr(image: np.ndarray) -> np.ndarray:
    height, width = image.shape[:2]
    max_side = max(height, width)
    if max_side <= 0:
        return image
    if max_side > QR_MAX_SIDE:
        scale = QR_MAX_SIDE / float(max_side)
    elif max_side < QR_MIN_SIDE:
        scale = QR_MIN_SIDE / float(max_side)
    else:
        return image
    size = (max(1, int(round(width * scale))), max(1, int(round(height * scale))))
    interpolation = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC
    return cv2.resize(image, size, interpolation=interpolation)


def _to_gray(image: np.ndarray) -> np.ndarray | None:
    if image.ndim == 2:
        return image
    if image.shape[2] == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if image.shape[2] == 4:
        return cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
    return None


def _candidate_images(image: np.ndarray):
    if image is None or image.size == 0:
        return
    resized = _resize_for_qr(image)
    yield resized
    gray = _to_gray(resized)
    if gray is not None and gray is not resized:
        yield gray


def _decode_candidate(detector: cv2.QRCodeDetector, image: np.ndarray) -> str | None:
    try:
        text, points, _ = detector.detectAndDecode(image)
    except cv2.error:
        return None

    text = text.strip() if text else ""
    if text:
        return text
    if points is None:
        return None

    try:
        x, y, width, height = cv2.boundingRect(points.reshape(-1, 2).astype(np.float32))
    except cv2.error:
        return None
    if width <= 0 or height <= 0:
        return None

    pad_x = max(1, int(width * 0.2))
    pad_y = max(1, int(height * 0.2))
    x0 = max(0, x - pad_x)
    y0 = max(0, y - pad_y)
    x1 = min(image.shape[1], x + width + pad_x)
    y1 = min(image.shape[0], y + height + pad_y)
    crop = image[y0:y1, x0:x1]
    if crop.size == 0:
        return None

    crop = cv2.resize(crop, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    try:
        text, _, _ = detector.detectAndDecode(crop)
    except cv2.error:
        return None
    return text.strip() if text else None


def decode_qr(*images: np.ndarray) -> str | None:
    detector = cv2.QRCodeDetector()
    fallback: str | None = None

    for image in images:
        if image is None or image.size == 0:
            continue
        for candidate in _candidate_images(image):
            code = _decode_candidate(detector, candidate)
            if not code:
                continue
            if _is_sat_qr(code):
                return code
            if fallback is None:
                fallback = code

    return fallback
