from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CalibrationConfig:
    """Camera+scene calibration values used for speed estimation.

        This baseline implementation uses a feet-per-pixel scale, optionally
    interpolated by the detection's y-coordinate to roughly compensate for
    perspective.

        - If only `feet_per_pixel_near` is provided, that constant scale is used.
        - If `feet_per_pixel_far`, `y_near`, and `y_far` are also provided, the
      scale is linearly interpolated between (y_near, near) and (y_far, far).
    """

    fps: float = 30.0

    feet_per_pixel_near: float = 0.05

    feet_per_pixel_far: float | None = None
    y_near: int | None = None
    y_far: int | None = None


@dataclass(frozen=True)
class MonitorConfig:
    """Top-level configuration for the speed monitor."""

    calibration: CalibrationConfig = CalibrationConfig()

    min_contour_area_px: int = 800
    max_track_age_frames: int = 10
    match_max_distance_px: float = 80.0

    speed_smoothing_window: int = 2

    speed_limit_mph: float | None = None


def _coerce_calibration(data: dict[str, Any]) -> CalibrationConfig:
    """Normalize calibration values read from JSON."""
    return CalibrationConfig(
        fps=float(data.get("fps", 30.0)),
        feet_per_pixel_near=float(data.get("feet_per_pixel_near", 0.05)),
        feet_per_pixel_far=(
            None
            if data.get("feet_per_pixel_far") is None
            else float(data["feet_per_pixel_far"])
        ),
        y_near=(None if data.get("y_near") is None else int(data["y_near"])),
        y_far=(None if data.get("y_far") is None else int(data["y_far"])),
    )


def load_config(path: str | Path) -> MonitorConfig:
    """Load monitor config from a JSON file."""

    file_path = Path(path)
    payload = json.loads(file_path.read_text(encoding="utf-8"))

    calibration_data = payload.get("calibration", {})
    calibration = _coerce_calibration(calibration_data)

    return MonitorConfig(
        calibration=calibration,
        min_contour_area_px=int(payload.get("min_contour_area_px", 800)),
        max_track_age_frames=int(payload.get("max_track_age_frames", 10)),
        match_max_distance_px=float(payload.get("match_max_distance_px", 80.0)),
        speed_smoothing_window=int(payload.get("speed_smoothing_window", 2)),
        speed_limit_mph=(
            None
            if payload.get("speed_limit_mph") is None
            else float(payload["speed_limit_mph"])
        ),
    )
