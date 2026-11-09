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


# The children registry names real repos, and one real repo carries a forbidden word in its name.
# Owner, 9 Nov 2026: "children.md ko test se chhoot do". Only this one file is exempt, never the whole docs/ tree.
EXEMPT = {"docs/children.md"}


def forbidden_files(root, exempt=frozenset(EXEMPT)):
    """Relative paths of scanned files that hold a forbidden name, minus the exempt ones."""
    bad = []
    for path in root.rglob("*"):
        if ".git/" in str(path) or not path.is_file():
            continue
        if path == Path(__file__).resolve():
            continue
        rel = str(path.relative_to(root))
        if rel in exempt or path.suffix.lower() not in SCAN_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="strict")
        except (UnicodeDecodeError, OSError):
            continue
        if FORBIDDEN.search(text):
            bad.append(rel)
    return bad


def test_no_forbidden_brand_names():
    bad = forbidden_files(ROOT)
    assert not bad, f"forbidden brand names in: {bad}"


def test_only_the_children_registry_is_exempt():
    assert EXEMPT == {"docs/children.md"}


def test_the_exemption_is_one_file_not_a_folder(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "children.md").write_text("owner/bhavna-ai\n")
    (tmp_path / "docs" / "other.md").write_text("owner/bhavna-ai\n")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "x.py").write_text("# amex\n")
    assert sorted(forbidden_files(tmp_path)) == ["docs/other.md", "scripts/x.py"]


def test_the_registry_lists_the_public_child_that_the_ban_hid():
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from adoption_scan import read_children

    children = dict(read_children(ROOT / "docs" / "children.md"))
    assert children.get("satvik-jain-iitd/bhavna-ai") is False, "bhavna-ai is public: listed, not private"
