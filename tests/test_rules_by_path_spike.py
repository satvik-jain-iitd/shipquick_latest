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


def _cells(row):
    return [c.strip() for c in row.strip().strip("|").split("|")]


def _spike_row():
    rows = [r for r in _rows(EXPERIMENTS) if "rules" in r.lower() and "paths" in r.lower()]
    assert rows, "no 2026-11-10 experiments row about path-scoped rules (#328)"
    return rows[0]


def test_a13_experiments_row_has_five_cells_like_the_header():
    header = next(line for line in EXPERIMENTS.splitlines() if line.startswith("| Date |"))
    row = _spike_row()
    assert row.count("|") == header.count("|") == 6, "the #328 row must have 5 cells, as the header does"
    assert len(_cells(row)) == 5


def test_a13_result_and_decision_sit_in_their_own_columns():
    cells = _cells(_spike_row())
    assert "pending test" in cells[3].lower(), "Result cell (index 3) must say pending test"
    assert "pending test" not in cells[2].lower(), "Design cell must not hold the result"
    assert cells[4].startswith("Decision:"), "Decision cell (index 4) must start with Decision:"

def test_a13_study_adapt_row_cites_the_docs_url():
    rows = [line for line in STUDY.splitlines() if line.startswith("| Rules split by path")]
    assert rows, "the Adapt table row for #328 is missing"
    assert DOCS_URL in rows[0], "the #328 Adapt row must cite the Claude Code docs URL"


def test_a13_every_test_in_this_file_is_listed_in_test_cases():
    import re

    names = re.findall(r"^def (test_\w+)", Path(__file__).read_text(encoding="utf-8"), re.M)
    cases = (ROOT / "docs" / "test-cases.md").read_text(encoding="utf-8")
    missing = [n for n in names if f"`{n}`" not in cases]
    assert not missing, f"tests not listed in docs/test-cases.md (rule 5): {missing}"
