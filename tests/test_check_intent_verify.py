"""Intent-verification gate (ADR-021). The proof is an issue comment, `Intent verified by QA: YYYY-MM-DD`, from a login
that is not the PR author. The PR body never counts: the coder writes it."""
import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_intent_verify.py"
PROOF = "Intent verified by QA: 2026-11-19"


STUB = """#!/usr/bin/env bash
case "$1 $2" in
  "auth status") [ -n "${STUB_NO_AUTH:-}" ] && { echo "You are not logged into any GitHub hosts. Run gh auth login" >&2; exit 1; }; exit 0 ;;
  "issue view") cat "$STUB_DIR/issue.json"; exit 0 ;;
  "api user") echo "${STUB_LOGIN:-dev-login}"; exit 0 ;;
esac
exit 9
"""


def stub_env(tmp_path, issue=None, no_auth=False):
    stub = tmp_path / "stub"; stub.mkdir(exist_ok=True)
    (stub / "gh").write_text(STUB, encoding="utf-8"); (stub / "gh").chmod(0o755)
    if issue is not None:
        (stub / "issue.json").write_text(json.dumps(issue), encoding="utf-8")
    return {**os.environ, "PATH": f"{stub}:{os.environ['PATH']}", "STUB_DIR": str(stub), "STUB_NO_AUTH": "1" if no_auth else ""}


def comment(login, body):
    return {"author": {"login": login}, "body": body}


def story_issue(created="2026-11-20T09:00:00Z", comments=()):
    return {"labels": [{"name": "user-story"}], "body": "## Value\nNo actor line.\n", "createdAt": created, "comments": list(comments)}


def run_pr(tmp_path, issue, author="dev-login", body="Closes #12\n## What\nFix.\n"):
    f = tmp_path / "body.md"
    f.write_text(body, encoding="utf-8")
    env = stub_env(tmp_path, issue)
    if author is None:
        env.pop("PR_AUTHOR", None)
    else:
        env["PR_AUTHOR"] = author
    return subprocess.run(["python3", str(SCRIPT), "--pr-body-file", str(f)], capture_output=True, text=True, env=env)


def test_a_proof_comment_from_another_login_passes(tmp_path):
    r = run_pr(tmp_path, story_issue(comments=[comment("qa-login", PROOF)]))
    assert r.returncode == 0 and "intent OK" in r.stdout, r.stdout


def test_a_proof_comment_by_the_pr_author_does_not_count(tmp_path):
    r = run_pr(tmp_path, story_issue(comments=[comment("dev-login", PROOF)]))
    assert r.returncode == 1 and "no comment" in r.stdout, r.stdout


def test_the_author_match_ignores_case(tmp_path):
    r = run_pr(tmp_path, story_issue(comments=[comment("Dev-Login", PROOF)]), author="dev-login")
    assert r.returncode == 1, r.stdout


def test_a_line_in_the_pr_body_alone_does_not_count(tmp_path):
    r = run_pr(tmp_path, story_issue(comments=[]), body=f"Closes #12\n{PROOF}\n")
    assert r.returncode == 1 and "no comment" in r.stdout, r.stdout


def test_a_story_with_no_comment_at_all_fails(tmp_path):
    r = run_pr(tmp_path, story_issue(comments=[]))
    assert r.returncode == 1, r.stdout


def test_a_comment_without_a_date_does_not_count(tmp_path):
    r = run_pr(tmp_path, story_issue(comments=[comment("qa-login", "Intent verified by QA: yes")]))
    assert r.returncode == 1, r.stdout


def test_an_empty_pr_author_fails_with_a_clear_line_even_with_a_proof_comment(tmp_path):
    r = run_pr(tmp_path, story_issue(comments=[comment("qa-login", PROOF)]), author="")
    assert r.returncode == 1 and "PR_AUTHOR" in r.stdout, r.stdout


def test_a_missing_pr_author_fails_with_a_clear_line(tmp_path):
    r = run_pr(tmp_path, story_issue(comments=[comment("qa-login", PROOF)]), author=None)
    assert r.returncode == 1 and "PR_AUTHOR" in r.stdout, r.stdout


@pytest.mark.parametrize("created,has_proof,rc", [
    ("2026-11-18T10:00:00Z", False, 0),   # before the rule: skipped
    ("2026-11-19T00:00:00Z", True, 0),    # on/after the rule with a proof comment from another login: passes
    ("2026-11-20T09:00:00Z", False, 1),   # on/after the rule without a proof comment: fails
])
def test_a_story_created_before_the_rule_is_skipped(tmp_path, created, has_proof, rc):
    comments = [comment("qa-login", PROOF)] if has_proof else []
    r = run_pr(tmp_path, story_issue(created, comments))
    assert r.returncode == rc, r.stdout


def test_pr_body_mode_skips_a_body_with_no_linked_issue(tmp_path):
    r = run_pr(tmp_path, None, body="## What\nNo link.\n")
    assert r.returncode == 0, r.stdout


# ---- fix 2 (#523 review): the local check judges the same proof as CI ----
def local_repo(tmp_path, message="feat: x\n\nCloses #12"):
    repo = tmp_path / "repo"; repo.mkdir()
    git = lambda *a: subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)
    git("init", "-q", "-b", "dev"); git("config", "user.email", "t@example.com"); git("config", "user.name", "t")
    git("commit", "-q", "--allow-empty", "-m", "chore: base")
    git("update-ref", "refs/remotes/origin/dev", "HEAD")
    git("commit", "-q", "--allow-empty", "-m", message)
    return repo


def run_local(tmp_path, repo, issue, login="dev-login"):
    env = stub_env(tmp_path, issue)
    env["STUB_LOGIN"] = login
    return subprocess.run(["bash", str(ROOT / "scripts" / "check_local.sh"), "intent-verify"], cwd=repo, capture_output=True, text=True, env=env)


def test_local_passes_on_a_proof_comment_from_another_login(tmp_path):
    r = run_local(tmp_path, local_repo(tmp_path), story_issue(comments=[comment("qa-login", PROOF)]), login="dev-login")
    assert r.returncode == 0 and "intent OK" in r.stdout, (r.stdout, r.stderr)


def test_local_fails_on_a_proof_comment_from_the_logged_in_author(tmp_path):
    r = run_local(tmp_path, local_repo(tmp_path), story_issue(comments=[comment("dev-login", PROOF)]), login="dev-login")
    assert r.returncode != 0 and "no comment" in r.stdout, (r.stdout, r.stderr)


def test_local_fails_on_a_linked_new_story_with_no_proof_comment(tmp_path):
    r = run_local(tmp_path, local_repo(tmp_path), story_issue(comments=[]), login="dev-login")
    assert r.returncode != 0, (r.stdout, r.stderr)
    assert "no comment" in r.stdout, r.stdout


# ---- fix 3 (#523 review): no doc line promises an `Intent:` block field that no check or example backs ----
def test_the_intent_field_is_not_promised_in_the_protocol_or_the_adr():
    for rel in ("docs/TEAM_PROTOCOL.md", "docs/decisions/ADR-021.md"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "`Intent:`" not in text and "Intent:` field" not in text, f"{rel} still promises an Intent: field"


# ---- fix 4 (#523 review): ADR-021 says who types the confirmation and what is still not stopped ----
def adr_last_section():
    text = (ROOT / "docs" / "decisions" / "ADR-021.md").read_text(encoding="utf-8")
    return text.split("## What this does not stop", 1)[1]


def test_the_adr_says_qa_types_the_confirmation_on_the_issue_not_dev_in_the_body():
    section = adr_last_section()
    assert "recorded by Dev" not in section and "Owner yes" not in section
    assert "QA" in section and "comment" in section and "not the PR author" in section


def test_the_adr_says_what_is_still_not_stopped():
    assert "does not read the say-back" in adr_last_section()


# ---- #555 qa review, point 1: no stale "PR body" proof text left in the docs ----
STALE_DOCS = ("docs/decisions/ADR-021.md", "docs/TEAM_ROSTER.md", "docs/TEAM_PROTOCOL.md")


@pytest.mark.parametrize("rel", STALE_DOCS)
def test_no_doc_says_the_proof_is_recorded_in_the_pr_body(rel):
    text = (ROOT / rel).read_text(encoding="utf-8")
    for stale in ("recorded in the PR body", "PR body carries the confirmation", "Dev that types a confirmation QA never gave passes"):
        assert stale not in text, f"{rel} still says: {stale!r}"


def test_the_adr_names_that_a_login_with_write_access_can_edit_a_comment():
    assert "edit" in adr_last_section() and "write access" in adr_last_section()


# ---- #555 qa review, point 2: the local skip when gh is not logged in is tested again ----
def test_check_local_skips_the_intent_check_when_gh_is_not_logged_in(tmp_path):
    repo = local_repo(tmp_path)
    env = stub_env(tmp_path, story_issue(comments=[]), no_auth=True)
    r = subprocess.run(["bash", str(ROOT / "scripts" / "check_local.sh"), "intent-verify"], cwd=repo, capture_output=True, text=True, env=env)
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "skip intent-verify: gh is not logged in" in r.stdout
