"""Story #118: feedback.sh takes a body file that tells the whole story in nine required sections
(story #111's one-line form is gone, no second way). The script fills the header itself (project,
ShipQuick commit, date) — the caller never writes it. A missing or empty section, or fewer than three
"Why" lines in section 5 (root cause), exits 2 naming it and opens nothing. A similar open `feedback`
issue gets a comment instead of a new issue, unless --new. No login prints the title and the full body
and exits 1, nothing lost."""
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "feedback.sh"
REPO = "satvik-jain-iitd/shipquick_latest"

SECTIONS = [
    "Situation", "Expected vs seen", "Steps to reproduce", "Impact", "Root cause",
    "Why ShipQuick did not catch it", "How big teams avoid it", "Generic fix for ShipQuick", "Stop the repeat",
]
ROOT_CAUSE_IDX = SECTIONS.index("Root cause")

STUB_OK_NO_DUPES = """#!/usr/bin/env bash
echo "$*" >> "$STUB_DIR/calls.log"
case "$1" in
  auth) [ "$2" = token ] && { echo "tok-$4"; exit 0; } ;;
  issue) case "$2" in
      create) printf '%s\\0' "$@" >> "$STUB_DIR/issue.log"; exit 0 ;;
      comment) printf '%s\\0' "$@" >> "$STUB_DIR/comment.log"; exit 0 ;;
      list) echo "[]"; exit 0 ;;
    esac ;;
esac
exit 9
"""

STUB_ONE_DUPE = """#!/usr/bin/env bash
echo "$*" >> "$STUB_DIR/calls.log"
case "$1" in
  auth) [ "$2" = token ] && { echo "tok-$4"; exit 0; } ;;
  issue) case "$2" in
      create) printf '%s\\0' "$@" >> "$STUB_DIR/issue.log"; exit 0 ;;
      comment) printf '%s\\0' "$@" >> "$STUB_DIR/comment.log"; exit 0 ;;
      list) echo '[{"number": 99, "title": "feedback: job-search: model_calls.sh is slow"}]'; exit 0 ;;
    esac ;;
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


def filled_body(**overrides):
    parts = []
    for s in SECTIONS:
        if s == "Root cause":
            text = overrides.get(s, "Why 1: it broke.\nWhy 2: the check was missing.\nWhy 3: nobody wrote it.\n")
        else:
            text = overrides.get(s, f"{s} text here, more than nothing.")
        parts.append(f"## {s}\n\n{text}\n")
    return "\n".join(parts)


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


def run(child, tmp_path, script, *args, env_extra=None):
    d = stub(tmp_path, script)
    env = {**os.environ, "PATH": f"{d}:{os.environ['PATH']}", "STUB_DIR": str(d), **(env_extra or {})}
    r = subprocess.run(["bash", str(SCRIPT), *args], cwd=child, capture_output=True, text=True, env=env)
    r.issue = (d / "issue.log").read_text(encoding="utf-8") if (d / "issue.log").exists() else ""
    r.comment = (d / "comment.log").read_text(encoding="utf-8") if (d / "comment.log").exists() else ""
    return r


def body_file(tmp_path, text, name="body.md"):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


def test_s118_a_fully_filled_body_opens_a_labelled_issue_with_a_header_and_the_project_name(child, tmp_path):
    f = body_file(tmp_path, filled_body())
    r = run(child, tmp_path, STUB_OK_NO_DUPES, "--title", "model_calls.sh is slow", "--body-file", str(f))
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert f"-R\x00{REPO}" in r.issue
    assert "--label\x00feedback" in r.issue
    assert "job-search" in r.issue
    assert "Why 3: nobody wrote it" in r.issue
    assert "model_calls.sh is slow" in r.issue
    assert r.comment == ""


@pytest.mark.parametrize("missing", SECTIONS)
def test_s118_a_missing_section_exits_2_and_names_it_opens_nothing(child, tmp_path, missing):
    parts = []
    for s in SECTIONS:
        if s == missing:
            continue
        text = "Why 1: a.\nWhy 2: b.\nWhy 3: c.\n" if s == "Root cause" else f"{s} text here.\n"
        parts.append(f"## {s}\n\n{text}")
    f = body_file(tmp_path, "\n".join(parts))
    r = run(child, tmp_path, STUB_OK_NO_DUPES, "--title", "t", "--body-file", str(f))
    assert r.returncode == 2 and missing in r.stderr
    assert r.issue == "" and r.comment == ""


@pytest.mark.parametrize("empty", SECTIONS)
def test_s118_an_empty_section_exits_2_and_names_it_opens_nothing(child, tmp_path, empty):
    f = body_file(tmp_path, filled_body(**{empty: "   \n"}))
    r = run(child, tmp_path, STUB_OK_NO_DUPES, "--title", "t", "--body-file", str(f))
    assert r.returncode == 2 and empty in r.stderr
    assert r.issue == "" and r.comment == ""


@pytest.mark.parametrize("whys", ["Why 1: a.\n", "Why 1: a.\nWhy 2: b.\n", "Not a why line.\nAlso not.\nStill not.\n"])
def test_s118_fewer_than_three_why_lines_in_root_cause_exits_2(child, tmp_path, whys):
    f = body_file(tmp_path, filled_body(**{"Root cause": whys}))
    r = run(child, tmp_path, STUB_OK_NO_DUPES, "--title", "t", "--body-file", str(f))
    assert r.returncode == 2 and "Root cause" in r.stderr
    assert r.issue == ""


def test_s118_a_similar_open_feedback_issue_gets_a_comment_instead_of_a_new_issue(child, tmp_path):
    f = body_file(tmp_path, filled_body())
    r = run(child, tmp_path, STUB_ONE_DUPE, "--title", "model_calls.sh is slow", "--body-file", str(f))
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert r.issue == "", "no new issue when a similar one is already open"
    assert "99" in r.comment
    assert "99" in r.stdout


def test_s118_new_flag_forces_a_new_issue_even_with_a_duplicate(child, tmp_path):
    f = body_file(tmp_path, filled_body())
    r = run(child, tmp_path, STUB_ONE_DUPE, "--title", "model_calls.sh is slow", "--body-file", str(f), "--new")
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert r.issue != "" and r.comment == ""


def test_s118_no_login_prints_the_title_and_full_body_and_exits_1_nothing_lost(child, tmp_path):
    f = body_file(tmp_path, filled_body())
    r = run(child, tmp_path, STUB_NO_LOGIN, "--title", "the title", "--body-file", str(f))
    assert r.returncode == 1
    assert "the title" in r.stderr
    assert "Why 3: nobody wrote it" in r.stderr
    assert r.issue == "" and r.comment == ""


def test_s118_the_old_one_line_form_is_gone_no_second_way(child, tmp_path):
    r = run(child, tmp_path, STUB_OK_NO_DUPES, "one line", "--why", "because")
    assert r.returncode == 2
    assert "usage" in r.stderr.lower()
    assert r.issue == ""


def test_s118_the_template_and_issue_form_carry_the_same_nine_sections():
    template = (ROOT / "docs" / "templates" / "feedback.md").read_text(encoding="utf-8")
    for s in SECTIONS:
        assert f"## {s}" in template, s
    form = (ROOT / ".github" / "ISSUE_TEMPLATE" / "feedback.yml").read_text(encoding="utf-8")
    for s in SECTIONS:
        assert f"label: {s}" in form, s
    assert form.count("required: true") >= len(SECTIONS)


def test_s118_shipquick_repo_and_build_user_env_overrides(child, tmp_path):
    f = body_file(tmp_path, filled_body())
    r = run(child, tmp_path, STUB_OK_NO_DUPES, "--title", "t", "--body-file", str(f),
            env_extra={"SHIPQUICK_REPO": "someone/fork", "SHIPQUICK_BUILD_USER": "forkbot"})
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "-R\x00someone/fork" in r.issue
    assert f"-R\x00{REPO}" not in r.issue


def test_s118_the_header_carries_the_project_name_and_the_shipquick_commit(child, tmp_path):
    f = body_file(tmp_path, filled_body())
    r = run(child, tmp_path, STUB_OK_NO_DUPES, "--title", "t", "--body-file", str(f))
    assert r.returncode == 0, (r.stdout, r.stderr)
    sha = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    assert "job-search" in r.issue
    assert sha[:7] in r.issue


# ---- PR #119 review blocker: the unfilled template must not pass (hints and "Why n: ..." placeholders are not content) ----
def test_s119_the_unfilled_template_itself_is_refused(child, tmp_path):
    r = run(child, tmp_path, STUB_OK_NO_DUPES, "--title", "unfilled template", "--body-file", str(ROOT / "docs" / "templates" / "feedback.md"))
    assert r.returncode == 2, (r.stdout, r.stderr)
    assert r.issue == ""


def test_s119_why_n_dot_dot_dot_placeholder_lines_do_not_count_as_why_lines(child, tmp_path):
    f = body_file(tmp_path, filled_body(**{"Root cause": "Why 1: ...\nWhy 2: ...\nWhy 3: ...\nOne real sentence that is not a Why line.\n"}))
    r = run(child, tmp_path, STUB_OK_NO_DUPES, "--title", "t", "--body-file", str(f))
    assert r.returncode == 2 and "Root cause" in r.stderr
    assert r.issue == ""


def test_s119_a_section_still_equal_to_the_template_hint_is_refused_even_with_other_sections_filled(child, tmp_path):
    hint = "Project, tool and version, what you were doing, the ids (PR, issue, run), the exact error text."
    f = body_file(tmp_path, filled_body(**{"Situation": hint}))
    r = run(child, tmp_path, STUB_OK_NO_DUPES, "--title", "t", "--body-file", str(f))
    assert r.returncode == 2 and "Situation" in r.stderr
    assert r.issue == ""


# ---- PR #119 review nit: duplicate match must not let a short title swallow an unrelated long one ----
def test_s119_a_short_title_does_not_match_an_unrelated_long_existing_title(child, tmp_path):
    stub = STUB_ONE_DUPE.replace("model_calls.sh is slow", "the ci pipeline double-runs tests on reopen")
    f = body_file(tmp_path, filled_body())
    r = run(child, tmp_path, stub, "--title", "ci", "--body-file", str(f))
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert r.comment == "", "a 1-word title must not be treated as matching a long unrelated title"
    assert r.issue != ""


def test_s119_a_normalised_whole_title_match_is_still_caught(child, tmp_path):
    f = body_file(tmp_path, filled_body())
    r = run(child, tmp_path, STUB_ONE_DUPE, "--title", "MODEL_CALLS.SH is slow!!", "--body-file", str(f))
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert r.comment != "" and r.issue == ""


# ---- story #140 (reviewer): BUILD_USER defaults to the calling repo's own first coder account ----
def test_build_user_defaults_to_the_callers_first_coder_account(child, tmp_path):
    (child / ".shipquick").mkdir()
    (child / ".shipquick" / "roles.yml").write_text("coder:\n  - repo-coder\n  - repo-coder-2\nreviewer:\n  - repo-reviewer\nowner: repo-reviewer\n", encoding="utf-8")
    f = body_file(tmp_path, filled_body())
    r = run(child, tmp_path, STUB_OK_NO_DUPES, "--title", "model_calls.sh is slow", "--body-file", str(f))
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "auth token --user repo-coder" in (Path(tmp_path / "stub" / "calls.log").read_text(encoding="utf-8"))


def test_shipquick_build_user_env_var_overrides_roles_yml(child, tmp_path):
    (child / ".shipquick").mkdir()
    (child / ".shipquick" / "roles.yml").write_text("coder:\n  - repo-coder\nreviewer:\n  - repo-reviewer\nowner: repo-reviewer\n", encoding="utf-8")
    f = body_file(tmp_path, filled_body())
    r = run(child, tmp_path, STUB_OK_NO_DUPES, "--title", "model_calls.sh is slow", "--body-file", str(f), env_extra={"SHIPQUICK_BUILD_USER": "override-acct"})
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "auth token --user override-acct" in (Path(tmp_path / "stub" / "calls.log").read_text(encoding="utf-8"))


def test_with_no_roles_yml_the_old_literal_default_is_unchanged(child, tmp_path):
    f = body_file(tmp_path, filled_body())
    r = run(child, tmp_path, STUB_OK_NO_DUPES, "--title", "model_calls.sh is slow", "--body-file", str(f))
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "auth token --user klickbae8yt-star" in (Path(tmp_path / "stub" / "calls.log").read_text(encoding="utf-8"))
