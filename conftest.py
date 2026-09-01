import sys
from pathlib import Path

BACKEND_DIR = str(Path(__file__).resolve().parent / "backend")
sys.path.insert(0, BACKEND_DIR)