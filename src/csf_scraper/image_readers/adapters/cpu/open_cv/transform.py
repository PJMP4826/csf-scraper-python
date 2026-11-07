from __future__ import annotations

from collections.abc import Sequence

import cv2
import numpy as np

from .errors import InvalidGeometryError

PointSet = np.ndarray | Sequence[Sequence[float]]


def _validate_points(pts: PointSet) -> np.ndarray:
    points = np.asarray(pts, dtype=np.float32).reshape(-1, 2)
    if points.shape != (4, 2):
        raise InvalidGeometryError(f"expected 4 points, got shape {points.shape}")
    if not np.isfinite(points).all():
        raise InvalidGeometryError("points contain non-finite values")
    if len(np.unique(points, axis=0)) != 4:
        raise InvalidGeometryError("points must be distinct")
    return points


def _signed_area(points: np.ndarray) -> float:
    x = points[:, 0]
    y = points[:, 1]
    return float(0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


def order_points(pts: PointSet) -> np.ndarray:
    points = _validate_points(pts)
    center = points.mean(axis=0)
    angles = np.arctan2(points[:, 1] - center[1], points[:, 0] - center[0])
    ordered = points[np.argsort(angles)]
    start = int(np.argmin(ordered.sum(axis=1)))
    ordered = np.roll(ordered, -start, axis=0)
    if _signed_area(ordered) < 0:
        ordered = ordered[[0, 3, 2, 1]]
    return ordered.astype(np.float32)


def scale_points(pts: PointSet, scale: float) -> np.ndarray:
    points = _validate_points(pts)
    if scale <= 0:
        raise InvalidGeometryError("scale must be positive")
    return points / float(scale)


def four_point_transform(
    image: np.ndarray,
    pts: PointSet,
    margin: int = 0,
) -> tuple[np.ndarray, np.ndarray]:
    if image is None or image.size == 0:
        raise InvalidGeometryError("image cannot be empty")
    if margin < 0:
        raise InvalidGeometryError("margin cannot be negative")

    rect = order_points(pts)
    if abs(_signed_area(rect)) < 1e-6:
        raise InvalidGeometryError("points do not define a valid quadrilateral")

    tl, tr, br, bl = rect
    width = max(np.linalg.norm(br - bl), np.linalg.norm(tr - tl))
    height = max(np.linalg.norm(tr - br), np.linalg.norm(tl - bl))
    width = round(width)
    height = round(height)

    if width < 2 or height < 2:
        raise InvalidGeometryError("document quad is too small")

    if margin > 0:
        width += 2 * margin
        height += 2 * margin

    offset = float(margin)
    max_x = float(width - 1)
    max_y = float(height - 1)
    dst = np.array(
        [
            [offset, offset],
            [max_x - offset, offset],
            [max_x - offset, max_y - offset],
            [offset, max_y - offset],
        ],
        dtype=np.float32,
    )

    matrix = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(
        image,
        matrix,
        (width, height),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REPLICATE,
    )
    return warped, matrix
