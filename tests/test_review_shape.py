"""Story #317 (A4a, epic #309): every review finding has one fixed shape, documented in docs/REVIEW_SHAPE.md."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "REVIEW_SHAPE.md"
PROTOCOL = ROOT / "docs" / "TEAM_PROTOCOL.md"


def test_review_shape_doc_exists():
    assert DOC.is_file(), "docs/REVIEW_SHAPE.md is missing"


def test_review_shape_names_the_four_parts_and_the_end_lines():
    text = DOC.read_text(encoding="utf-8")
    for part in ("What this is", "Problem", "Fix", "If we skip"):
        assert f"**{part}:**" in text, part
    assert "Verdict:" in text
    assert "Not checked:" in text


def test_review_shape_keeps_the_gate_rules():
    text = DOC.read_text(encoding="utf-8")
    assert "80%" in text
    assert "callers" in text
    assert "shortcut:" in text
    assert "zero findings" in text.lower()
    assert "fresh agent" in text


def test_team_protocol_links_the_review_shape_doc():
    assert "docs/REVIEW_SHAPE.md" in PROTOCOL.read_text(encoding="utf-8")
