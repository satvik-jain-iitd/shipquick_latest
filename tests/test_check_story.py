"""Story #155: a story names who does it in real life (actor, app or screen, how often) before it is Ready.
The GoServe case: a kitchen-remove feature was built for the cook on the kitchen app, when the owner,
on the admin app, had the pain. Nothing in the story asked who."""
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_story.py"


def run(body, *args):
    return subprocess.run(["python3", str(SCRIPT), *args], input=body, capture_output=True, text=True)


@pytest.mark.parametrize("body", [
    "## Value\nRemove a kitchen.\n\nWho does it: the admin, on the admin app City screen, about twice a month\n",
    "### Who does it\n\nthe admin, admin app City screen, twice a month\n",   # how a GitHub issue form renders the field
    "- **Who does it:** the cook, kitchen app home, every morning\n",
])
def test_s155_a_story_with_actor_screen_and_how_often_passes(body):
    r = run(body)
    assert r.returncode == 0 and "OK" in r.stdout, r.stdout


@pytest.mark.parametrize("body", [
    "## Value\nRemove a kitchen.\n",                                    # no line at all
    "Who does it:\n",                                                  # empty
    "Who does it: <actor>, <app or screen>, <how often>\n",            # template placeholder left in
    "### Who does it\n\n_No response_\n",                              # issue form left blank
    "Who does it: the admin\n",                                        # actor only, no screen, no how often
    "Who does it: the admin, admin app\n",                             # no how often
])
def test_s155_a_story_without_a_full_who_does_it_line_fails_and_says_why(body):
    r = run(body)
    assert r.returncode == 1 and "Who does it" in r.stdout, r.stdout


def test_s155_the_story_template_and_the_issue_form_both_carry_the_field():
    template = (ROOT / "pm" / "agile" / "templates" / "story.md").read_text(encoding="utf-8")
    form = (ROOT / ".github" / "ISSUE_TEMPLATE" / "user-story.yml").read_text(encoding="utf-8")
    assert "Who does it:" in template
    assert "label: Who does it" in form and form.split("label: Who does it", 1)[1].split("- type:", 1)[0].count("required: true") == 1


def test_s155_ci_checks_every_linked_user_story_issue():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "scripts/check_story.py --pr-body-file" in ci and "issues: read" in ci


def test_s155_check_local_runs_the_story_check():
    text = (ROOT / "scripts" / "check_local.sh").read_text(encoding="utf-8")
    assert "check_story.py" in text and "story)" in text


def test_s155_pr_body_mode_skips_a_body_with_no_linked_issue(tmp_path):
    f = tmp_path / "body.md"
    f.write_text("## What\nNo link.\n", encoding="utf-8")
    r = run("", "--pr-body-file", str(f))
    assert r.returncode == 0, r.stdout


# ---- review of PR #168: older stories and a gh that is not logged in ----
import json
import os

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


@pytest.mark.parametrize("created,rc", [("2026-10-01T10:00:00Z", 0), ("2026-11-08T23:59:59Z", 0), ("2026-11-09T00:00:00Z", 1), ("2026-11-20T09:00:00Z", 1)])
def test_s155_a_story_created_before_the_rule_is_skipped_with_one_line(tmp_path, created, rc):
    f = tmp_path / "body.md"; f.write_text("Closes #12\n", encoding="utf-8")
    r = subprocess.run(["python3", str(SCRIPT), "--pr-body-file", str(f)], capture_output=True, text=True, env=stub_env(tmp_path, story_issue(created)))
    assert r.returncode == rc, r.stdout
    if rc == 0:
        assert "skip #12" in r.stdout and "before 2026-11-09" in r.stdout


def test_s155_check_local_skips_the_story_check_when_gh_is_not_logged_in(tmp_path):
    repo = tmp_path / "repo"; repo.mkdir()
    git = lambda *a: subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)
    git("init", "-q", "-b", "dev"); git("config", "user.email", "t@example.com"); git("config", "user.name", "t")
    git("commit", "-q", "--allow-empty", "-m", "chore: base")
    git("update-ref", "refs/remotes/origin/dev", "HEAD")
    git("commit", "-q", "--allow-empty", "-m", "feat: x\n\nCloses #12")
    env = stub_env(tmp_path, story_issue("2026-11-20T09:00:00Z"), no_auth=True)
    r = subprocess.run(["bash", str(ROOT / "scripts" / "check_local.sh"), "story"], cwd=repo, capture_output=True, text=True, env=env)
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "skip story: gh is not logged in" in r.stdout


# Story #194: an inline value that wraps onto the next line is read whole.
def test_s194_an_inline_value_that_crosses_a_line_break_is_read_whole():
    r = run("Who does it: the admin,\non the admin app City screen,\nabout twice a month\n\n## Scenarios\n")
    assert r.returncode == 0, r.stdout
