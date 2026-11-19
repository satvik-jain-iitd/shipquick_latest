"""Story size gate (ADR-020): only XS and S may be planned; M, L, XL must be split first."""
import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_story_size.py"


def run(body, *args):
    return subprocess.run(["python3", str(SCRIPT), *args], input=body, capture_output=True, text=True)


@pytest.mark.parametrize("body", [
    "## Value\nRemove a kitchen.\n\nSize: XS\n",
    "## Value\nRemove a kitchen.\n\nSize: S\n",
    "### Size (T-shirt)\n\nXS\n",   # how a GitHub issue form renders the field
    "- **Size:** s\n",
])
def test_a_story_sized_xs_or_s_passes(body):
    r = run(body)
    assert r.returncode == 0 and "OK" in r.stdout, r.stdout


@pytest.mark.parametrize("body", [
    "## Value\nRemove a kitchen.\n",                                    # no line at all
    "Size:\n",                                                          # empty
    "Size: M\n",                                                        # too big
    "Size: L\n",
    "Size: XL\n",
    "### Size (T-shirt)\n\n_No response_\n",                            # issue form left blank
    "Size: Z\n",                                                        # unknown
])
def test_a_story_sized_m_l_xl_or_missing_fails_and_says_why(body):
    r = run(body)
    assert r.returncode == 1 and "Size" in r.stdout, r.stdout


def test_the_story_template_and_the_issue_form_both_carry_the_field():
    template = (ROOT / "pm" / "agile" / "templates" / "story.md").read_text(encoding="utf-8")
    form = (ROOT / ".github" / "ISSUE_TEMPLATE" / "user-story.yml").read_text(encoding="utf-8")
    assert "Size:" in template
    assert "label: \"Size (T-shirt)\"" in form


def test_ci_checks_every_linked_user_story_size():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "scripts/check_story_size.py --pr-body-file" in ci and "issues: read" in ci


def test_check_local_runs_the_size_check():
    text = (ROOT / "scripts" / "check_local.sh").read_text(encoding="utf-8")
    assert "check_story_size.py" in text and "story-size)" in text


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


def story_issue(created, size="M"):
    return {"labels": [{"name": "user-story"}], "body": f"## Value\nNo size line.\nSize: {size}\n", "createdAt": created}


@pytest.mark.parametrize("created,size,rc", [
    ("2026-11-18T10:00:00Z", "M", 0),   # before the rule: skipped
    ("2026-11-19T00:00:00Z", "XS", 0),
    ("2026-11-19T00:00:00Z", "S", 0),
    ("2026-11-19T00:00:00Z", "M", 1),
    ("2026-11-20T09:00:00Z", "L", 1),
])
def test_a_story_created_before_the_rule_is_skipped_with_one_line(tmp_path, created, size, rc):
    f = tmp_path / "body.md"; f.write_text("Closes #12\n", encoding="utf-8")
    r = subprocess.run(["python3", str(SCRIPT), "--pr-body-file", str(f)], capture_output=True, text=True, env=stub_env(tmp_path, story_issue(created, size)))
    assert r.returncode == rc, r.stdout
    if rc == 0 and created[:10] < "2026-11-19":
        assert "skip #12" in r.stdout and "before 2026-11-19" in r.stdout


def test_check_local_skips_the_size_check_when_gh_is_not_logged_in(tmp_path):
    repo = tmp_path / "repo"; repo.mkdir()
    git = lambda *a: subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)
    git("init", "-q", "-b", "dev"); git("config", "user.email", "t@example.com"); git("config", "user.name", "t")
    git("commit", "-q", "--allow-empty", "-m", "chore: base")
    git("update-ref", "refs/remotes/origin/dev", "HEAD")
    git("commit", "-q", "--allow-empty", "-m", "feat: x\n\nCloses #12")
    env = stub_env(tmp_path, story_issue("2026-11-20T09:00:00Z", "M"), no_auth=True)
    r = subprocess.run(["bash", str(ROOT / "scripts" / "check_local.sh"), "story-size"], cwd=repo, capture_output=True, text=True, env=env)
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "skip story-size: gh is not logged in" in r.stdout
