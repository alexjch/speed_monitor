from speed_monitor.tracker import CentroidTracker
from speed_monitor.types import BBox


def test_tracker_keeps_id_for_small_motion():
    tr = CentroidTracker(max_age_frames=5, match_max_distance_px=50.0)

    tracks_f1 = tr.update(detections=[BBox(0, 0, 10, 10)], frame_idx=1)
    assert len(tracks_f1) == 1
    tid = tracks_f1[0].track_id

    tracks_f2 = tr.update(detections=[BBox(5, 0, 15, 10)], frame_idx=2)
    assert len(tracks_f2) == 1
    assert tracks_f2[0].track_id == tid


def test_tracker_creates_new_id_when_far_apart():
    tr = CentroidTracker(max_age_frames=5, match_max_distance_px=10.0)

    tracks_f1 = tr.update(detections=[BBox(0, 0, 10, 10)], frame_idx=1)
    tid1 = tracks_f1[0].track_id

    tracks_f2 = tr.update(detections=[BBox(100, 0, 110, 10)], frame_idx=2)
    ids = sorted(t.track_id for t in tracks_f2)

    assert tid1 in ids
    assert len(ids) == 2
