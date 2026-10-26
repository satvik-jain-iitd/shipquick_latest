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
  repo) case "$*" in *defaultBranchRef*) echo '{"defaultBranchRef":{"name":"main"}}' ;; *) echo "o/r" ;; esac; exit 0 ;;
  issue) case "$2" in
        view) echo '{"state":"OPEN","labels":[]}'; exit 0 ;;
        close) [ -n "${STUB_FAIL_CLOSE:-}" ] && exit 1; echo "GH_TOKEN=$GH_TOKEN GH_REPO=${GH_REPO:-} $*" >> "$STUB_DIR/issue.log"; exit 0 ;;
      esac ;;
  pr) case "$2" in
        view) case "$*" in *state,baseRefName,body*) jq -c '{state: "MERGED", baseRefName: "dev", body: .body}' "$STUB_DIR/pr.json"; exit 0 ;; esac
              cat "$STUB_DIR/pr.json"; exit 0 ;;
        merge) echo "GH_TOKEN=$GH_TOKEN $*" >> "$STUB_DIR/merge.log"; exit 0 ;;
      esac ;;
  api) case "$2" in repos/*) echo '{"default_branch":"main"}'; exit 0 ;; esac; cat "$STUB_DIR/threads.json"; exit 0 ;;
esac
exit 9
"""


class Log(str):
    """The merge log as text, with the issue-close log and every gh call attached."""


def good():
    return {
        "title": "feat(x): a story (#67)", "author": {"login": "klickbae8yt-star"}, "state": "OPEN", "isDraft": False, "mergeable": "MERGEABLE", "headRefOid": "abc123", "body": "## What\nSomething.\n\nCloses #67\n",
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

    def go(pr=None, th=None, mode="auto", args=("12",), fail_close=False):
        (stub / "merge.log").unlink(missing_ok=True)
        (stub / "issue.log").unlink(missing_ok=True)
        e["STUB_FAIL_CLOSE"] = "1" if fail_close else ""   # one call per scenario: a test may call go() twice
        (stub / "pr.json").write_text(json.dumps(pr or good()), encoding="utf-8")
        (stub / "threads.json").write_text(json.dumps(th or threads(True, True)), encoding="utf-8")
        if mode:
            subprocess.run(["bash", str(MODE), "set", mode], cwd=repo, check=True, env=e)
        r = subprocess.run(["bash", str(GATE), *args], cwd=repo, capture_output=True, text=True, env=e)
        merged = (stub / "merge.log").read_text(encoding="utf-8") if (stub / "merge.log").exists() else ""
        out = Log(merged)
        out.closed = (stub / "issue.log").read_text(encoding="utf-8") if (stub / "issue.log").exists() else ""
        out.calls = (stub / "calls.log").read_text(encoding="utf-8") if (stub / "calls.log").exists() else ""
        return r, out

    return go


def refused(result, merged, rule):
    assert result.returncode == 1, (result.stdout, result.stderr)
    assert result.stderr.startswith("refused: ") and rule in result.stderr, result.stderr
    assert merged == "", "the gate must not merge when it refuses"
    assert merged.closed == "", "and it must not close any issue"


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


def test_s16_a_check_still_running_has_no_conclusion_and_refuses(env):
    pr = good(); pr["statusCheckRollup"][0] = {"name": "test", "status": "IN_PROGRESS", "conclusion": None}   # GitHub sends null, not an empty string
    refused(*env(pr=pr), "check test is not SUCCESS")
    pr = good(); pr["statusCheckRollup"][0] = {"name": "test", "status": "QUEUED"}   # and sometimes no conclusion field at all
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


def test_s16_after_a_good_merge_it_closes_the_story_issues_with_the_review_account_token_and_for_the_right_repo(env):
    pr = good(); pr["body"] = "## What\nBoth.\n\nCloses #67\nCloses #5\n"
    r, merged = env(pr=pr, args=("12", "x/y"))
    assert r.returncode == 0, r.stderr
    lines = merged.closed.strip().splitlines()
    assert len(lines) == 2 and all("GH_TOKEN=tok-satvik-jain-iitd" in l and "GH_REPO=x/y" in l for l in lines)
    assert "issue close 67" in lines[0] and "issue close 5" in lines[1]
    assert merged.calls.index("pr merge") < merged.calls.index("issue close"), "issues close only after the merge"
    assert "closed" in r.stdout


def test_s16_if_closing_fails_after_the_merge_the_gate_says_the_merge_happened_and_how_to_finish(env):
    r, merged = env(fail_close=True)
    assert "pr merge 12" in merged, "the merge already happened"
    assert r.returncode == 4 and "merged #12" in r.stdout
    assert "close_linked_issues.py" in r.stderr and "--yes" in r.stderr


def test_s16_the_gate_uses_the_same_closes_rule_as_ci_so_exempt_pull_requests_can_merge(env):
    for title, author in (("chore(deps): bump the github-actions group with 6 updates", "dependabot[bot]"), ("release: v0.6.0 (#71)", "klickbae8yt-star"), ("chore: merge main into dev", "klickbae8yt-star"), ("Bump x from 1 to 2", "dependabot[bot]")):
        pr = good(); pr["body"] = "no issue link here\n"; pr["title"] = title; pr["author"] = {"login": author}
        r, merged = env(pr=pr)
        assert r.returncode == 0 and "pr merge 12" in merged, (title, r.stderr)


def test_s16_a_story_pull_request_without_closes_is_still_refused_and_fixes_counts(env):
    pr = good(); pr["body"] = "no issue link here\n"
    refused(*env(pr=pr), "no `Closes #n`")
    pr = good(); pr["body"] = "Fixes #67\n"
    r, merged = env(pr=pr)
    assert r.returncode == 0 and "pr merge 12" in merged


def test_s16_the_gate_calls_check_closes_instead_of_its_own_grep():
    text = GATE.read_text(encoding="utf-8")
    assert "check_closes.py" in text and "grep -Eiq" not in text
