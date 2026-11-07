from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

OutputMode = Literal["color", "gray", "bw"]
ThresholdMethod = Literal["adaptive", "otsu"]


def _require_odd_min(value: int, name: str, minimum: int = 3) -> None:
    if value < minimum or value % 2 == 0:
        raise ValueError(f"{name} must be an odd integer >= {minimum}, got {value}")


@dataclass(frozen=True, slots=True)
class DetectionConfig:
    resize_height: int = 700
    blur_ksize: int = 5
    canny_low: int = 75
    canny_high: int = 200
    dilate_kernel: int = 9
    dilate_iterations: int = 2
    min_area_ratio: float = 0.05
    max_area_ratio: float = 0.98
    bright_open_kernel: int = 5
    approx_epsilon_ratios: tuple[float, ...] = (0.02, 0.05, 0.08)
    use_clahe: bool = True
    clahe_clip_limit: float = 2.0
    clahe_tile_grid: tuple[int, int] = (8, 8)
    min_confidence: float = 0.08

    def __post_init__(self) -> None:
        if self.resize_height < 100:
            raise ValueError("resize_height must be >= 100")
        _require_odd_min(self.blur_ksize, "blur_ksize")
        _require_odd_min(self.dilate_kernel, "dilate_kernel")
        _require_odd_min(self.bright_open_kernel, "bright_open_kernel")
        if self.canny_low >= self.canny_high:
            raise ValueError("canny_low must be lower than canny_high")
        if not 0 < self.min_area_ratio < self.max_area_ratio <= 1:
            raise ValueError("area ratios must satisfy 0 < min < max <= 1")
        if self.dilate_iterations < 1:
            raise ValueError("dilate_iterations must be >= 1")
        if not self.approx_epsilon_ratios:
            raise ValueError("approx_epsilon_ratios cannot be empty")
        if any(ratio <= 0 for ratio in self.approx_epsilon_ratios):
            raise ValueError("approx_epsilon_ratios must contain positive values")
        if not 0 <= self.min_confidence <= 1:
            raise ValueError("min_confidence must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class EnhancementConfig:
    mode: OutputMode = "bw"
    use_clahe: bool = True
    clahe_clip_limit: float = 2.0
    clahe_tile_grid: tuple[int, int] = (8, 8)
    threshold_method: ThresholdMethod = "adaptive"
    adaptive_block_size: int = 31
    adaptive_c: float = 10.0
    denoise: bool = True
    min_ocr_width: int = 1000
    max_upscale: float = 3.0

    def __post_init__(self) -> None:
        if self.mode not in ("color", "gray", "bw"):
            raise ValueError("mode must be one of: color, gray, bw")
        if self.threshold_method not in ("adaptive", "otsu"):
            raise ValueError("threshold_method must be adaptive or otsu")
        _require_odd_min(self.adaptive_block_size, "adaptive_block_size")
        if self.adaptive_c < 0:
            raise ValueError("adaptive_c must be >= 0")
        if self.min_ocr_width < 0:
            raise ValueError("min_ocr_width must be >= 0")
        if self.max_upscale < 1:
            raise ValueError("max_upscale must be >= 1")


@dataclass(frozen=True, slots=True)
class ScanConfig:
    detection: DetectionConfig = field(default_factory=DetectionConfig)
    enhancement: EnhancementConfig = field(default_factory=EnhancementConfig)
    allow_full_image_fallback: bool = True
    debug: bool = False
