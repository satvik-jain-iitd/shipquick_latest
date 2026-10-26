"""S0.16: the coded merge gate (story #67). A stub `gh` on PATH: no network, no token, nothing is ever merged."""
import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "scripts" / "review_merge.sh"
MODE = ROOT / "scripts" / "mode.sh"
REVIEWER = "satvik-jain-iitd"
STUB = """#!/usr/bin/env bash
echo "$*" >> "$STUB_DIR/calls.log"
case "$1" in
  auth) [ "$2" = token ] && { echo "tok-$4"; exit 0; } ;;
  repo) echo "o/r"; exit 0 ;;
  pr) case "$2" in
        view) cat "$STUB_DIR/pr.json"; exit 0 ;;
        merge) echo "GH_TOKEN=$GH_TOKEN $*" >> "$STUB_DIR/merge.log"; exit 0 ;;
      esac ;;
  api) cat "$STUB_DIR/threads.json"; exit 0 ;;
esac
exit 9
"""


def good():
    return {
        "state": "OPEN", "isDraft": False, "mergeable": "MERGEABLE", "headRefOid": "abc123", "body": "## What\nSomething.\n\nCloses #67\n",
        "reviews": [{"author": {"login": REVIEWER}, "state": "APPROVED", "commit": {"oid": "abc123"}}],
        "statusCheckRollup": [{"name": "test", "status": "COMPLETED", "conclusion": "SUCCESS"}, {"name": "gate", "status": "COMPLETED", "conclusion": "SUCCESS"}],
    }


def threads(*resolved):
    return {"data": {"repository": {"pullRequest": {"reviewThreads": {"nodes": [{"isResolved": r} for r in resolved]}}}}}


@pytest.fixture
def env(tmp_path):
    repo, stub = tmp_path / "repo", tmp_path / "stub"
    repo.mkdir(); stub.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "dev", str(repo)], check=True)
    (stub / "gh").write_text(STUB, encoding="utf-8"); (stub / "gh").chmod(0o755)
    e = {**os.environ, "PATH": f"{stub}:{os.environ['PATH']}", "STUB_DIR": str(stub), "GH_TOKEN": "not-used"}

    def go(pr=None, th=None, mode="auto", args=("12",)):
        (stub / "merge.log").unlink(missing_ok=True)   # one call per scenario: a test may call go() twice
        (stub / "pr.json").write_text(json.dumps(pr or good()), encoding="utf-8")
        (stub / "threads.json").write_text(json.dumps(th or threads(True, True)), encoding="utf-8")
        if mode:
            subprocess.run(["bash", str(MODE), "set", mode], cwd=repo, check=True, env=e)
        r = subprocess.run(["bash", str(GATE), *args], cwd=repo, capture_output=True, text=True, env=e)
        merged = (stub / "merge.log").read_text(encoding="utf-8") if (stub / "merge.log").exists() else ""
        return r, merged

    return go


def refused(result, merged, rule):
    assert result.returncode == 1, (result.stdout, result.stderr)
    assert result.stderr.startswith("refused: ") and rule in result.stderr, result.stderr
    assert merged == "", "the gate must not merge when it refuses"


def test_s16_semi_mode_refuses(env):
    refused(*env(mode="semi"), "mode is semi")


def test_s16_manual_mode_refuses(env):
    refused(*env(mode="manual"), "mode is manual")


def test_s16_an_unset_mode_refuses(env):
    refused(*env(mode=None), "mode is not set")


def test_s16_a_draft_or_closed_pull_request_refuses(env):
    pr = good(); pr["isDraft"] = True
    refused(*env(pr=pr), "not open")
    pr = good(); pr["state"] = "MERGED"
    refused(*env(pr=pr), "not open")


def test_s16_an_approval_by_someone_else_is_not_enough(env):
    pr = good(); pr["reviews"][0]["author"]["login"] = "klickbae8yt-star"
    refused(*env(pr=pr), f"not approved by {REVIEWER}")


def test_s16_an_approval_of_an_older_commit_is_not_enough(env):
    pr = good(); pr["reviews"][0]["commit"]["oid"] = "old000"
    refused(*env(pr=pr), f"not approved by {REVIEWER}")


def test_s16_a_later_request_for_changes_cancels_the_approval(env):
    pr = good(); pr["reviews"].append({"author": {"login": REVIEWER}, "state": "CHANGES_REQUESTED", "commit": {"oid": "abc123"}})
    refused(*env(pr=pr), f"not approved by {REVIEWER}")


def test_s16_one_unresolved_thread_refuses(env):
    refused(*env(th=threads(True, False, True)), "unresolved review threads")


def test_s16_a_failing_or_pending_check_refuses_and_names_it(env):
    pr = good(); pr["statusCheckRollup"][1] = {"name": "gate", "status": "COMPLETED", "conclusion": "FAILURE"}
    refused(*env(pr=pr), "check gate is not SUCCESS")
    pr = good(); pr["statusCheckRollup"][0] = {"name": "test", "status": "IN_PROGRESS", "conclusion": ""}
    refused(*env(pr=pr), "check test is not SUCCESS")


def test_s16_no_checks_at_all_refuses(env):
    pr = good(); pr["statusCheckRollup"] = []
    refused(*env(pr=pr), "no checks ran")


def test_s16_a_body_without_closes_refuses(env):
    pr = good(); pr["body"] = "## What\nSomething. See #67.\n"
    refused(*env(pr=pr), "no `Closes #n`")


def test_s16_a_pull_request_with_conflicts_refuses(env):
    pr = good(); pr["mergeable"] = "CONFLICTING"
    refused(*env(pr=pr), "has conflicts")


def test_s16_the_happy_path_merges_once_with_a_merge_commit_and_the_review_account_token(env):
    r, merged = env()
    assert r.returncode == 0, r.stderr
    assert merged.count("\n") == 1
    assert "pr merge 12 -R o/r --merge" in merged and "GH_TOKEN=tok-satvik-jain-iitd" in merged
    assert "merged" in r.stdout


def test_s16_skipped_and_neutral_checks_do_not_block(env):
    pr = good(); pr["statusCheckRollup"] += [{"name": "a", "status": "COMPLETED", "conclusion": "SKIPPED"}, {"name": "b", "status": "COMPLETED", "conclusion": "NEUTRAL"}]
    r, merged = env(pr=pr)
    assert r.returncode == 0 and "pr merge" in merged


def test_s16_the_repo_argument_is_used_and_a_missing_pr_number_is_refused(env):
    r, merged = env(args=("12", "x/y"))
    assert r.returncode == 0 and "-R x/y" in merged
    r, merged = env(args=())
    assert r.returncode == 2 and merged == ""
