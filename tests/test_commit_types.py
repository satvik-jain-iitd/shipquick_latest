"""The `release:` commit type: CI, the local check, the commit-msg hook and the guidelines agree."""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def hook(subject, tmp_path):
    f = tmp_path / "msg"
    f.write_text(subject + "\n")
    return subprocess.run([sys.executable, str(ROOT / "scripts" / "check_commit_msg.py"), str(f)], capture_output=True, text=True).returncode


@pytest.mark.parametrize("subject,code", [("release: v0.7.0 notes", 0), ("release(notes): v0.7.0", 0), ("foo: v0.7.0", 1)])
def test_commit_msg_hook(subject, code, tmp_path):
    assert hook(subject, tmp_path) == code


def test_ci_and_local_check_and_guidelines_list_release():
    assert "|build|release)" in (ROOT / ".github" / "workflows" / "ci.yml").read_text()
    assert "|build|release)" in (ROOT / "scripts" / "check_local.sh").read_text()
    assert "| `release` |" in (ROOT / "COMMIT_GUIDELINES.md").read_text()
