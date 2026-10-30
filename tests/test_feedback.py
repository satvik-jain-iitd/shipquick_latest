"""Story #111: a one-line feedback inbox from a child project into ShipQuick (scripts/feedback.sh).
Given a child repo running feedback.sh "<line>" --why "<why>", an issue opens in satvik-jain-iitd/shipquick_latest
with label feedback, the project name, the line and the why. No gh login for the build account: it prints the
text to paste and exits 1, nothing lost."""
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "feedback.sh"
REPO = "satvik-jain-iitd/shipquick_latest"

STUB_OK = """#!/usr/bin/env bash
echo "$*" >> "$STUB_DIR/calls.log"
case "$1" in
  auth) [ "$2" = token ] && { echo "tok-$4"; exit 0; } ;;
  issue) [ "$2" = create ] && { printf '%s\\0' "$@" >> "$STUB_DIR/issue.log"; exit 0; } ;;
esac
exit 9
"""

STUB_NO_LOGIN = """#!/usr/bin/env bash
echo "$*" >> "$STUB_DIR/calls.log"
case "$1" in
  auth) [ "$2" = token ] && exit 1 ;;
esac
exit 9
"""


@pytest.fixture
def child(tmp_path):
    repo = tmp_path / "job-search"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    return repo


def stub(tmp_path, script):
    d = tmp_path / "stub"
    d.mkdir()
    (d / "gh").write_text(script, encoding="utf-8")
    (d / "gh").chmod(0o755)
    return d


def run(child, tmp_path, script, *args):
    d = stub(tmp_path, script)
    env = {**os.environ, "PATH": f"{d}:{os.environ['PATH']}", "STUB_DIR": str(d)}
    r = subprocess.run(["bash", str(SCRIPT), *args], cwd=child, capture_output=True, text=True, env=env)
    r.calls = (d / "calls.log").read_text(encoding="utf-8") if (d / "calls.log").exists() else ""
    r.issue = (d / "issue.log").read_text(encoding="utf-8") if (d / "issue.log").exists() else ""
    return r


def test_s111_opens_a_labelled_issue_with_the_project_name_the_line_and_the_why(child):
    r = run(child, child.parent, STUB_OK, "scripts/model_calls.sh is slow on a big repo", "--why", "a kit user hit it on job-search")
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert f"-R\x00{REPO}" in r.issue
    assert "--label\x00feedback" in r.issue
    assert "job-search" in r.issue
    assert "scripts/model_calls.sh is slow on a big repo" in r.issue
    assert "a kit user hit it on job-search" in r.issue


def test_s111_the_project_name_comes_from_the_git_remote_when_there_is_one(child):
    subprocess.run(["git", "remote", "add", "origin", "https://github.com/satvik-jain-iitd/LinkRight.git"], cwd=child, check=True)
    r = run(child, child.parent, STUB_OK, "one line", "--why", "because")
    assert "LinkRight" in r.issue and "job-search" not in r.issue


def test_s111_no_gh_login_prints_the_text_to_paste_and_exits_1_nothing_lost(child):
    r = run(child, child.parent, STUB_NO_LOGIN, "one line", "--why", "because")
    assert r.returncode == 1
    assert "one line" in r.stderr and "because" in r.stderr
    assert r.issue == "", "nothing is opened when there is no login"


def test_s111_missing_why_is_a_usage_error(child):
    r = run(child, child.parent, STUB_OK, "one line")
    assert r.returncode == 2
    assert "usage" in r.stderr.lower()
