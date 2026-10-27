"""Story 2 of epic #97: CLAUDE.md holds the protocol only; project facts live in a template the child fills."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLAUDE = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
TEMPLATE = ROOT / "docs" / "CLAUDE.project.template.md"
POINTER = "follow knowledge/shipquick_latest/CLAUDE.md"


def test_protocol_has_no_project_facts():
    for n in (6, 9, 10):
        assert not re.search(rf"^{n}\. ", CLAUDE, re.M), f"rule {n} is a project fact"
    for word in ("Apple-silicon", "VAD", "models/", "Rosetta"):
        assert word not in CLAUDE, word


def test_protocol_says_where_project_facts_go_and_that_numbers_stay():
    assert "docs/CLAUDE.project.template.md" in CLAUDE
    assert "Rule numbers never change" in CLAUDE


def test_template_has_facts_sections_and_the_pointer_line():
    t = TEMPLATE.read_text(encoding="utf-8")
    assert t.count(POINTER) == 1
    for h in ("## Stack", "## Folders", "## Decisions"):
        assert h in t, h


def test_template_repeats_no_protocol_rule():
    t = TEMPLATE.read_text(encoding="utf-8")
    assert not re.search(r"^\d+\. ", t, re.M), "a numbered rule is a protocol rule: it belongs in CLAUDE.md"
