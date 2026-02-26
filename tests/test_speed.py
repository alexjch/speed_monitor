import pytest

from speed_monitor.config import CalibrationConfig
from speed_monitor.speed import meters_per_pixel_at_y, speed_kmh_from_pixel_displacement


def test_speed_kmh_from_pixel_displacement_constant_scale():
    cal = CalibrationConfig(fps=30.0, meters_per_pixel_near=0.1)

    # 10 px per frame -> 1.0 m per frame -> 30 m/s -> 108 km/h
    speed = speed_kmh_from_pixel_displacement(
        pixel_distance=10.0,
        frames_delta=1,
        calibration=cal,
        y_for_scale=None,
    )
    assert abs(speed - 108.0) < 1e-6


def test_meters_per_pixel_interpolates_by_y():
    cal = CalibrationConfig(
        fps=30.0,
        meters_per_pixel_near=0.06,
        meters_per_pixel_far=0.02,
        y_near=600,
        y_far=100,
    )

    assert meters_per_pixel_at_y(cal, 600) == pytest.approx(0.06)
    assert meters_per_pixel_at_y(cal, 100) == pytest.approx(0.02)

    mid = meters_per_pixel_at_y(cal, 350)
    assert 0.02 < mid < 0.06
