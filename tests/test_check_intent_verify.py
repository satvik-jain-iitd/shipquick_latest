"""Intent-verification gate (ADR-021): a dev PR must record `Intent verified by QA: <date>`."""
import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_intent_verify.py"


def run(body, *args):
    return subprocess.run(["python3", str(SCRIPT), *args], input=body, capture_output=True, text=True)


@pytest.mark.parametrize("body", [
    "## What\nFix.\n\nIntent verified by QA: 2026-11-19\n",
    "Intent verified by QA: 2026-11-20\n",
])
def test_a_pr_body_with_intent_verified_line_passes(body):
    r = run(body)
    assert r.returncode == 0 and "OK" in r.stdout, r.stdout


@pytest.mark.parametrize("body", [
    "## What\nFix.\n",                                  # no line at all
    "Intent verified by QA:\n",                         # empty
    "Intent verified by QA: yes\n",                     # no date
])
def test_a_pr_body_without_a_dated_intent_line_fails(body):
    r = run(body)
    assert r.returncode == 1 and "Intent" in r.stdout, r.stdout


def test_pr_body_mode_skips_a_body_with_no_linked_issue(tmp_path):
    f = tmp_path / "body.md"
    f.write_text("## What\nNo link.\n", encoding="utf-8")
    r = run("", "--pr-body-file", str(f))
    assert r.returncode == 0, r.stdout


STUB = """#!/usr/bin/env bash
case "$1 $2" in
  "auth status") [ -n "${STUB_NO_AUTH:-}" ] && { echo "You are not logged into any GitHub hosts. Run gh auth login" >&2; exit 1; }; exit 0 ;;
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


def story_issue(created):
    return {"labels": [{"name": "user-story"}], "body": "## Value\nNo actor line.\n", "createdAt": created}


@pytest.mark.parametrize("created,has_intent,rc", [
    ("2026-11-18T10:00:00Z", False, 0),   # before the rule: skipped
    ("2026-11-19T00:00:00Z", True, 0),    # on/after rule with intent line: passes
    ("2026-11-20T09:00:00Z", False, 1),   # on/after rule without intent line: fails
])
def test_a_story_created_before_the_rule_is_skipped(tmp_path, created, has_intent, rc):
    f = tmp_path / "body.md"
    body = "Closes #12\n" + ("Intent verified by QA: 2026-11-19\n" if has_intent else "")
    f.write_text(body, encoding="utf-8")
    r = subprocess.run(["python3", str(SCRIPT), "--pr-body-file", str(f)], capture_output=True, text=True, env=stub_env(tmp_path, story_issue(created)))
    assert r.returncode == rc, r.stdout


def test_check_local_skips_the_intent_check_when_gh_is_not_logged_in(tmp_path):
    repo = tmp_path / "repo"; repo.mkdir()
    git = lambda *a: subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)
    git("init", "-q", "-b", "dev"); git("config", "user.email", "t@example.com"); git("config", "user.name", "t")
    git("commit", "-q", "--allow-empty", "-m", "chore: base")
    git("update-ref", "refs/remotes/origin/dev", "HEAD")
    git("commit", "-q", "--allow-empty", "-m", "feat: x\n\nCloses #12")
    env = stub_env(tmp_path, story_issue("2026-11-20T09:00:00Z"), no_auth=True)
    r = subprocess.run(["bash", str(ROOT / "scripts" / "check_local.sh"), "intent-verify"], cwd=repo, capture_output=True, text=True, env=env)
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "skip intent-verify: gh is not logged in" in r.stdout
