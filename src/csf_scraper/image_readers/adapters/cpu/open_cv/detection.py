from __future__ import annotations

from dataclasses import dataclass, field

import cv2
import numpy as np

from .config import DetectionConfig
from .enhance import apply_clahe, to_gray
from .errors import InvalidGeometryError
from .transform import order_points


@dataclass(slots=True)
class DetectionResult:
    quad: np.ndarray | None
    confidence: float
    method: str
    scale: float
    debug: dict[str, np.ndarray] = field(default_factory=dict)
    variant: str = ""

    @property
    def found(self) -> bool:
        return self.quad is not None


def _prepare_work_image(gray: np.ndarray, config: DetectionConfig) -> tuple[np.ndarray, float]:
    height, width = gray.shape[:2]
    scale = min(1.0, config.resize_height / float(height))
    if scale < 1.0:
        size = (max(1, int(round(width * scale))), max(1, int(round(height * scale))))
        work = cv2.resize(gray, size, interpolation=cv2.INTER_AREA)
    else:
        work = gray.copy()

    if config.use_clahe:
        work = apply_clahe(work, config.clahe_clip_limit, config.clahe_tile_grid)

    return work, scale


def _edge_masks(
    work: np.ndarray,
    config: DetectionConfig,
) -> tuple[np.ndarray, np.ndarray, list[tuple[str, np.ndarray]]]:
    blurred = cv2.GaussianBlur(
        work,
        (config.blur_ksize, config.blur_ksize),
        0,
    )
    edges = cv2.Canny(blurred, config.canny_low, config.canny_high)

    small_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (config.dilate_kernel, config.dilate_kernel),
    )
    small_dilated = cv2.dilate(edges, small_kernel, iterations=1)
    dilated = cv2.dilate(edges, kernel, iterations=config.dilate_iterations)
    closed = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel)

    bright_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (config.bright_open_kernel, config.bright_open_kernel),
    )
    _, bright = cv2.threshold(
        work,
        0,
        255,
        cv2.THRESH_BINARY | cv2.THRESH_OTSU,
    )
    bright = cv2.morphologyEx(bright, cv2.MORPH_OPEN, bright_kernel)
    bright_ratio = cv2.countNonZero(bright) / float(bright.size)

    masks = [
        ("raw", edges),
        ("dilate_small", small_dilated),
        ("dilate_close", closed),
    ]
    if 0.02 < bright_ratio < 0.98:
        masks.append(("bright", bright))
    return edges, closed, masks


def _approx_quad(contour: np.ndarray, epsilon_ratios: tuple[float, ...]) -> np.ndarray | None:
    hull = cv2.convexHull(contour)
    perimeter = cv2.arcLength(hull, True)
    if perimeter <= 0:
        return None
    for ratio in epsilon_ratios:
        approx = cv2.approxPolyDP(hull, ratio * perimeter, True)
        if len(approx) == 4:
            return approx.reshape(4, 2).astype(np.float32)
    return None


def _iter_candidates(
    contours: list[np.ndarray],
    image_area: float,
    config: DetectionConfig,
):
    valid: list[np.ndarray] = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area <= 0:
            continue
        ratio = area / image_area
        if config.min_area_ratio <= ratio <= config.max_area_ratio:
            valid.append(contour)

    if not valid:
        valid = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    for contour in valid:
        area = cv2.contourArea(contour)
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        solidity = area / hull_area if hull_area > 0 else 0.0

        approx = _approx_quad(hull, config.approx_epsilon_ratios)
        if approx is not None:
            yield approx, "approx", solidity

        rect = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect).astype(np.float32)
        yield box, "min_area_rect", solidity

    if valid:
        merged = np.vstack([contour.reshape(-1, 2) for contour in valid]).astype(np.float32)
        merged_hull = cv2.convexHull(merged.reshape(-1, 1, 2))

        approx = _approx_quad(merged_hull, config.approx_epsilon_ratios)
        if approx is not None:
            yield approx, "merged_hull", 1.0

        box = cv2.boxPoints(cv2.minAreaRect(merged_hull)).astype(np.float32)
        yield box, "merged_hull_rect", 1.0


def _score_candidate(
    quad: np.ndarray,
    image_shape: tuple[int, int],
    solidity: float,
    method: str,
) -> tuple[float, np.ndarray | None]:
    try:
        ordered = order_points(quad)
    except InvalidGeometryError:
        return -1.0, None

    image_height, image_width = image_shape
    image_area = float(image_height * image_width)
    area = abs(cv2.contourArea(ordered))
    if area <= 0:
        return -1.0, None

    area_ratio = area / image_area
    if area_ratio < 0.02 or area_ratio > 1.0:
        return -1.0, None

    rect = cv2.minAreaRect(ordered.astype(np.float32))
    rect_width, rect_height = rect[1]
    rect_area = max(float(rect_width) * float(rect_height), 1e-6)
    rectangularity = min(1.0, area / rect_area)

    long_side = max(rect_width, rect_height)
    short_side = max(min(rect_width, rect_height), 1e-6)
    aspect = long_side / short_side

    score = area_ratio * (0.5 + 0.5 * rectangularity)
    score *= 0.7 + 0.3 * max(0.0, min(1.0, solidity))

    if aspect < 0.25 or aspect > 4.0:
        score *= 0.5
    if area_ratio > 0.97:
        score *= 0.2
    elif area_ratio > 0.90:
        score *= 0.5

    margin_x = 0.015 * image_width
    margin_y = 0.015 * image_height
    border_contacts = int(
        np.count_nonzero(
            (ordered[:, 0] < margin_x)
            | (ordered[:, 0] > image_width - 1 - margin_x)
            | (ordered[:, 1] < margin_y)
            | (ordered[:, 1] > image_height - 1 - margin_y)
        )
    )
    if border_contacts:
        score *= 0.55**border_contacts

    score *= {
        "approx": 1.0,
        "merged_hull": 1.0,
        "min_area_rect": 0.6,
        "merged_hull_rect": 0.6,
    }.get(method, 0.8)

    return float(min(score, 1.0)), ordered


def detect_document(
    image: np.ndarray,
    config: DetectionConfig | None = None,
) -> DetectionResult:
    cfg = config or DetectionConfig()
    if image is None or image.size == 0:
        raise ValueError("image cannot be empty")

    gray = to_gray(image)
    height, width = gray.shape[:2]
    work, scale = _prepare_work_image(gray, cfg)
    edges, closed, masks = _edge_masks(work, cfg)

    image_area = float(work.shape[0] * work.shape[1])
    image_shape = (work.shape[0], work.shape[1])
    best_score = -1.0
    best_quad: np.ndarray | None = None
    best_method = "none"
    best_variant = ""

    for variant, mask in masks:
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            continue
        for quad, method, solidity in _iter_candidates(contours, image_area, cfg):
            score, ordered = _score_candidate(quad, image_shape, solidity, method)
            if ordered is not None and score > best_score:
                best_score = score
                best_quad = ordered
                best_method = method
                best_variant = variant

    debug = {
        "gray": gray,
        "work": work,
        "edges": edges,
        "closed": closed,
    }

    if best_quad is None:
        return DetectionResult(None, 0.0, "none", scale, debug, "")

    if best_score < cfg.min_confidence:
        return DetectionResult(
            None,
            max(best_score, 0.0),
            best_method,
            scale,
            debug,
            best_variant,
        )

    quad_original = best_quad / scale
    quad_original[:, 0] = np.clip(quad_original[:, 0], 0, width - 1)
    quad_original[:, 1] = np.clip(quad_original[:, 1], 0, height - 1)

    return DetectionResult(
        quad_original.astype(np.float32),
        best_score,
        best_method,
        scale,
        debug,
        best_variant,
    )
