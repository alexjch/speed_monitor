from __future__ import annotations

from dataclasses import dataclass, field

from .types import BBox


def _euclidean(a: tuple[float, float], b: tuple[float, float]) -> float:
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return (dx * dx + dy * dy) ** 0.5


@dataclass
class Track:
    """
    A class that represents a tracked object across multiple frames.

    Attributes:
        track_id (int): Unique identifier for this track.
        bbox (BBox): Current bounding box of the tracked object.
        last_seen_frame (int): Frame index where the object was last detected.
        history (list[tuple[int, float, float]]): List of (frame_idx, center_x, center_y) tuples
            representing the object's position history across frames.

    Methods:
        update: Updates the track with a new bounding box and frame index.
        cx: Property that returns the current center x-coordinate of the bounding box.
        cy: Property that returns the current center y-coordinate of the bounding box.
    """
    track_id: int
    bbox: BBox
    last_seen_frame: int
    history: list[tuple[int, float, float]] = field(default_factory=list)

    def update(self, *, bbox: BBox, frame_idx: int) -> None:
        self.bbox = bbox
        self.last_seen_frame = frame_idx
        self.history.append((frame_idx, bbox.cx, bbox.cy))

    @property
    def cx(self) -> float:
        return self.bbox.cx

    @property
    def cy(self) -> float:
        return self.bbox.cy


class CentroidTracker:
    """
    A centroid-based tracker for matching detections across frames.

    Uses centroid distance to greedily match detections to existing tracks.
    Tracks that are not updated for a configurable number of frames are removed.

    Attributes:
        _max_age_frames: Maximum number of frames a track can exist without updates.
        _match_max_distance_px: Maximum centroid distance in pixels for a valid match.
        _next_id: Counter for generating unique track IDs.
        _tracks: Dictionary mapping track IDs to Track objects.

    Methods:
        update: Updates tracks with new detections and returns all active tracks.
    """

    def __init__(
        self,
        *,
        max_age_frames: int = 10,
        match_max_distance_px: float = 80.0,
    ) -> None:
        self._max_age_frames = int(max_age_frames)
        self._match_max_distance_px = float(match_max_distance_px)

        self._next_id = 1
        self._tracks: dict[int, Track] = {}

    def update(self, *, detections: list[BBox], frame_idx: int) -> list[Track]:
        # Drop stale tracks.
        stale_ids = [
            tid
            for tid, tr in self._tracks.items()
            if (frame_idx - tr.last_seen_frame) > self._max_age_frames
        ]
        for tid in stale_ids:
            self._tracks.pop(tid, None)

        unmatched_dets = set(range(len(detections)))
        unmatched_tracks = set(self._tracks.keys())

        # Greedy matching: for each track, find nearest detection.
        matches: list[tuple[int, int, float]] = []  # (track_id, det_idx, dist)
        for tid, tr in self._tracks.items():
            best_det = None
            best_dist = None
            for di, det in enumerate(detections):
                if di not in unmatched_dets:
                    continue
                dist = _euclidean((tr.cx, tr.cy), (det.cx, det.cy))
                if best_dist is None or dist < best_dist:
                    best_dist = dist
                    best_det = di
            if best_det is not None and best_dist is not None:
                matches.append((tid, best_det, best_dist))

        # Apply matches in order of increasing distance.
        matches.sort(key=lambda t: t[2])
        for tid, di, dist in matches:
            if tid not in unmatched_tracks or di not in unmatched_dets:
                continue
            if dist > self._match_max_distance_px:
                continue

            self._tracks[tid].update(bbox=detections[di], frame_idx=frame_idx)
            unmatched_tracks.remove(tid)
            unmatched_dets.remove(di)

        # Create new tracks for unmatched detections.
        for di in sorted(unmatched_dets):
            det = detections[di]
            tid = self._next_id
            self._next_id += 1

            tr = Track(track_id=tid, bbox=det, last_seen_frame=frame_idx)
            tr.history.append((frame_idx, det.cx, det.cy))
            self._tracks[tid] = tr

        return list(self._tracks.values())
