import pytest

from speed_monitor.config import CalibrationConfig
from speed_monitor.speed import feet_per_pixel_at_y, speed_mph_from_pixel_displacement


def test_speed_mph_from_pixel_displacement_constant_scale() -> None:
    """Compute mph from a constant feet-per-pixel scale."""
    cal = CalibrationConfig(fps=30.0, feet_per_pixel_near=0.1)

    # 10 px per frame -> 1.0 ft per frame -> 30 ft/s -> 20.4545 mph
    speed = speed_mph_from_pixel_displacement(
        pixel_distance=10.0,
        frames_delta=1,
        calibration=cal,
        y_for_scale=None,
    )
    assert abs(speed - (30.0 * 3600.0 / 5280.0)) < 1e-6


def test_feet_per_pixel_interpolates_by_y() -> None:
    """Ensure feet-per-pixel interpolation respects near/far values."""
    cal = CalibrationConfig(
        fps=30.0,
        feet_per_pixel_near=0.06,
        feet_per_pixel_far=0.02,
        y_near=600,
        y_far=100,
    )

    assert feet_per_pixel_at_y(cal, 600) == pytest.approx(0.06)
    assert feet_per_pixel_at_y(cal, 100) == pytest.approx(0.02)

    mid = feet_per_pixel_at_y(cal, 350)
    assert 0.02 < mid < 0.06
