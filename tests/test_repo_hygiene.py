"""Repo hygiene tests. S0.3: CI runs tests."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FORBIDDEN = re.compile(
    r"american express|americanexpress|aexp|amex|bhavna|ease-full|ease full",
    re.IGNORECASE,
)
SCAN_SUFFIXES = {".md", ".yml", ".yaml", ".py"}


def test_readme_exists_and_lists_platforms():
    text = (ROOT / "README.md").read_text()
    for word in ("Web", "Android", "iOS", "Flutter", "Material Design 3"):
        assert word in text, f"README missing {word}"


def test_required_files_exist():
    for rel in (
        "CLAUDE.md",
        "COMMIT_GUIDELINES.md",
        ".gitignore",
        ".editorconfig",
        ".pre-commit-config.yaml",
        "docs/PLAN.md",
        "docs/process-trace.md",
        "docs/architecture.md",
        "docs/design-tokens.md",
        ".github/workflows/ci.yml",
        ".github/PULL_REQUEST_TEMPLATE.md",
        "docs/TEAM_PROTOCOL.md",
        "docs/TEAM_ROSTER.md",
    ):
        assert (ROOT / rel).is_file(), f"missing {rel}"


def test_no_forbidden_brand_names():
    bad = []
    for path in ROOT.rglob("*"):
        if ".git/" in str(path) or not path.is_file():
            continue
        if path == Path(__file__).resolve():
            continue
        if path.suffix.lower() not in SCAN_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="strict")
        except (UnicodeDecodeError, OSError):
            continue
        if FORBIDDEN.search(text):
            bad.append(str(path.relative_to(ROOT)))
    assert not bad, f"forbidden brand names in: {bad}"
