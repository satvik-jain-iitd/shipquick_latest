"""A13 (story #328): the path-scoped rules spike is written down with its source URL (docs finding, no rule moved)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_URL = "https://code.claude.com/docs/en/memory"
EXPERIMENTS = (ROOT / "docs" / "research" / "experiments.md").read_text(encoding="utf-8")
STUDY = (ROOT / "docs" / "research" / "2026-11-10-ponytail-ecc-study.md").read_text(encoding="utf-8")


def _rows(text):
    return [line for line in text.splitlines() if line.startswith("| 2026-11-10 |")]


def test_a13_experiments_row_exists_with_docs_url():
    rows = [r for r in _rows(EXPERIMENTS) if "rules" in r.lower() and "paths" in r.lower()]
    assert rows, "no 2026-11-10 experiments row about path-scoped rules (#328)"
    row = rows[0]
    assert DOCS_URL in row, "the experiments row must cite the Claude Code docs URL"
    assert "pending test" in row.lower(), "the row must say its status is pending test"
    assert "#328" in row, "the row must name story #328"


def test_a13_study_adapt_row_cites_the_docs_url():
    rows = [line for line in STUDY.splitlines() if line.startswith("| Rules split by path")]
    assert rows, "the Adapt table row for #328 is missing"
    assert DOCS_URL in rows[0], "the #328 Adapt row must cite the Claude Code docs URL"
