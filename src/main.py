from __future__ import annotations

import argparse
from pathlib import Path

from speed_monitor.config import MonitorConfig, load_config
from speed_monitor.monitor import SpeedMonitor


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    """Parse CLI arguments for the speed monitor."""
    parser = argparse.ArgumentParser(description="Speed Monitor (baseline)")
    parser.add_argument(
        "--video",
        default="0",
        help="Path to a video file, or a camera index (default: 0)",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Path to a JSON config file (optional)",
    )
    parser.add_argument(
        "--output",
        default="speeds.csv",
        help="CSV output path (default: speeds.csv)",
    )
    parser.add_argument(
        "--display",
        action="store_true",
        help="Show the video with overlays; press 'q' to quit.",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        help="Stop after N frames (useful for quick tests)",
    )
    parser.add_argument(
        "--speed-limit-mph",
        type=float,
        default=None,
        help="Optional alert threshold in mph.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the speed monitor CLI."""
    args = _parse_args(argv)

    config: MonitorConfig
    if args.config is not None:
        config = load_config(Path(args.config))
    else:
        config = MonitorConfig()

    if args.speed_limit_mph is not None:
        config = MonitorConfig(
            calibration=config.calibration,
            min_contour_area_px=config.min_contour_area_px,
            max_track_age_frames=config.max_track_age_frames,
            match_max_distance_px=config.match_max_distance_px,
            speed_smoothing_window=config.speed_smoothing_window,
            speed_limit_mph=float(args.speed_limit_mph),
        )

    # Accept camera index as a string like "0".
    video_source: str | int
    video_str = str(args.video)
    if video_str.isdigit():
        video_source = int(video_str)
    else:
        video_source = video_str

    SpeedMonitor(config=config).run(
        video_source=video_source,
        output_csv=str(args.output),
        display=bool(args.display),
        max_frames=args.max_frames,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())