"""AC traceability (M5d)."""
import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_ac_trace.py"


def run(body, *args):
    return subprocess.run(["python3", str(SCRIPT), *args], input=body, capture_output=True, text=True)


def test_a_story_with_ac_ids_and_tests_passes():
    r = run("## Scenarios\nAC-1: foo\nAC-2: bar\nTests: AC-1 -> tests/test_x.py::test_foo\n")
    assert r.returncode == 0 and "OK" in r.stdout, r.stdout


def test_a_story_without_ac_ids_fails():
    r = run("## Scenarios\nfoo\nTests: tests/test_x.py\n")
    assert r.returncode == 1 and "acceptance-criteria IDs" in r.stdout, r.stdout


def test_a_story_without_tests_mapping_fails():
    r = run("## Scenarios\nAC-1: foo\n")
    assert r.returncode == 1 and "Tests:" in r.stdout, r.stdout


def test_pr_body_mode_skips_no_link(tmp_path):
    f = tmp_path / "body.md"; f.write_text("## What\nNo link.\n", encoding="utf-8")
    r = run("", "--pr-body-file", str(f))
    assert r.returncode == 0, r.stdout


STUB = """#!/usr/bin/env bash
case "$1 $2" in
  "auth status") [ -n "${STUB_NO_AUTH:-}" ] && { echo "You are not logged into any GitHub hosts." >&2; exit 1; }; exit 0 ;;
  "issue view") cat "$STUB_DIR/issue.json"; exit 0 ;;
esac
exit 9
"""


def stub_env(tmp_path, issue=None, no_auth=False):
    stub = tmp_path / "stub"; stub.mkdir()
    (stub / "gh").write_text(STUB, encoding="utf-8"); (stub / "gh").chmod(0o755)
    if issue is not None:
        (stub / "issue.json").write_text(json.dumps(issue), encoding="utf-8")
    return {**os.environ, "PATH": f"{stub}:{os.environ['PATH']}", "STUB_DIR": str(stub), "STUB_NO_AUTH": "1" if no_auth else ""}


def story_issue(created, body):
    return {"labels": [{"name": "user-story"}], "body": body, "createdAt": created}


def test_old_story_skipped(tmp_path):
    f = tmp_path / "body.md"; f.write_text("Closes #12\n", encoding="utf-8")
    issue = story_issue("2026-11-18T10:00:00Z", "## Value\nNo AC.\n")
    r = subprocess.run(["python3", str(SCRIPT), "--pr-body-file", str(f)], capture_output=True, text=True, env=stub_env(tmp_path, issue))
    assert r.returncode == 0, r.stdout
    assert "skip #12" in r.stdout


def test_new_story_without_ac_fails(tmp_path):
    f = tmp_path / "body.md"; f.write_text("Closes #12\n", encoding="utf-8")
    issue = story_issue("2026-11-20T09:00:00Z", "## Value\nNo AC IDs.\n")
    r = subprocess.run(["python3", str(SCRIPT), "--pr-body-file", str(f)], capture_output=True, text=True, env=stub_env(tmp_path, issue))
    assert r.returncode == 1, r.stdout


def test_check_local_skips_when_gh_not_logged_in(tmp_path):
    repo = tmp_path / "repo"; repo.mkdir()
    git = lambda *a: subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)
    git("init", "-q", "-b", "dev"); git("config", "user.email", "t@example.com"); git("config", "user.name", "t")
    git("commit", "-q", "--allow-empty", "-m", "chore: base")
    git("update-ref", "refs/remotes/origin/dev", "HEAD")
    git("commit", "-q", "--allow-empty", "-m", "feat: x\n\nCloses #12")
    issue = story_issue("2026-11-20T09:00:00Z", "## Value\nNo AC.\n")
    env = stub_env(tmp_path, issue, no_auth=True)
    r = subprocess.run(["bash", str(ROOT / "scripts" / "check_local.sh"), "ac-trace"], cwd=repo, capture_output=True, text=True, env=env)
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "skip ac-trace: gh is not logged in" in r.stdout
