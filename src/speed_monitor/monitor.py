from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

import cv2
import numpy as np

from .config import MonitorConfig
from .detector import BackgroundSubtractorDetector
from .logger import CsvSpeedLogger, SpeedLogRow
from .speed import speed_kmh_from_pixel_displacement
from .tracker import CentroidTracker, Track


@dataclass(frozen=True)
class SpeedAlert:
    timestamp_iso: str
    frame_idx: int
    track_id: int
    speed_kmh: float
    speed_limit_kmh: float


class SpeedMonitor:
    def __init__(self, *, config: MonitorConfig) -> None:
        self._config = config

        self._detector = BackgroundSubtractorDetector(
            min_contour_area_px=config.min_contour_area_px,
        )
        self._tracker = CentroidTracker(
            max_age_frames=config.max_track_age_frames,
            match_max_distance_px=config.match_max_distance_px,
        )

    def _estimate_track_speed_kmh(self, tr: Track) -> float | None:
        window = max(2, int(self._config.speed_smoothing_window))
        if len(tr.history) < window:
            return None

        f0, x0, y0 = tr.history[-window]
        f1, x1, y1 = tr.history[-1]
        frames_delta = int(f1 - f0)
        if frames_delta <= 0:
            return None

        pixel_distance = float(((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5)
        return speed_kmh_from_pixel_displacement(
            pixel_distance=pixel_distance,
            frames_delta=frames_delta,
            calibration=self._config.calibration,
            y_for_scale=float(y1),
        )

    def run(
        self,
        *,
        video_source: str | int,
        output_csv: str,
        display: bool = False,
        max_frames: int | None = None,
    ) -> None:
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            raise RuntimeError(f"Could not open video source: {video_source}")

        frame_idx = 0
        with CsvSpeedLogger(output_csv) as logger:
            while True:
                ok, frame = cap.read()
                if not ok or frame is None:
                    break

                frame_idx += 1
                if max_frames is not None and frame_idx > max_frames:
                    break

                det = self._detector.detect(frame)
                tracks = self._tracker.update(detections=det.bboxes, frame_idx=frame_idx)

                timestamp_iso = dt.datetime.now(dt.timezone.utc).isoformat()

                for tr in tracks:
                    speed_kmh = self._estimate_track_speed_kmh(tr)
                    if speed_kmh is None:
                        continue

                    logger.log(
                        SpeedLogRow(
                            timestamp_iso=timestamp_iso,
                            frame_idx=frame_idx,
                            track_id=tr.track_id,
                            x1=tr.bbox.x1,
                            y1=tr.bbox.y1,
                            x2=tr.bbox.x2,
                            y2=tr.bbox.y2,
                            speed_kmh=float(speed_kmh),
                        )
                    )

                    if self._config.speed_limit_kmh is not None and speed_kmh > self._config.speed_limit_kmh:
                        print(
                            f"ALERT track={tr.track_id} speed={speed_kmh:.1f}km/h "
                            f"limit={self._config.speed_limit_kmh:.1f}km/h frame={frame_idx}"
                        )

                if display:
                    overlay = frame.copy()
                    self._draw_overlay(overlay, tracks)
                    if det.foreground_mask is not None:
                        mask_bgr = cv2.cvtColor(det.foreground_mask, cv2.COLOR_GRAY2BGR)
                        stacked = np.hstack([overlay, mask_bgr])
                    else:
                        stacked = overlay

                    cv2.imshow("speed_monitor", stacked)
                    # 1ms wait keeps UI responsive.
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break

        cap.release()
        if display:
            cv2.destroyAllWindows()

    def _draw_overlay(self, frame: np.ndarray, tracks: list[Track]) -> None:
        for tr in tracks:
            x1, y1, x2, y2 = tr.bbox.x1, tr.bbox.y1, tr.bbox.x2, tr.bbox.y2
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            speed_kmh = self._estimate_track_speed_kmh(tr)
            label = f"id={tr.track_id}"
            if speed_kmh is not None:
                label += f" {speed_kmh:.1f} km/h"

            cv2.putText(
                frame,
                label,
                (x1, max(0, y1 - 6)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
                cv2.LINE_AA,
            )
