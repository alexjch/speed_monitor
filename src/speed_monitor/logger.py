from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO


@dataclass(frozen=True)
class SpeedLogRow:
    """Single row of speed measurements for CSV output."""
    timestamp_iso: str
    frame_idx: int
    track_id: int
    x1: int
    y1: int
    x2: int
    y2: int
    speed_mph: float


class CsvSpeedLogger:
    """Write speed measurements to a CSV file."""
    def __init__(self, path: str | Path) -> None:
        """Initialize the logger with an output path."""
        self._path = Path(path)
        self._file: TextIO | None = None
        self._writer: csv.DictWriter[str] | None = None

    def __enter__(self) -> "CsvSpeedLogger":
        """Open the CSV file and write the header."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self._path.open("w", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(
            self._file,
            fieldnames=[
                "timestamp_iso",
                "frame_idx",
                "track_id",
                "x1",
                "y1",
                "x2",
                "y2",
                "speed_mph",
            ],
        )
        self._writer.writeheader()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        """Close the CSV file."""
        if self._file is not None:
            self._file.close()
        self._file = None
        self._writer = None

    def log(self, row: SpeedLogRow) -> None:
        """Write a single speed measurement row."""
        if self._writer is None:
            raise RuntimeError("CsvSpeedLogger must be used as a context manager")
        self._writer.writerow(
            {
                "timestamp_iso": row.timestamp_iso,
                "frame_idx": row.frame_idx,
                "track_id": row.track_id,
                "x1": row.x1,
                "y1": row.y1,
                "x2": row.x2,
                "y2": row.y2,
                "speed_mph": f"{row.speed_mph:.3f}",
            }
        )
