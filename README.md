# Speed Monitor

Baseline implementation of the system described in [ssd.md](ssd.md): detect moving vehicles from a fixed camera feed, track them across frames, estimate speed from pixel displacement + calibration, and log results.

## Install

This repo expects a local virtualenv at `.venv`.

```
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run

Camera (index 0) to CSV:

```
python src/main.py --output speeds.csv
```

Video file, with display overlay:

```
python src/main.py --video path/to/video.mp4 --display --output speeds.csv
```

With config + speed limit alerts:

```
python src/main.py --config config.example.json --speed-limit-mph 35 --display
```

Press `q` to quit when `--display` is enabled.

## Offline downsampling helper

Use the helper to downsample a video file before running the monitor.

Basic usage:

```
python3 helpers/downsample.py input.mp4 --output downsampled.mp4 --scale 0.25
```

With explicit codec and fps:

```
python3 helpers/downsample.py input.mp4 --output downsampled.mp4 --scale 0.25 --codec avc1 --fps 30
```

Notes:
- `input` is positional and must come before options.
- `--scale` is a float in `(0, 1]`.
- If `--fps` is omitted (or `0`), input FPS is reused (fallback: `30.0`).

## Configuration

Configuration is JSON. See [config.example.json](config.example.json).

For how to measure calibration values in a real scene, see [calibration.md](calibration.md).

```json
{
    "calibration": {
        "fps": 30.0,
        "feet_per_pixel_near": 0.05,
        "feet_per_pixel_far": 0.02,
        "y_near": 700,
        "y_far": 100
    },
    "min_contour_area_px": 2000,
    "max_track_age_frames": 10,
    "match_max_distance_px": 80.0,
    "speed_smoothing_window": 2,
    "speed_limit_mph": 35.0
}
```


## Output

CSV rows contain timestamp, frame index, track id, bounding box, and estimated speed (mph).

## Testing

```
make test

# or, without make:
.venv/bin/python -m pytest -q
```

## Notes / limitations

The baseline detector uses OpenCV background subtraction, so it will detect any motion (not strictly “vehicles”). For real deployments you’ll likely swap in a dedicated object detector + a stronger tracker, and calibrate with ground truth.

## TODO
- Use proper configuration and calibration