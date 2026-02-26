import sys
from pathlib import Path

# Ensure imports work with the common "src/" layout when running pytest from the repo root.
SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))
