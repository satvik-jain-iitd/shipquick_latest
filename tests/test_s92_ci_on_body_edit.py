"""Story #92: CI runs again when a PR body is edited, so the team-block, tdd and uat checks see the new body."""
import re
import subprocess
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
ADOPT = ROOT / "scripts" / "adopt.sh"
PONYTAIL_ON = ROOT / "tests/fixtures/adopt/settings-ponytail-on.json"
TYPES = "types: [opened, synchronize, reopened, edited]"


def pull_request_block(text):
    """The indented lines under the top-level `  pull_request:` trigger."""
    m = re.search(r"^  pull_request:\n((?:    .*\n)*)", text, re.M)
    assert m, "no pull_request trigger found"
    return m.group(1)


def test_s92_ci_pull_request_trigger_lists_edited():
    block = pull_request_block((ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8"))
    assert "edited" in block and TYPES in block, block


@pytest.fixture
def child(tmp_path):
    c = tmp_path / "my-child"
    (c / ".github" / "workflows").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "dev", str(c)], check=True)
    (c / ".github" / "workflows" / "ci.yml").write_text('name: Child CI\non:\n  push:\n', encoding="utf-8")
    return c


def test_s92_the_adopted_checks_caller_also_runs_on_body_edit(child):
    e = dict(os.environ)
    e["SHIPQUICK_CLAUDE_SETTINGS"] = str(PONYTAIL_ON)
    e.pop("CI", None)
    r = subprocess.run(["bash", str(ADOPT), str(child)], capture_output=True, text=True, env=e)
    assert r.returncode == 0, r.stderr
    call = (child / ".github" / "workflows" / "shipquick-call.yml").read_text(encoding="utf-8")
    assert TYPES in pull_request_block(call), call
