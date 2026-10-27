"""S0.5: linked story issues close by hand when a PR merges into a non-default branch."""
import json
import os
import stat
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "close_linked_issues.py"

# The fake gh answers from a JSON fixture and logs every call to CALLS.
FAKE_GH = """#!/usr/bin/env python3
import json, os, sys
fx = json.load(open(os.environ["FAKE_GH_FIXTURE"]))
open(os.environ["FAKE_GH_CALLS"], "a").write(" ".join(sys.argv[1:]) + "\\n")
a = sys.argv[1:]
if a[:2] == ["repo", "view"]:
    # real gh ignores GH_REPO here and reads the folder's git remotes: answer with a wrong repo (issue #88)
    print(json.dumps({"defaultBranchRef": {"name": "master-of-the-wrong-repo"}}))
elif a[:2] == ["api", "repos/{owner}/{repo}"]:
    print(json.dumps({"default_branch": fx["default"]}))
elif a[:2] == ["pr", "view"]:
    print(json.dumps(fx["pr"]))
elif a[:2] == ["issue", "view"]:
    print(json.dumps(fx["issues"][a[2]]))
"""


def run(tmp_path, fixture, *args):
    gh = tmp_path / "gh"
    gh.write_text(FAKE_GH)
    gh.chmod(gh.stat().st_mode | stat.S_IEXEC)
    fx = tmp_path / "fx.json"
    fx.write_text(json.dumps(fixture))
    calls = tmp_path / "calls.txt"
    calls.write_text("")
    env = dict(os.environ, PATH=f"{tmp_path}:{os.environ['PATH']}",
               FAKE_GH_FIXTURE=str(fx), FAKE_GH_CALLS=str(calls))
    proc = subprocess.run([sys.executable, str(SCRIPT), "7", *args],
                          capture_output=True, text=True, env=env)
    return proc, calls.read_text()


def issue(state="OPEN", labels=()):
    return {"state": state, "labels": [{"name": n} for n in labels]}


MERGED_TO_DEV = {
    "default": "main",
    "pr": {"number": 7, "state": "MERGED", "baseRefName": "dev",
           "body": "Closes #39\nCloses #40, closes #41\nFixes #50\nSee #99"},
    "issues": {"39": issue(), "40": issue(labels=["epic"]),
               "41": issue("CLOSED"), "50": issue(labels=["story"])},
}


def test_dry_run_lists_open_stories_and_closes_nothing(tmp_path):
    proc, calls = run(tmp_path, MERGED_TO_DEV)
    assert proc.returncode == 0, proc.stderr
    assert "#39" in proc.stdout and "#50" in proc.stdout
    assert "#40" in proc.stdout and "epic" in proc.stdout  # listed as skipped
    assert "#99" not in proc.stdout
    assert "issue close" not in calls


def test_yes_closes_each_open_story_with_comment(tmp_path):
    proc, calls = run(tmp_path, MERGED_TO_DEV, "--yes")
    assert proc.returncode == 0, proc.stderr
    closed = [c for c in calls.splitlines() if c.startswith("issue close")]
    assert len(closed) == 2
    assert closed[0].startswith("issue close 39 --comment Done in PR #7 (merged to dev)")
    assert closed[1].startswith("issue close 50 ")
    assert not any(c.startswith("issue close 40") or c.startswith("issue close 41") for c in calls.splitlines())


def test_open_pr_closes_nothing(tmp_path):
    fx = dict(MERGED_TO_DEV, pr=dict(MERGED_TO_DEV["pr"], state="OPEN"))
    proc, calls = run(tmp_path, fx, "--yes")
    assert proc.returncode == 1
    assert "issue close" not in calls


def test_closed_unmerged_pr_closes_nothing(tmp_path):
    fx = dict(MERGED_TO_DEV, pr=dict(MERGED_TO_DEV["pr"], state="CLOSED"))
    proc, calls = run(tmp_path, fx, "--yes")
    assert proc.returncode == 1
    assert "issue close" not in calls


def test_merge_into_default_branch_is_left_to_github(tmp_path):
    fx = dict(MERGED_TO_DEV, pr=dict(MERGED_TO_DEV["pr"], baseRefName="main"))
    proc, calls = run(tmp_path, fx, "--yes")
    assert proc.returncode == 0
    assert "issue close" not in calls
    assert "GitHub" in proc.stdout
