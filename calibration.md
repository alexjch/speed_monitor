# Calibration procedure

To obtain the values needed for calibration, physically mark two horizontal reference lines in the scene (one near the camera and one farther away), then measure the real-world distance between marks and the corresponding pixel distance in a video frame.

Notes:
- Image coordinates use OpenCV convention: $y = 0$ is at the top of the frame and increases downward.
- Typically the "near" line will have a larger $y$ value than the "far" line (because it appears lower in the image).

## 1. Near line (near the camera)

On the near sidewalk/road edge, place two visible marks (left of center and right of center) on the same imaginary horizontal line. Measure and record the real-world distance between the marks in meters (e.g. with a tape measure).

## 2. Far line (farther from the camera)

Farther up the road (higher in the frame), place two visible marks (left and right of center) on the same imaginary horizontal line. Measure and record the real-world distance between the marks in meters.

## 3. Extract a frame where all 4 marks are visible

```bash
./helpers/getframe.py my_video.mp4 --output /tmp/frame.jpeg --number 1
```

(Frame numbering is 0-indexed: `--number 0` is the first frame.)

## 4. Compute Calibration Parameters

Calculate the transformation constants based on the reference frame to map image pixels to real-world meters.

- **a) `meters_per_pixel_near`** Calculate the horizontal scale at the **near** reference line.
$$meters\_per\_pixel_{near} = \frac{\text{Real-world distance (meters)}}{\text{Distance between marks (pixels)}}$$

- **b) `meters_per_pixel_far`** Calculate the horizontal scale at the **far** reference line.
$$meters\_per\_pixel_{far} = \frac{\text{Real-world distance (meters)}}{\text{Distance between marks (pixels)}}$$

- **c) `y_near`** The vertical pixel index ($y$-coordinate) of the near horizontal line. This represents the line closest to the bottom of the frame.

- **d) `y_far`** The vertical pixel index ($y$-coordinate) of the far horizontal line.

> **Note on Coordinate Convention:** Since the image origin $(0,0)$ is at the **upper-left corner**, `y_far` must be a lower numerical value than `y_near`.
