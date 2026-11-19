"""The shared loop of the story checks (#564 review point 4): the linked issues of a PR body, the user-story label, the rule date."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

GH = """#!/usr/bin/env bash
if [ "$1 $2" = "issue view" ]; then
  echo "$@" >> "$STUB_DIR/calls.txt"
  [ -f "$STUB_DIR/fail_$3" ] && { echo "boom" >&2; exit 1; }
  cat "$STUB_DIR/issue_$3.json"; exit 0
fi
exit 9
"""


@pytest.fixture
def gh(tmp_path, monkeypatch):
    stub = tmp_path / "stub"; stub.mkdir()
    (stub / "gh").write_text(GH, encoding="utf-8"); (stub / "gh").chmod(0o755)
    monkeypatch.setenv("PATH", f"{stub}:" + __import__("os").environ["PATH"])
    monkeypatch.setenv("STUB_DIR", str(stub))

    def issue(n, created, labels=("user-story",), body="b"):
        (stub / f"issue_{n}.json").write_text(json.dumps({"labels": [{"name": x} for x in labels], "body": body, "createdAt": created}), encoding="utf-8")
    issue.stub = stub
    return issue


def stories(body, rule="2026-11-19", **kw):
    import linked_stories
    return list(linked_stories.linked_stories(body, rule, **kw))


def test_a_new_user_story_is_yielded_with_its_issue_info(gh):
    gh(12, "2026-11-20T09:00:00Z", body="hello")
    got = stories("Closes #12\n")
    assert [n for n, _ in got] == ["12"] and got[0][1]["body"] == "hello"


def test_an_issue_without_the_user_story_label_is_skipped(gh):
    gh(12, "2026-11-20T09:00:00Z", labels=("bug",))
    assert stories("Closes #12\n") == []


def test_a_story_made_before_the_rule_date_is_skipped_and_the_skip_is_said(gh, capsys):
    gh(12, "2026-11-18T10:00:00Z")
    assert stories("Closes #12\n") == []
    assert "skip #12" in capsys.readouterr().out


def test_a_link_repeated_in_the_body_is_read_once(gh):
    gh(12, "2026-11-20T09:00:00Z")
    stories("Closes #12\nFixes #12\n")
    assert (gh.stub / "calls.txt").read_text().count("issue view 12") == 1


def test_the_json_fields_are_passed_to_gh(gh):
    gh(12, "2026-11-20T09:00:00Z")
    stories("Closes #12\n", fields="labels,body,createdAt,comments")
    assert "labels,body,createdAt,comments" in (gh.stub / "calls.txt").read_text()


def test_a_gh_failure_raises_a_story_read_error_naming_the_issue(gh):
    import linked_stories
    (gh.stub / "fail_12").write_text("x")
    with pytest.raises(linked_stories.StoryReadError) as e:
        stories("Closes #12\n")
    assert "#12" in str(e.value) and "boom" in str(e.value)


def test_a_body_with_no_link_yields_nothing(gh):
    assert stories("## What\nNo link.\n") == []
