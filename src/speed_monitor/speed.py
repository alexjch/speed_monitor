from __future__ import annotations

import math

from .config import CalibrationConfig


def meters_per_pixel_at_y(calibration: CalibrationConfig, y: float | None) -> float:
    """Return meters-per-pixel scale for a given y coordinate.

    If a far scale and y-range is configured, linearly interpolate.
    """

    if (
        calibration.meters_per_pixel_far is None
        or calibration.y_near is None
        or calibration.y_far is None
        or y is None
    ):
        return calibration.meters_per_pixel_near

    y0 = float(calibration.y_near)
    y1 = float(calibration.y_far)

    if math.isclose(y0, y1):
        return calibration.meters_per_pixel_near

    t = (float(y) - y0) / (y1 - y0)
    t = max(0.0, min(1.0, t))

    near = calibration.meters_per_pixel_near
    far = calibration.meters_per_pixel_far
    return near + t * (far - near)


def speed_kmh_from_pixel_displacement(
    *,
    pixel_distance: float,
    frames_delta: int,
    calibration: CalibrationConfig,
    y_for_scale: float | None = None,
) -> float:
    """Compute speed in km/h from a pixel displacement observed over N frames."""

    if frames_delta <= 0:
        raise ValueError("frames_delta must be > 0")

    meters_per_pixel = meters_per_pixel_at_y(calibration, y_for_scale)
    meters = float(pixel_distance) * meters_per_pixel
    seconds = frames_delta / float(calibration.fps)

    if seconds <= 0:
        return 0.0

    mps = meters / seconds
    return mps * 3.6
