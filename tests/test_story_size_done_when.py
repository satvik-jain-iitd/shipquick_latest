"""Story #310 (A0, epic #309): a user story carries a runnable `Done when:` line, and size:M, size:L or size:XL
gets a warning. Stories created before 2026-11-10 are skipped, the same way story #155 skipped older ones."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_story.py"
sys.path.insert(0, str(ROOT / "scripts"))
import check_story as cs  # noqa: E402

WHO = "Who does it: the coder (Haiku), the desk page, once per story PR"


def test_a_story_with_an_inline_done_when_passes():
    assert cs.check_done_when(f"{WHO}\n\nDone when: `python3 -m unittest tests.test_desk` is green.\n") is None


def test_a_story_with_a_done_when_heading_and_a_line_passes():
    assert cs.check_done_when(f"{WHO}\n\n## Done when\nThe page answers 200 on /.\n") is None


def test_a_story_with_an_empty_done_when_heading_fails():
    why = cs.check_done_when(f"{WHO}\n\n## Done when\n\n## Scenarios\n- x\n")
    assert why and "Done when" in why


def test_a_story_with_no_done_when_line_fails_and_says_the_shape():
    why = cs.check_done_when(f"{WHO}\n\n## Story\nAs the owner.\n")
    assert why and "Done when:" in why


def test_size_m_l_and_xl_get_a_warning_and_xs_and_s_do_not():
    assert cs.size_warning(["user-story", "size:M"]) and "size:M" in cs.size_warning(["size:M"])
    assert cs.size_warning(["size:L"]) and cs.size_warning(["size:XL"])
    assert cs.size_warning(["size:XS"]) is None and cs.size_warning(["size:S"]) is None
    assert cs.size_warning(["user-story"]) is None


STUB = """#!/usr/bin/env bash
case "$1 $2" in
  "auth status") exit 0 ;;
  "issue view") cat "$STUB_DIR/issue.json"; exit 0 ;;
esac
exit 9
"""


def run_pr(tmp_path, issue):
    stub = tmp_path / "stub"
    stub.mkdir()
    (stub / "gh").write_text(STUB, encoding="utf-8")
    (stub / "gh").chmod(0o755)
    (stub / "issue.json").write_text(json.dumps(issue), encoding="utf-8")
    body = tmp_path / "body.md"
    body.write_text("Closes #12\n", encoding="utf-8")
    env = {**os.environ, "PATH": f"{stub}:{os.environ['PATH']}", "STUB_DIR": str(stub)}
    return subprocess.run(["python3", str(SCRIPT), "--pr-body-file", str(body)], capture_output=True, text=True, env=env)


def story(created, labels=("user-story", "size:XS"), body=None):
    return {"labels": [{"name": n} for n in labels], "createdAt": created,
            "body": body if body is not None else f"{WHO}\n\nDone when: `make test` passes.\n"}


def test_a_new_story_with_no_done_when_fails_the_pr_check(tmp_path):
    r = run_pr(tmp_path, story("2026-11-10T12:00:00Z", body=f"{WHO}\n\n## Story\nx\n"))
    assert r.returncode == 1 and "Done when" in r.stdout, r.stdout


def test_a_story_from_before_today_with_no_done_when_is_skipped_not_failed(tmp_path):
    r = run_pr(tmp_path, story("2026-11-09T23:00:00Z", body=f"{WHO}\n\n## Story\nx\n"))
    assert r.returncode == 0 and "Done when" not in r.stdout, r.stdout


def test_a_size_m_story_with_a_done_when_passes_with_a_warning(tmp_path):
    r = run_pr(tmp_path, story("2026-11-10T12:00:00Z", labels=("user-story", "size:M")))
    assert r.returncode == 0 and "warn: #12 size:M" in r.stdout and "story OK" in r.stdout, r.stdout


def test_the_brief_template_carries_done_when_and_the_untrusted_rule():
    t = (ROOT / "docs" / "templates" / "subagent-brief.md").read_text(encoding="utf-8")
    assert "Done when:" in t and "untrusted" in t.lower()


def test_claude_md_rule_18_says_xs_or_s_only():
    rules = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    line = next(l for l in rules.splitlines() if l.startswith("18. "))
    assert "XS, S" in line or "XS or S" in line


# review of #329 (qa): an empty Done when line must not read the next heading, and placeholders are no answer
def test_an_empty_inline_done_when_followed_by_a_heading_fails():
    why = cs.check_done_when(f"{WHO}\n\nDone when:\n\n## Scenarios\n- x\n")
    assert why and "Done when" in why


def test_a_placeholder_or_no_response_under_the_heading_fails():
    assert cs.check_done_when(f"{WHO}\n\n## Done when\n_No response_\n")
    assert cs.check_done_when(f"{WHO}\n\n## Done when\n<one runnable condition>\n")


def test_a_placeholder_or_no_response_inline_fails():
    assert cs.check_done_when(f"{WHO}\n\nDone when: _No response_\n")
    assert cs.check_done_when(f"{WHO}\n\nDone when: <one runnable condition>\n")


def test_the_story_form_has_a_required_done_when_field():
    form = (ROOT / ".github" / "ISSUE_TEMPLATE" / "user-story.yml").read_text(encoding="utf-8")
    block = form.split("label: Done when", 1)
    assert len(block) == 2, "no Done when field in the story form"
    assert "required: true" in block[1].split("- type:", 1)[0]


def test_claude_md_rule_18_carries_the_qa_split_and_the_reviewer_rerun():
    rules = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    line = next(l for l in rules.splitlines() if l.startswith("18. "))
    assert "The QA session breaks work down; the coder runs on Haiku for XS and S" in line
    assert "the reviewer reruns the Done when line before merge" in line


# review of #329 (qa): a bold label with no value must not take a `*` from the markup as the value
def test_a_bold_done_when_with_no_value_before_a_heading_fails():
    assert cs.check_done_when("**Done when:**\r\n\r\n## Notes\r\nfoo")


def test_a_bold_done_when_with_a_value_passes():
    assert cs.check_done_when(f"{WHO}\n\n**Done when:** make test passes\n") is None
