"""Coverage ratchet (M5a)."""
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_coverage.py"


def run(*args, cwd=None):
    return subprocess.run(["python3", str(SCRIPT), *args], capture_output=True, text=True, cwd=cwd or ROOT)


def test_help_runs():
    r = run("--help")
    assert r.returncode == 0




def test_baseline_file_is_valid_json():
    bp = ROOT / ".shipquick" / "coverage-baseline.json"
    if bp.exists():
        json.loads(bp.read_text())
