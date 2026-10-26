"""S0.14: parallel stories with few merge conflicts (story #59). Real git in a throwaway repo; text checks for the rules."""
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
LOGS = ("docs/process-trace.md", "docs/LEARNINGS.md")   # only logs whose rows are never edited; ideas.md rows get status edits, so it is not on the list


def git(cwd, *args, check=True):
    return subprocess.run(["git", *args], cwd=cwd, check=check, capture_output=True, text=True)


def two_branches(tmp_path, log, with_attributes, number="2"):
    """A repo with a table log; branch a and branch b each append one row at the end. Returns the repo after `git merge b` on a."""
    git(tmp_path, "init", "-q", "-b", "dev")
    git(tmp_path, "config", "user.email", "t@example.com")
    git(tmp_path, "config", "user.name", "T")
    path = tmp_path / log
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# Log\n\n| # | Actor | Step |\n|---|---|---|\n| 1 | coder | start |\n", encoding="utf-8")
    if with_attributes:
        shutil.copy(ROOT / ".gitattributes", tmp_path / ".gitattributes")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-q", "-m", "docs: base")
    for name in ("a", "b"):
        git(tmp_path, "checkout", "-q", "-b", name, "dev")
        with path.open("a", encoding="utf-8") as f:
            f.write(f"| {number} | coder-{name} | story {name} |\n")
        git(tmp_path, "commit", "-qam", f"docs: row {name}")
    git(tmp_path, "checkout", "-q", "a")
    return git(tmp_path, "merge", "--no-edit", "b", check=False)


@pytest.mark.parametrize("log", LOGS)
def test_s14_two_branches_that_each_add_a_row_merge_with_no_conflict(tmp_path, log):
    result = two_branches(tmp_path, log, with_attributes=True)
    assert result.returncode == 0, result.stdout + result.stderr
    text = (tmp_path / log).read_text(encoding="utf-8")
    assert "coder-a" in text and "coder-b" in text and "<<<<<<<" not in text


def test_s14_without_the_attribute_the_same_two_branches_do_conflict(tmp_path):
    """The control: this is why the file exists. If git ever stops conflicting here, the test above proves nothing."""
    result = two_branches(tmp_path, "docs/process-trace.md", with_attributes=False)
    assert result.returncode != 0 and "CONFLICT" in result.stdout


def test_s14_gitattributes_lists_exactly_the_append_only_logs_and_not_the_changelog():
    lines = [l.split() for l in (ROOT / ".gitattributes").read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    assert sorted(p for p, attr in lines if attr == "merge=union") == sorted(LOGS)
    assert "CHANGELOG.md" not in [p for p, _ in lines]   # only the release PR edits it, and a union merge would hide a real conflict there
    assert "docs/ideas.md" not in [p for p, _ in lines]  # a status edit on one row, made on two branches, would be kept twice with no conflict shown


def test_s14_every_log_ends_with_a_newline_so_a_union_merge_never_joins_two_rows():
    for log in LOGS:
        assert (ROOT / log).read_text(encoding="utf-8").endswith("\n"), log


CLAUDE = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
RULE23 = re.search(r"^23\. (.+)$", CLAUDE, re.M).group(1)


def test_s14_rule_23_allows_up_to_three_stacks_in_separate_lanes_and_asks_for_a_daily_merge_of_dev():
    assert "One stack open at a time" not in RULE23
    assert "up to 3" in RULE23 and "lane" in RULE23
    assert re.search(r"merge `dev` into every open branch once a day", RULE23)
    assert re.search(r"right before the merge, merge `dev` once more with Git on the Mac if `dev` moved", RULE23)
    assert "`docs/process-trace.md`, `docs/LEARNINGS.md`)" in RULE23 and "`docs/LEARNINGS.md`, `docs/ideas.md`" not in RULE23   # ideas.md is not an append-only log
    assert "pm/agile/templates/sprint-lanes.md" in RULE23


def test_s14_the_sprint_lane_template_asks_for_files_per_story_and_a_foundation_first():
    text = (ROOT / "pm" / "agile" / "templates" / "sprint-lanes.md").read_text(encoding="utf-8")
    for needle in ("Lane", "Files touched", "Foundation", "overlap"):
        assert needle in text, needle


def test_s14_the_release_guide_uses_a_release_branch_and_a_back_merge():
    text = (ROOT / "pm" / "agile" / "RELEASE_GUIDE.md").read_text(encoding="utf-8")
    assert "release/vX.Y.Z" in text and "back-merge" in text and "merge commit" in text.lower()
    assert "Any merge method works" in text   # step 1 put main in the branch, so the release never hangs on the owner's choice of button
    assert re.search(r"Optional\. Step 1 of the next release covers it", text)


def test_s14_the_roster_has_one_reviewer_and_up_to_three_coders_each_with_a_worktree():
    text = (ROOT / "docs" / "TEAM_ROSTER.md").read_text(encoding="utf-8")
    assert "up to 3 coder" in text and "worktree" in text


def test_s14_two_branches_that_each_add_a_dash_row_merge_with_no_conflict_and_keep_both_rows(tmp_path):
    """Rows without a number (a dash in the # column) cannot collide on a number; both rows stay."""
    result = two_branches(tmp_path, "docs/process-trace.md", with_attributes=True, number="-")
    assert result.returncode == 0, result.stdout + result.stderr
    text = (tmp_path / "docs/process-trace.md").read_text(encoding="utf-8")
    assert text.count("| - |") == 2 and "<<<<<<<" not in text


def test_s14_rule_1_and_the_trace_header_say_a_new_row_writes_a_dash_in_the_number_column():
    rule1 = re.search(r"^1\. (.+)$", CLAUDE, re.M).group(1)
    assert "`-` in the `#` column" in rule1
    header = (ROOT / "docs" / "process-trace.md").read_text(encoding="utf-8").split("| # |", 1)[0]
    assert "`-` in the `#` column" in header


def test_s14_the_first_merge_trick_is_in_the_lane_template_and_the_child_steps():
    for path in ("pm/agile/templates/sprint-lanes.md", "docs/TEAM_PROTOCOL.md"):
        text = (ROOT / path).read_text(encoding="utf-8")
        assert ".git/info/attributes" in text, path
