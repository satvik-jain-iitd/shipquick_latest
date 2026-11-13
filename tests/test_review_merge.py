"""S0.16: the coded merge gate (story #67). A stub `gh` on PATH: no network, no token, nothing is ever merged."""
import base64
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
# the protection call always carries --jq in the script: the stub applies the same filter
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
  api) case "$*" in
         *actions/runs*)
           [ -f "$STUB_DIR/runs_unreadable" ] && { echo "gh: rate limited" >&2; exit 1; }
           [ -f "$STUB_DIR/runs.ndjson" ] && { cat "$STUB_DIR/runs.ndjson"; exit 0; }; exit 0 ;;
         *protection*) [ -f "$STUB_DIR/protection.json" ] && { jq -r ".required_linear_history.enabled" "$STUB_DIR/protection.json"; exit 0; }; exit 1 ;;
         *contents/CLAUDE.md*)
           case "$*" in *" -f "*|*" -F "*) echo "stub: -f/-F on a GET turns gh api into a POST, GitHub 404s" >&2; exit 1 ;; esac
           [ -f "$STUB_DIR/claude_md_b64" ] && { cat "$STUB_DIR/claude_md_b64"; exit 0; }; exit 1 ;;
         *contents/.shipquick/freeze*)
           [ -f "$STUB_DIR/freeze_unreadable" ] && { echo "gh: rate limited" >&2; exit 1; }
           [ -f "$STUB_DIR/freeze_b64" ] && { cat "$STUB_DIR/freeze_b64"; exit 0; }; echo "gh: Not Found (HTTP 404)" >&2; exit 1 ;;
         *contents/.shipquick/features.json*)
           [ -f "$STUB_DIR/features_unreadable" ] && { echo "gh: rate limited" >&2; exit 1; }
           [ -f "$STUB_DIR/features_b64" ] && { cat "$STUB_DIR/features_b64"; exit 0; }; echo "gh: Not Found (HTTP 404)" >&2; exit 1 ;;
         *contents/.shipquick/roles.yml*)
           [ -f "$STUB_DIR/roles_unreadable" ] && { echo "gh: rate limited" >&2; exit 1; }
           cat "$STUB_DIR/roles_yml_b64"; exit 0 ;;
         *contents/.github/workflows/shipquick-call.yml*)
           [ -f "$STUB_DIR/caller_b64" ] && { cat "$STUB_DIR/caller_b64"; exit 0; }; echo "gh: Not Found (HTTP 404)" >&2; exit 1 ;;
         *contents/docs/screens.txt*)
           [ -f "$STUB_DIR/screens_b64" ] && { cat "$STUB_DIR/screens_b64"; exit 0; }; echo "gh: Not Found (HTTP 404)" >&2; exit 1 ;;
         *pulls/*/commits*)
           [ -f "$STUB_DIR/commits.json" ] && { cat "$STUB_DIR/commits.json"; exit 0; }; echo '[]'; exit 0 ;;
         *pulls/*/files*)
           [ -f "$STUB_DIR/pr_files.json" ] && { cat "$STUB_DIR/pr_files.json"; exit 0; }; echo '[]'; exit 0 ;;
       esac
       case "$2" in repos/*) echo '{"default_branch":"main"}'; exit 0 ;; esac; cat "$STUB_DIR/threads.json"; exit 0 ;;
esac
exit 9
"""


class Log(str):
    """The merge log as text, with the issue-close log and every gh call attached."""


def good():
    return {
        "title": "feat(x): a story (#67)", "author": {"login": "klickbae8yt-star"}, "state": "OPEN", "isDraft": False, "mergeable": "MERGEABLE", "baseRefName": "dev", "headRefOid": "abc123", "body": "## What\nSomething.\n\nCloses #67\n",
        "reviews": [{"author": {"login": REVIEWER}, "state": "APPROVED", "commit": {"oid": "abc123"}, "body": "Verdict: approve\nNot checked: nothing\n"}],
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

    def go(runs=None, runs_unreadable=False, pr=None, th=None, mode="auto", args=("12",), fail_close=False, linear=None, dev_link=None, claude_md_unreadable=False, freeze=None, pr_files=None, freeze_unreadable=False, roles=None, roles_unreadable=False, screens=None, caller=None, features=None):
        (stub / "merge.log").unlink(missing_ok=True)
        (stub / "calls.log").unlink(missing_ok=True)
        (stub / "runs.ndjson").unlink(missing_ok=True); (stub / "runs_unreadable").unlink(missing_ok=True)
        if runs is not None:   # story #496: the workflow runs of the head, one JSON object per line, as `gh api --jq .workflow_runs[]` prints them
            (stub / "runs.ndjson").write_text("".join(json.dumps(r) + "\n" for r in runs), encoding="utf-8")
        if runs_unreadable:
            (stub / "runs_unreadable").write_text("1", encoding="utf-8")
        if caller is not None:   # story #225: the PR's own repo's shipquick-call.yml on its base; None = none (404)
            (stub / "caller_b64").write_text(base64.b64encode(caller.encode()).decode(), encoding="utf-8")
        else:
            (stub / "caller_b64").unlink(missing_ok=True)
        if screens is not None:   # story #153: the PR's own repo's docs/screens.txt on its base branch; None = not configured (404)
            (stub / "screens_b64").write_text(base64.b64encode(screens.encode()).decode(), encoding="utf-8")
        else:
            (stub / "screens_b64").unlink(missing_ok=True)
        (stub / "issue.log").unlink(missing_ok=True)
        (stub / "features_b64").unlink(missing_ok=True); (stub / "features_unreadable").unlink(missing_ok=True)
        if features == "rate":   # story #424: the flags are read from the PR's base branch on GitHub, never the local tree
            (stub / "features_unreadable").write_text("1", encoding="utf-8")
        elif features is not None:
            (stub / "features_b64").write_text(base64.b64encode(features.encode()).decode(), encoding="utf-8")
        (stub / "protection.json").unlink(missing_ok=True)
        default_roles_yml = "coder:\n  - klickbae8yt-star\nreviewer:\n  - satvik-jain-iitd\nowner: satvik-jain-iitd\n"
        (stub / "roles_yml_b64").write_text(base64.b64encode((roles or default_roles_yml).encode()).decode(), encoding="utf-8")
        roles_unreadable_file = stub / "roles_unreadable"
        if roles_unreadable:
            roles_unreadable_file.write_text("1", encoding="utf-8")
        else:
            roles_unreadable_file.unlink(missing_ok=True)
        freeze_b64_file = stub / "freeze_b64"
        if freeze:
            freeze_b64_file.write_text(base64.b64encode(freeze.encode()).decode(), encoding="utf-8")
        else:
            freeze_b64_file.unlink(missing_ok=True)
        pr_files_file = stub / "pr_files.json"
        if pr_files is not None:
            pr_files_file.write_text(json.dumps(pr_files), encoding="utf-8")
        else:
            pr_files_file.unlink(missing_ok=True)
        freeze_unreadable_file = stub / "freeze_unreadable"
        if freeze_unreadable:
            freeze_unreadable_file.write_text("1", encoding="utf-8")
        else:
            freeze_unreadable_file.unlink(missing_ok=True)
        if linear is not None:   # the base branch protection answer: required_linear_history on or off; None = the branch has no protection (the call fails)
            (stub / "protection.json").write_text(json.dumps({"required_linear_history": {"enabled": linear}}), encoding="utf-8")
        # story #122 fix: the UAT gate reads the PR's OWN repo's CLAUDE.md via the GitHub contents API (base64),
        # never the local checkout's — a local checkout without a Dev link must not make a different repo exempt.
        b64_file = stub / "claude_md_b64"
        if claude_md_unreadable:
            b64_file.unlink(missing_ok=True)
        else:
            body = f"## Environments\n- Dev link: {dev_link}\n" if dev_link else "# no Dev link configured\n"
            b64_file.write_text(base64.b64encode(body.encode()).decode(), encoding="utf-8")
        # the local checkout deliberately carries no CLAUDE.md of its own, to prove it is never read
        (repo / "CLAUDE.md").unlink(missing_ok=True)
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
    refused(*env(pr=pr), "not approved by a reviewer account")


def test_s16_an_approval_of_an_older_commit_is_not_enough(env):
    pr = good(); pr["reviews"][0]["commit"]["oid"] = "old000"
    refused(*env(pr=pr), "not approved by a reviewer account")


def test_s16_a_later_request_for_changes_cancels_the_approval(env):
    pr = good(); pr["reviews"].append({"author": {"login": REVIEWER}, "state": "CHANGES_REQUESTED", "commit": {"oid": "abc123"}})
    refused(*env(pr=pr), "not approved by a reviewer account")


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


def test_s112_a_stale_failed_run_of_the_same_check_name_is_ignored_once_a_later_run_of_it_passed(env):
    pr = good()
    pr["statusCheckRollup"] = [
        {"name": "gate", "status": "COMPLETED", "conclusion": "FAILURE", "startedAt": "2026-10-29T13:08:00Z"},
        {"name": "gate", "status": "COMPLETED", "conclusion": "SUCCESS", "startedAt": "2026-10-30T04:00:00Z"},
        {"name": "test", "status": "COMPLETED", "conclusion": "SUCCESS", "startedAt": "2026-10-30T04:00:00Z"},
    ]
    r, merged = env(pr=pr)
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert merged != "", "the gate must merge once the latest run of every check passed"


def test_s112_a_later_failed_run_is_not_masked_by_an_earlier_pass_of_the_same_name(env):
    pr = good()
    pr["statusCheckRollup"] = [
        {"name": "gate", "status": "COMPLETED", "conclusion": "SUCCESS", "startedAt": "2026-10-29T13:08:00Z"},
        {"name": "gate", "status": "COMPLETED", "conclusion": "FAILURE", "startedAt": "2026-10-30T04:00:00Z"},
        {"name": "test", "status": "COMPLETED", "conclusion": "SUCCESS", "startedAt": "2026-10-30T04:00:00Z"},
    ]
    refused(*env(pr=pr), "check gate is not SUCCESS")


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


# ---- story #87: the merge method. Squash when the base branch needs a straight history, a flag wins, the default stays merge. ----
def test_q0_a_base_branch_that_needs_linear_history_is_squashed(env):
    r, merged = env(linear=True)
    assert r.returncode == 0, r.stderr
    assert "--squash" in merged and "--merge" not in merged


def test_q0_the_flag_wins_over_the_setting(env):
    r, merged = env(args=("12", "--method", "rebase"), linear=True)
    assert r.returncode == 0, r.stderr
    assert "--rebase" in merged and "--squash" not in merged


def test_q0_no_flag_and_no_setting_still_merges_with_a_merge_commit(env):
    for linear in (False, None):   # protection with linear history off, and a branch with no protection at all
        r, merged = env(linear=linear)
        assert r.returncode == 0, r.stderr
        assert "--merge" in merged and "--squash" not in merged


def test_q0_an_unknown_method_is_a_usage_error_and_merges_nothing(env):
    r, merged = env(args=("12", "--method", "fast"))
    assert r.returncode == 2 and "usage" in r.stderr, (r.stdout, r.stderr)
    assert merged == ""


# ---- story #120: a dev -> main promotion refuses without a followable, fully-ticked UAT checklist ----
UAT_STORY = """- [x] #219 Fix: cart total after removing an item
  Open: https://dev.app.example.com/cart (log in with test phone 9999999999, OTP 123456)
  1. Add "Masala Dosa" 3 times.
  2. Tap the minus on "Masala Dosa" once.
  Expected: the cart shows 2 x Masala Dosa and the total is ₹240 (2 x ₹120).
"""
UAT_TAIL = """- [x] Old flows still work
- [x] Design matches the approved boards
Known bugs going to production: none
"""


DEV_LINK = "https://dev.app.example.com"


def test_s120_a_promotion_pr_to_main_without_a_uat_section_refuses(env):
    pr = good(); pr["baseRefName"] = "main"
    refused(*env(pr=pr, dev_link=DEV_LINK), "UAT on dev")


def test_s120_a_promotion_pr_to_main_with_a_complete_ticked_uat_checklist_merges(env):
    pr = good(); pr["baseRefName"] = "main"
    pr["body"] = pr["body"] + f"\n## UAT on dev ({DEV_LINK})\n{UAT_STORY}{UAT_TAIL}"
    r, merged = env(pr=pr, dev_link=DEV_LINK)
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert merged != ""


def test_s120_an_unticked_box_in_the_uat_checklist_refuses(env):
    pr = good(); pr["baseRefName"] = "main"
    pr["body"] = pr["body"] + f"\n## UAT on dev ({DEV_LINK})\n{UAT_STORY.replace('[x] #219', '[ ] #219')}{UAT_TAIL}"
    refused(*env(pr=pr, dev_link=DEV_LINK), "unticked")


def test_s120_a_uat_story_line_with_no_expected_refuses(env):
    pr = good(); pr["baseRefName"] = "main"
    broken_story = UAT_STORY.replace('  Expected: the cart shows 2 x Masala Dosa and the total is ₹240 (2 x ₹120).\n', "")
    pr["body"] = pr["body"] + f"\n## UAT on dev ({DEV_LINK})\n{broken_story}{UAT_TAIL}"
    refused(*env(pr=pr, dev_link=DEV_LINK), "not followable")


def test_s120_a_regular_feature_pr_to_dev_needs_no_uat_checklist(env):
    r, merged = env(dev_link=DEV_LINK)   # good() already targets dev, no UAT section at all
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert merged != ""


# ---- story #122 (PR #122 review blocker): exempt by project (no Dev link configured), never by PR title ----
def test_s122_a_project_with_no_dev_link_is_exempt_even_with_a_release_title_and_no_uat_section(env):
    pr = good(); pr["baseRefName"] = "main"; pr["title"] = "release: v0.8.0"
    r, merged = env(pr=pr)   # no dev_link passed: this project's own CLAUDE.md has none
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert merged != ""


def test_s122_a_release_titled_promotion_still_refuses_when_the_project_has_a_dev_link_and_an_unticked_box(env):
    pr = good(); pr["baseRefName"] = "main"; pr["title"] = "release: v0.8.0"
    pr["body"] = pr["body"] + f"\n## UAT on dev ({DEV_LINK})\n{UAT_STORY.replace('[x] #219', '[ ] #219')}{UAT_TAIL}"
    refused(*env(pr=pr, dev_link=DEV_LINK), "unticked")


def test_s122_cannot_read_the_pr_repos_claude_md_refuses_it_is_never_treated_as_exempt(env):
    pr = good(); pr["baseRefName"] = "main"
    refused(*env(pr=pr, claude_md_unreadable=True), "cannot read")


# ---- story #126: a release freeze blocks every merge into main except a PR that only lifts it ----
def test_s126_a_frozen_main_refuses_a_normal_promotion(env):
    pr = good(); pr["baseRefName"] = "main"
    refused(*env(pr=pr, freeze="reason: holiday freeze\nuntil: 2099-01-01\n"), "frozen until 2099-01-01")


def test_s126_an_expired_freeze_still_refuses_and_says_stale(env):
    pr = good(); pr["baseRefName"] = "main"
    refused(*env(pr=pr, freeze="reason: incident\nuntil: 2000-01-01\n"), "STALE")


def test_s126_a_pr_that_only_removes_the_freeze_file_is_still_a_protected_path(env):
    # review blocker on PR #141: lifting a freeze is the owner's own decision too, so a lift-only
    # PR no longer auto-merges -- .shipquick/* is protected with no exception.
    pr = good(); pr["baseRefName"] = "main"
    files = [{"filename": ".shipquick/freeze", "status": "removed"}]
    refused(*env(pr=pr, freeze="reason: x\nuntil: 2099-01-01\n", pr_files=files), "protected path, owner merges")


def test_s126_a_pr_that_removes_the_freeze_file_plus_something_else_is_not_exempt(env):
    # not the lift-only shape, so it is caught by the (now broader) protected-paths check before
    # the freeze check even runs -- still refused, same as before PR #141's review, different line.
    pr = good(); pr["baseRefName"] = "main"
    files = [{"filename": ".shipquick/freeze", "status": "removed"}, {"filename": "README.md", "status": "modified"}]
    refused(*env(pr=pr, freeze="reason: x\nuntil: 2099-01-01\n", pr_files=files), "protected path")


def test_s126_a_pr_that_edits_the_freeze_file_rather_than_removing_it_is_not_exempt(env):
    pr = good(); pr["baseRefName"] = "main"
    files = [{"filename": ".shipquick/freeze", "status": "modified"}]
    refused(*env(pr=pr, freeze="reason: x\nuntil: 2099-01-01\n", pr_files=files), "protected path")


def test_s126_no_freeze_file_at_all_is_not_frozen(env):
    r, merged = env()   # good() targets dev; also true for a main promotion, covered by the s120/s122 merge-success tests above
    assert r.returncode == 0, (r.stdout, r.stderr)


def test_s126_cannot_read_the_freeze_file_for_a_reason_other_than_404_refuses(env):
    pr = good(); pr["baseRefName"] = "main"
    refused(*env(pr=pr, freeze_unreadable=True), "cannot read")


# ---- story #131: harden the merge gate -- a required "gate" check, plus protected paths ----
def test_s131_no_gate_check_at_all_refuses_even_though_every_other_check_passed(env):
    pr = good(); pr["statusCheckRollup"] = [{"name": "test", "status": "COMPLETED", "conclusion": "SUCCESS"}]   # gate job deleted from the caller
    refused(*env(pr=pr), "no required check named exactly gate")


def test_s131_the_required_gate_check_name_also_matches_the_child_shape(env):
    pr = good(); pr["statusCheckRollup"] = [{"name": "test", "status": "COMPLETED", "conclusion": "SUCCESS"}, {"name": "shipquick-checks / gate", "status": "COMPLETED", "conclusion": "SUCCESS"}]
    r, merged = env(pr=pr)
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert merged != ""


def test_s131_a_gate_check_that_is_not_itself_success_refuses(env):
    pr = good(); pr["statusCheckRollup"] = [{"name": "gate", "status": "COMPLETED", "conclusion": "NEUTRAL"}]   # the generic loop treats NEUTRAL as passed; the gate itself must not
    refused(*env(pr=pr), "required check gate is NEUTRAL, not SUCCESS")


def test_s131_a_pr_touching_a_protected_path_refuses(env):
    files = [{"filename": ".github/workflows/ci.yml", "status": "modified"}]
    refused(*env(pr_files=files), "protected path, owner merges")


def test_s131_a_pr_touching_an_unrelated_file_is_not_protected_and_merges(env):
    files = [{"filename": "README.md", "status": "modified"}]
    r, merged = env(pr_files=files)
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert merged != ""


def test_s131_protected_paths_cover_configs_baselines_and_the_submodule_pin(env):
    for f in (".claude/settings.json", "design/tokens.json", ".stylelintrc.json", "eslint.config.js",
              ".swiftlint.yml", "detekt-baseline.yml", ".dependency-cruiser.js", ".importlinter",
              "docs/frontend-paths.txt", "docs/architecture-paths.txt", "docs/guard.yml",
              "knowledge/shipquick_latest", "android/app/detekt-baseline.xml"):
        files = [{"filename": f, "status": "modified"}]
        result, merged = env(pr_files=files)
        assert result.returncode == 1 and "protected path" in result.stderr, (f, result.stderr)


def test_s131_emptying_frontend_paths_txt_is_itself_a_protected_path_edit(env):
    files = [{"filename": "docs/frontend-paths.txt", "status": "modified"}]
    refused(*env(pr_files=files), "protected path, owner merges (docs/frontend-paths.txt)")


# ---- review blocker on PR #141: the enforcers themselves must be protected paths too ----
def test_s131_the_enforcer_scripts_are_themselves_protected(env):
    for f in ("scripts/protected_paths.txt", "scripts/review_merge.sh", "scripts/mode.sh",
              "scripts/has_dev_link.sh", "scripts/check_closes.py", "scripts/check_uat.py",
              ".shipquick/roles.yml", ".shipquick/mode"):
        result, merged = env(pr_files=[{"filename": f, "status": "modified"}])
        assert result.returncode == 1 and "protected path" in result.stderr, (f, result.stderr)


def test_s225_kit_branch_py_is_a_protected_path_since_the_gate_reads_kit_branch_through_it(env):
    lines = (ROOT / "scripts" / "protected_paths.txt").read_text(encoding="utf-8").splitlines()
    assert "scripts/kit_branch.py" in lines
    result, merged = env(pr_files=[{"filename": "scripts/kit_branch.py", "status": "modified"}])
    assert result.returncode == 1 and "protected path" in result.stderr, result.stderr


def test_s131_a_lift_only_freeze_pr_is_refused_in_auto_mode_the_owner_merges_it(env):
    pr = good(); pr["baseRefName"] = "main"
    files = [{"filename": ".shipquick/freeze", "status": "removed"}]
    refused(*env(pr=pr, freeze="reason: x\nuntil: 2099-01-01\n", pr_files=files), "protected path, owner merges")


def test_s131_editing_the_freeze_file_rather_than_removing_it_is_still_protected(env):
    files = [{"filename": ".shipquick/freeze", "status": "modified"}]
    result, merged = env(pr_files=files)
    assert result.returncode == 1 and "protected path" in result.stderr


# ---- story #140: who may author, who may approve -- come from .shipquick/roles.yml, the #114 case ----
def test_s140_an_author_not_in_the_coder_list_refuses_even_with_a_reviewer_approval(env):
    pr = good(); pr["author"] = {"login": "some-random-account"}
    refused(*env(pr=pr), "PR author some-random-account is not a coder account")


def test_s140_a_pr_opened_by_the_reviewer_account_refuses_the_114_case(env):
    pr = good(); pr["author"] = {"login": REVIEWER}
    refused(*env(pr=pr), "is not a coder account")


def test_s140_the_reviewer_approving_their_own_pr_is_never_enough_even_if_they_are_also_listed_as_coder(env):
    roles = "coder:\n  - klickbae8yt-star\n  - satvik-jain-iitd\nreviewer:\n  - satvik-jain-iitd\nowner: satvik-jain-iitd\n"
    pr = good(); pr["author"] = {"login": REVIEWER}; pr["reviews"] = [{"author": {"login": REVIEWER}, "state": "APPROVED", "commit": {"oid": "abc123"}}]
    refused(*env(pr=pr, roles=roles), "not approved by a reviewer account")


def test_s140_a_second_reviewer_account_in_roles_yml_is_honored(env):
    roles = "coder:\n  - klickbae8yt-star\nreviewer:\n  - satvik-jain-iitd\n  - second-reviewer\nowner: satvik-jain-iitd\n"
    pr = good(); pr["reviews"] = [{"author": {"login": "second-reviewer"}, "state": "APPROVED", "commit": {"oid": "abc123"}, "body": "Verdict: approve\nNot checked: nothing\n"}]
    r, merged = env(pr=pr, roles=roles)
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert merged != ""


def test_s140_dependabot_is_exempt_from_the_coder_check_but_still_needs_a_real_reviewer_approval(env):
    pr = good(); pr["author"] = {"login": "dependabot[bot]"}; pr["title"] = "chore(deps): bump x"; pr["body"] = "no issue link\n"
    r, merged = env(pr=pr)   # good()'s default review is still from REVIEWER, a real reviewer account
    assert r.returncode == 0, (r.stdout, r.stderr)


def test_s140_cannot_read_roles_yml_refuses_it_is_never_treated_as_exempt(env):
    refused(*env(roles_unreadable=True), "cannot read")


# ---- story #225, review of PR #227 fix 2: a rule-24 child's roles.yml lives on its kit branch ----
KIT_CALLER = "jobs:\n  shipquick-checks:\n    with:\n      shipquick_ref: abc\n      kit_branch: documents  # rule 24\n"


def test_s225_a_pr_into_main_of_a_rule24_child_reads_roles_yml_from_the_kit_branch(env):
    pr = {**good(), "baseRefName": "main"}
    r, merged = env(pr=pr, caller=KIT_CALLER)
    assert "contents/.shipquick/roles.yml?ref=documents" in merged.calls, merged.calls
    assert "contents/.shipquick/roles.yml?ref=main" not in merged.calls


def test_s225_a_pr_into_the_kit_branch_itself_reads_its_own_base(env):
    pr = {**good(), "baseRefName": "documents"}
    r, merged = env(pr=pr, caller=KIT_CALLER)
    assert "contents/.shipquick/roles.yml?ref=documents" in merged.calls


def test_s225_no_caller_or_no_kit_branch_reads_roles_yml_from_the_base_as_before(env):
    r, merged = env()
    assert r.returncode == 0, r.stderr
    assert "contents/.shipquick/roles.yml?ref=dev" in merged.calls


def test_s225_an_expression_as_kit_branch_refuses(env):
    refused(*env(caller=KIT_CALLER.replace("documents  # rule 24", "${{ github.base_ref }}")), "expression")


def test_s225_roles_yml_missing_on_the_kit_branch_names_the_kit_branch(env):
    refused(*env(pr={**good(), "baseRefName": "main"}, caller=KIT_CALLER, roles_unreadable=True), "kit branch documents")


# Story #180 (S0): a protected PR merges only when the approving review records a second review and
# the owner's own yes. `.shipquick/*` (mode, roles, freeze) stays owner-merge only, whatever the review says.
PROTECTED = [{"filename": ".github/workflows/ci.yml", "status": "modified"}]
TODAY = __import__("datetime").date.today().isoformat()   # the gate checks the yes is at most 14 days old
YES = f'Verdict: approve\nNot checked: nothing\nApproved.\nSecond review: fresh reviewer agent, 0 open findings\nOwner yes: {TODAY} "haan merge karo"\n'


def with_review(body):
    pr = good()
    pr["reviews"][0]["body"] = body
    return pr


def test_s180_a_protected_pr_with_a_second_review_and_the_owner_yes_merges(env):
    r, merged = env(pr=with_review(YES), pr_files=PROTECTED)
    assert r.returncode == 0, r.stderr
    assert "pr merge 12" in merged


def test_s180_a_protected_pr_without_the_owner_yes_refuses(env):
    body = YES.replace(f'Owner yes: {TODAY} "haan merge karo"\n', "")
    refused(*env(pr=with_review(body), pr_files=PROTECTED), "Owner yes:")


def test_s180_a_protected_pr_without_a_second_review_refuses(env):
    body = YES.replace("Second review: fresh reviewer agent, 0 open findings\n", "")
    refused(*env(pr=with_review(body), pr_files=PROTECTED), "Second review:")


def test_s180_an_owner_yes_with_no_date_or_no_quoted_words_refuses(env):
    refused(*env(pr=with_review(YES.replace(f"{TODAY} ", "")), pr_files=PROTECTED), "Owner yes:")
    refused(*env(pr=with_review(YES.replace('"haan merge karo"', "yes")), pr_files=PROTECTED), "Owner yes:")


def test_s180_the_lines_in_the_pr_body_do_not_count_only_the_approving_review(env):
    pr = good()
    pr["body"] += "\n" + YES
    refused(*env(pr=pr, pr_files=PROTECTED), "owner merges")


def test_s180_a_shipquick_mode_or_roles_change_stays_owner_merge_even_with_the_yes(env):
    files = [{"filename": ".shipquick/mode", "status": "modified"}]
    refused(*env(pr=with_review(YES), pr_files=files), "owner merges")


# PR #196 second review: the two lines must carry real content, and a rename cannot dodge the protected list.
def test_s180_an_impossible_or_future_owner_yes_date_refuses(env):
    for bad in ("9999-99-99", "2999-01-01"):
        refused(*env(pr=with_review(YES.replace(TODAY, bad)), pr_files=PROTECTED), "Owner yes:")


def test_s180_an_owner_yes_older_than_14_days_refuses(env):
    refused(*env(pr=with_review(YES.replace(TODAY, "2020-01-01")), pr_files=PROTECTED), "Owner yes:")


def test_s180_placeholder_lines_refuse(env):
    refused(*env(pr=with_review(YES.replace('"haan merge karo"', '"<his words>"')), pr_files=PROTECTED), "Owner yes:")
    refused(*env(pr=with_review(YES.replace("fresh reviewer agent, 0 open findings", "<who, findings>")), pr_files=PROTECTED), "Second review:")
    refused(*env(pr=with_review(YES.replace("fresh reviewer agent, 0 open findings", "ok")), pr_files=PROTECTED), "Second review:")


def test_s180_renaming_a_protected_file_away_is_still_protected(env):
    files = [{"filename": "docs/old-list.txt", "previous_filename": "scripts/protected_paths.txt", "status": "renamed"}]
    refused(*env(pr_files=files), "owner merges")


def test_s180_renaming_shipquick_roles_away_stays_owner_only(env):
    files = [{"filename": "docs/roles.yml", "previous_filename": ".shipquick/roles.yml", "status": "renamed"}]
    refused(*env(pr=with_review(YES), pr_files=files), "mode, roles and freeze")


def test_s180_claude_md_is_a_protected_path(env):
    refused(*env(pr_files=[{"filename": "CLAUDE.md", "status": "modified"}]), "owner merges")


# ---- story #153: the approving review must say the render was compared with the named board ----
SCREENS = "welcome | / | 412x915 | welcome\n"


# Story #318: every approval carries the Verdict and Not checked lines; these helpers add them to the body under test.
VERDICT_LINES = "Verdict: approve\nNot checked: nothing\n"


def design_pr(review_body):
    pr = good()
    pr["body"] = "Design board: Production / C1 Welcome\nApproved: 2026-11-08\nRender: https://github.com/o/r/actions/runs/1\n\nCloses #67\n"
    pr["reviews"] = [{"author": {"login": REVIEWER}, "state": "APPROVED", "commit": {"oid": "abc123"}, "body": VERDICT_LINES + review_body}]
    return pr


def test_s153_an_approval_on_the_diff_alone_refuses_a_frontend_pr_with_screens_configured(env):
    refused(*env(pr=design_pr("LGTM"), screens=SCREENS), "Render: Production / C1 Welcome -- matches")


def test_s153_an_approval_that_says_the_render_matches_the_board_merges(env):
    r, merged = env(pr=design_pr("Compared side by side.\nRender: Production / C1 Welcome -- matches"), screens=SCREENS)
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert merged != ""


def test_s153_a_project_with_no_screens_txt_is_unaffected(env):
    r, merged = env(pr=design_pr("LGTM"))
    assert r.returncode == 0, (r.stdout, r.stderr)


def test_s153_a_second_reviewers_matches_line_counts_when_the_first_approval_lacks_it(env):
    roles = "coder:\n  - klickbae8yt-star\nreviewer:\n  - satvik-jain-iitd\n  - second-reviewer\nowner: satvik-jain-iitd\n"
    pr = design_pr("LGTM")
    pr["reviews"].append({"author": {"login": "second-reviewer"}, "state": "APPROVED", "commit": {"oid": "abc123"}, "body": "Render: Production / C1 Welcome -- matches"})
    r, merged = env(pr=pr, roles=roles, screens=SCREENS)
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert merged != ""


# Story #139 (ADR-011): with session lists in roles.yml, the approver's session must not have built the PR.
SESSION_ROLES = ("coder:\n  - klickbae8yt-star\nreviewer:\n  - satvik-jain-iitd\nowner: satvik-jain-iitd\n"
                 "coder_sessions:\n  - proj-dev\nreviewer_sessions:\n  - proj-qa\n")


def session_pr(review_body, *built_by, stub_dir):
    pr = good()
    pr["reviews"][0]["body"] = VERDICT_LINES + review_body
    (stub_dir / "commits.json").write_text(json.dumps(
        [{"commit": {"message": f"feat: x\n\nBuilt-by: {s}\n"}} for s in built_by]), encoding="utf-8")
    return pr


@pytest.fixture
def stub_dir(env, tmp_path):
    return tmp_path / "stub"


def test_s139_an_approval_from_the_session_that_built_a_commit_refuses(env, stub_dir):
    r, merged = env(pr=session_pr("Reviewed-by: proj-qa", "proj-dev", "proj-qa", stub_dir=stub_dir), roles=SESSION_ROLES)
    refused(r, merged, "proj-qa built a commit")


def test_s139_an_approval_that_names_no_session_refuses(env, stub_dir):
    r, merged = env(pr=session_pr("LGTM", "proj-dev", stub_dir=stub_dir), roles=SESSION_ROLES)
    refused(r, merged, "names no session")


def test_s139_an_approval_from_a_reviewer_session_that_built_nothing_merges(env, stub_dir):
    r, merged = env(pr=session_pr("Reviewed-by: proj-qa", "proj-dev", stub_dir=stub_dir), roles=SESSION_ROLES)
    assert r.returncode == 0, r.stderr
    assert "pr merge 12" in merged


def test_s139_without_session_lists_the_review_body_is_not_read(env):
    r, merged = env()
    assert r.returncode == 0, r.stderr


def test_s139_every_built_by_line_counts_not_only_the_first(env, stub_dir):
    # PR #178 review: a prose "Built-by:" line earlier in the body must not hide the real trailer.
    pr = session_pr("Reviewed-by: proj-qa", stub_dir=stub_dir)
    (stub_dir / "commits.json").write_text(json.dumps(
        [{"commit": {"message": "feat: x\n\nBuilt-by: proj-dev is how it works\n\nBuilt-by: proj-qa\n"}}]), encoding="utf-8")
    r, merged = env(pr=pr, roles=SESSION_ROLES)
    refused(r, merged, "proj-qa built a commit")


def test_s139_a_dev_merge_commit_by_the_reviewer_session_does_not_block_its_approval(env, stub_dir):
    pr = session_pr("Reviewed-by: proj-qa", stub_dir=stub_dir)
    (stub_dir / "commits.json").write_text(json.dumps([
        {"parents": [{}], "commit": {"message": "feat: x\n\nBuilt-by: proj-dev\n"}},
        {"parents": [{}, {}], "commit": {"message": "Merge dev into feat/x\n\nBuilt-by: proj-qa\n"}}]), encoding="utf-8")
    r, merged = env(pr=pr, roles=SESSION_ROLES)
    assert r.returncode == 0, r.stderr


# Story #194: lows from the PR #196 verify.
def _days_ago(n):
    import datetime
    return (datetime.date.today() - datetime.timedelta(days=n)).isoformat()


def test_s194_an_owner_yes_of_14_days_passes_and_15_refuses(env):
    r, merged = env(pr=with_review(YES.replace(TODAY, _days_ago(14))), pr_files=PROTECTED)
    assert r.returncode == 0, r.stderr
    refused(*env(pr=with_review(YES.replace(TODAY, _days_ago(15))), pr_files=PROTECTED), "Owner yes:")


def test_s194_owner_yes_words_made_only_of_spaces_refuse(env):
    refused(*env(pr=with_review(YES.replace('"haan merge karo"', '"    "')), pr_files=PROTECTED), "Owner yes:")


def test_s194_a_second_review_of_dots_refuses(env):
    refused(*env(pr=with_review(YES.replace("fresh reviewer agent, 0 open findings", "..........")), pr_files=PROTECTED), "Second review:")


def test_s194_the_second_review_prefix_does_not_count_as_words(env):
    refused(*env(pr=with_review(YES.replace("fresh reviewer agent, 0 open findings", "ok fine!!!!")), pr_files=PROTECTED), "Second review:")


def test_s194_owner_yes_words_need_a_letter(env):
    refused(*env(pr=with_review(YES.replace('"haan merge karo"', '".."')), pr_files=PROTECTED), "Owner yes:")


def test_s194_an_owner_yes_in_devanagari_passes(env):
    r, merged = env(pr=with_review(YES.replace('"haan merge karo"', '"हाँ मर्ज करो"')), pr_files=PROTECTED)
    assert r.returncode == 0, r.stderr


# Story #318 (A4b): the approving review must carry a `Verdict:` line and a `Not checked:` line.
VERDICT_BODY = "Verdict: approve, matches the story\nNot checked: the live dev link (no UAT here)\n"


def test_s318_an_approval_without_a_verdict_line_refuses(env):
    body = VERDICT_BODY.replace("Verdict: approve, matches the story\n", "")
    refused(*env(pr=with_review(body)), "Verdict:")


def test_s318_an_approval_without_a_not_checked_line_refuses(env):
    body = VERDICT_BODY.replace("Not checked: the live dev link (no UAT here)\n", "")
    refused(*env(pr=with_review(body)), "Not checked:")


def test_s318_the_words_inside_a_sentence_are_not_the_line(env):
    refused(*env(pr=with_review("Looks fine, Verdict: approve and Not checked: nothing\n")), "Verdict:")


def test_s318_an_approval_with_both_lines_merges(env):
    r, merged = env(pr=with_review(VERDICT_BODY))
    assert r.returncode == 0, r.stderr
    assert "pr merge 12" in merged


def _flags(**f):
    return json.dumps({"version": 1, "features": {k: {"on": v} for k, v in f.items()}})


def test_s424_close_on_merge_off_at_the_base_ref_needs_no_closes_link(env):
    pr = good(); pr["body"] = "## What\nNo link.\n"
    r, merged = env(pr=pr, features=_flags(**{"close-on-merge": False}))
    assert r.returncode == 0, r.stderr
    assert "contents/.shipquick/features.json?ref=dev" in merged.calls


def test_s424_a_local_features_file_saying_off_is_never_read(env, tmp_path):
    pr = good(); pr["body"] = "## What\nNo link.\n"
    (tmp_path / "repo" / ".shipquick").mkdir()
    (tmp_path / "repo" / ".shipquick" / "features.json").write_text(_flags(**{"close-on-merge": False}), encoding="utf-8")
    refused(*env(pr=pr), "no `Closes #n`")   # the base ref has no file: default on, so the link is required


def test_s424_an_unreadable_or_broken_base_features_file_refuses(env):
    refused(*env(features="rate"), "features")
    refused(*env(features="{oops"), "features")


# ---- story #496 (epic #485 items 15 and 16): only the PR's own, newest run of each workflow counts ----
def row(name, run, concl="SUCCESS", started="2026-11-13T10:00:00Z"):
    return {"name": name, "status": "COMPLETED", "conclusion": concl, "startedAt": started,
            "detailsUrl": f"https://github.com/o/r/actions/runs/{run}/job/{run}1"}


def wf_run(run_id, event="pull_request", workflow=1, number=1, prs=(12,)):
    """One workflow run of the head. `prs` are the numbers of the pull requests the run names (the tests merge PR 12)."""
    return {"id": run_id, "event": event, "workflow_id": workflow, "run_number": number, "head_sha": "abc123",
            "pull_requests": [{"number": n} for n in prs]}


def test_s496_a_manual_run_with_a_green_gate_cannot_replace_a_red_pr_result(env):
    """Epic #485 item 15. The manual run skips the PR-only jobs and starts later, so its green gate used to win."""
    pr = good()
    pr["statusCheckRollup"] = [
        row("tdd", 100, "FAILURE", "2026-11-13T10:00:00Z"), row("gate", 100, "FAILURE", "2026-11-13T10:05:00Z"),
        row("tdd", 101, "SKIPPED", "2026-11-13T11:00:00Z"), row("gate", 101, "SUCCESS", "2026-11-13T11:05:00Z"),
    ]
    runs = [wf_run(100, "pull_request", 1, 1), wf_run(101, "workflow_dispatch", 1, 2)]
    refused(*env(pr=pr, runs=runs), "is not SUCCESS")   # the PR run is red on tdd and on gate; the first by name is named


def test_s496_a_push_run_on_the_same_head_is_not_counted_either(env):
    pr = good()
    pr["statusCheckRollup"] = [row("gate", 100, "FAILURE"), row("gate", 101, "SUCCESS", "2026-11-13T11:00:00Z")]
    runs = [wf_run(100, "pull_request", 1, 1), wf_run(101, "push", 1, 2)]
    refused(*env(pr=pr, runs=runs), "check gate is not SUCCESS")


def test_s496_a_check_row_from_a_run_that_a_newer_run_replaced_is_not_counted(env):
    """The #509 case: a run cancelled before the test matrix expanded left a check named `test` (cancelled). The next run
    on the same head named the job `test (3.12)` and passed. The old row belongs to a replaced run, so it is not counted."""
    pr = good()
    pr["statusCheckRollup"] = [
        row("test", 100, "CANCELLED", "2026-11-13T10:00:00Z"),
        row("test (3.12)", 102, "SUCCESS", "2026-11-13T10:10:00Z"), row("gate", 102, "SUCCESS", "2026-11-13T10:12:00Z"),
    ]
    runs = [wf_run(100, "pull_request", 1, 1), wf_run(102, "pull_request", 1, 3)]
    r, merged = env(pr=pr, runs=runs)
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert merged != "", "the gate must merge: the cancelled row is from a replaced run"


def test_s496_the_newest_run_of_a_workflow_still_counts_when_it_is_red(env):
    pr = good()
    pr["statusCheckRollup"] = [row("gate", 100, "SUCCESS"), row("gate", 102, "FAILURE", "2026-11-13T10:10:00Z")]
    runs = [wf_run(100, "pull_request", 1, 1), wf_run(102, "pull_request", 1, 3)]
    refused(*env(pr=pr, runs=runs), "check gate is not SUCCESS")


def test_s496_a_run_of_another_workflow_is_not_replaced_by_a_newer_run_of_this_one(env):
    """The replacing rule is per workflow and event: a red check of another workflow still blocks the merge."""
    pr = good()
    pr["statusCheckRollup"] = [row("lint-docs", 200, "FAILURE"), row("gate", 102, "SUCCESS", "2026-11-13T10:10:00Z")]
    runs = [wf_run(200, "pull_request", 2, 1), wf_run(102, "pull_request", 1, 3)]
    refused(*env(pr=pr, runs=runs), "check lint-docs is not SUCCESS")


def test_s496_an_unreadable_run_list_refuses(env):
    pr = good()
    pr["statusCheckRollup"] = [row("gate", 100)]
    refused(*env(pr=pr, runs_unreadable=True), "cannot read the workflow runs")


def test_s496_a_check_from_a_run_the_list_does_not_name_refuses(env):
    pr = good()
    pr["statusCheckRollup"] = [row("gate", 100)]
    refused(*env(pr=pr, runs=[wf_run(999, "pull_request", 1, 1)]), "not in the workflow runs")


def test_s496_a_pull_request_run_of_another_pr_on_the_same_head_is_not_counted(env):
    """Second review of #513: two PRs can share one head commit. The newest pull_request run of the head may belong to
    the other PR, so only a run whose pull_requests list names this PR counts."""
    pr = good()
    pr["statusCheckRollup"] = [row("gate", 100, "FAILURE"), row("gate", 101, "SUCCESS", "2026-11-13T11:00:00Z")]
    runs = [wf_run(100, "pull_request", 1, 1, prs=(12,)), wf_run(101, "pull_request", 1, 2, prs=(99,))]
    refused(*env(pr=pr, runs=runs), "two pull requests share this head")


def test_s496_a_run_that_names_this_pr_and_another_refuses(env):
    """Second review of #513: `pull_requests` lists every open PR on the head, so (12, 99) is two PRs on one head."""
    pr = good()
    pr["statusCheckRollup"] = [row("gate", 100)]
    refused(*env(pr=pr, runs=[wf_run(100, "pull_request", 1, 1, prs=(12, 99))]), "two pull requests share this head")


def test_s496_a_pull_request_run_that_names_no_pull_request_is_not_counted(env):
    pr = good()
    pr["statusCheckRollup"] = [row("gate", 100, "SUCCESS")]
    refused(*env(pr=pr, runs=[wf_run(100, "pull_request", 1, 1, prs=())]), "no required check")


def test_s496_a_red_row_of_another_event_still_refuses(env):
    """Second review of #513, point 1: only push and workflow_dispatch rows and replaced pull_request rows are dropped.
    A red row of a pull_request_target run counts as before this story."""
    pr = good()
    pr["statusCheckRollup"] = [row("gate", 100), row("security", 101, "FAILURE", "2026-11-13T11:00:00Z")]
    runs = [wf_run(100, "pull_request", 1, 1), wf_run(101, "pull_request_target", 2, 1, prs=())]
    refused(*env(pr=pr, runs=runs), "check security is not SUCCESS")


def test_s496_a_row_with_no_run_id_passes_through(env):
    pr = good()
    pr["statusCheckRollup"] = [row("gate", 100), {"name": "external", "status": "COMPLETED", "conclusion": "FAILURE"}]
    refused(*env(pr=pr, runs=[wf_run(100, "pull_request", 1, 1)]), "check external is not SUCCESS")


def test_s496_a_newest_run_with_no_rows_yet_leaves_no_gate_and_refuses(env):
    pr = good()
    pr["statusCheckRollup"] = [row("gate", 100)]
    runs = [wf_run(100, "pull_request", 1, 1), wf_run(102, "pull_request", 1, 3)]   # run 102 is queued: no rows yet
    refused(*env(pr=pr, runs=runs), "no required check")
