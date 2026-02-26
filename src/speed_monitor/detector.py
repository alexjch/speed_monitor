from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from .types import BBox


@dataclass
class DetectorResult:
    bboxes: list[BBox]
    foreground_mask: np.ndarray | None = None


class BackgroundSubtractorDetector:
    """Baseline vehicle detector using background subtraction.

    This works best with a fixed camera, which matches the SSD.

    Limitations:
    - Will detect any moving object (not just vehicles)
    - Sensitive to camera shake and lighting changes
    """

    def __init__(
        self,
        *,
        min_contour_area_px: int = 800,
        history: int = 400,
        var_threshold: float = 32.0,
        detect_shadows: bool = True,
    ) -> None:
        self._min_contour_area_px = int(min_contour_area_px)
        self._bg = cv2.createBackgroundSubtractorMOG2(
            history=int(history),
            varThreshold=float(var_threshold),
            detectShadows=bool(detect_shadows),
        )

        self._kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        self._kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))

    def detect(self, frame_bgr: np.ndarray) -> DetectorResult:
        fg = self._bg.apply(frame_bgr)

        # Drop shadow class (127) if enabled.
        _, fg = cv2.threshold(fg, 200, 255, cv2.THRESH_BINARY)

        fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, self._kernel_open, iterations=1)
        fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, self._kernel_close, iterations=2)

        contours, _hier = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        bboxes: list[BBox] = []
        for c in contours:
            area = cv2.contourArea(c)
            if area < self._min_contour_area_px:
                continue

            x, y, w, h = cv2.boundingRect(c)
            if w <= 0 or h <= 0:
                continue

            bboxes.append(BBox(x1=int(x), y1=int(y), x2=int(x + w), y2=int(y + h)))

        return DetectorResult(bboxes=bboxes, foreground_mask=fg)
