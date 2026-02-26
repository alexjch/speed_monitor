"""Speed Monitor package.

Baseline implementation of the system described in ssd.md.
"""

from .config import CalibrationConfig, MonitorConfig
from .monitor import SpeedMonitor

__all__ = ["CalibrationConfig", "MonitorConfig", "SpeedMonitor"]
