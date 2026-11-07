from __future__ import annotations

import cv2
import numpy as np

from .config import EnhancementConfig


def to_gray(image: np.ndarray) -> np.ndarray:
    if image is None or image.size == 0:
        raise ValueError("image cannot be empty")
    if image.ndim == 2:
        return image
    channels = image.shape[2]
    if channels == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if channels == 4:
        return cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
    raise ValueError(f"unsupported channel count: {channels}")


def apply_clahe(gray: np.ndarray, clip_limit: float, tile_grid: tuple[int, int]) -> np.ndarray:
    clahe = cv2.createCLAHE(clipLimit=float(clip_limit), tileGridSize=tuple(tile_grid))
    return clahe.apply(gray)


def _upscale_if_needed(image: np.ndarray, min_width: int, max_upscale: float) -> np.ndarray:
    if min_width <= 0:
        return image
    width = image.shape[1]
    if width >= min_width:
        return image
    scale = min(min_width / float(width), max_upscale)
    if scale <= 1.0:
        return image
    size = (round(image.shape[1] * scale), round(image.shape[0] * scale))
    return cv2.resize(image, size, interpolation=cv2.INTER_CUBIC)


def _enhance_color(image: np.ndarray, config: EnhancementConfig) -> np.ndarray:
    enhanced = _upscale_if_needed(image, config.min_ocr_width, config.max_upscale)
    if not config.use_clahe:
        return enhanced
    lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)
    lightness, a_channel, b_channel = cv2.split(lab)
    lightness = apply_clahe(lightness, config.clahe_clip_limit, config.clahe_tile_grid)
    merged = cv2.merge([lightness, a_channel, b_channel])
    return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)


def _adaptive_block_size(requested: int, height: int, width: int) -> int | None:
    limit = min(height, width)
    if limit < 3:
        return None
    max_odd = limit if limit % 2 == 1 else limit - 1
    return max(3, min(requested, max_odd))


def _binarize(gray: np.ndarray, config: EnhancementConfig) -> np.ndarray:
    if config.threshold_method == "otsu":
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        return binary

    block_size = _adaptive_block_size(
        config.adaptive_block_size,
        gray.shape[0],
        gray.shape[1],
    )
    if block_size is None:
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        return binary

    return cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        block_size,
        float(config.adaptive_c),
    )


def enhance_for_ocr(image: np.ndarray, config: EnhancementConfig | None = None) -> np.ndarray:
    cfg = config or EnhancementConfig()
    if image is None or image.size == 0:
        raise ValueError("image cannot be empty")

    if cfg.mode == "color":
        return _enhance_color(image, cfg)

    gray = to_gray(image)
    gray = _upscale_if_needed(gray, cfg.min_ocr_width, cfg.max_upscale)

    if cfg.use_clahe:
        gray = apply_clahe(gray, cfg.clahe_clip_limit, cfg.clahe_tile_grid)

    if cfg.denoise:
        gray = cv2.medianBlur(gray, 3)

    if cfg.mode == "gray":
        return gray

    return _binarize(gray, cfg)
