"""Story #96: the roles are explicit in the source. The coder opens every PR, the reviewer never does,
and auto mode lets the reviewer merge dev to main."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read(rel):
    return (ROOT / rel).read_text()


def rule(n):
    m = re.search(rf"^{n}\. .*$", read("CLAUDE.md"), re.M)
    assert m, f"CLAUDE.md has no rule {n}"
    return m.group(0)


def test_rule_4_coder_opens_every_pr_including_dev_to_main():
    r = rule(4)
    assert "coder opens every PR" in r and "dev -> main" in r
    assert "reviewer never opens" in r


def test_rule_4_main_merge_depends_on_mode():
    r = rule(4)
    assert "manual and semi" in r and "auto" in r and "review_merge.sh" in r
    assert "the owner merges main." not in r  # the old unconditional sentence


def test_rule_27_names_the_roles():
    assert "reviewer never opens a PR" in rule(27)


def test_roster_and_pr_rules_state_the_roles():
    assert "reviewer never opens" in read("docs/TEAM_ROSTER.md")
    pr = read("docs/PR_RULES.md")
    assert "The coder opens every PR" in pr
    assert "The reviewer never opens" in pr


def test_modes_auto_row_merges_dev_to_main():
    row = next(l for l in read("docs/MODES.md").splitlines() if l.startswith("| Auto"))
    assert "dev to main" in row
    assert "pending owner yes" in read("docs/MODES.md")


def test_pr_rules_auto_merge_section_not_owner_only_in_auto():
    sec = read("docs/PR_RULES.md").split("## 8. Auto-merge")[1].split("## 9.")[0]
    assert "auto mode" in sec.lower()
