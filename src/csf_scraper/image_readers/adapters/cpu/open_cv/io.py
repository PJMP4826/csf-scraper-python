from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from .errors import ImageLoadError, ImageSaveError


def load_image(path: str | Path) -> np.ndarray:
    source = Path(path)
    if not source.is_file():
        raise ImageLoadError(f"image not found: {source}")

    image = cv2.imread(str(source), cv2.IMREAD_COLOR)
    if image is None:
        raise ImageLoadError(f"could not decode image: {source}")
    return image


def save_image(path: str | Path, image: np.ndarray) -> Path:
    destination = Path(path)
    if image is None or image.size == 0:
        raise ImageSaveError("refusing to save an empty image")

    destination.parent.mkdir(parents=True, exist_ok=True)
    success = cv2.imwrite(str(destination), image)
    if not success:
        raise ImageSaveError(f"could not write image: {destination}")
    return destination
