"""Story #426 (F9, epic #86): one page says what each feature does and how to change it; CLAUDE.md carries rule 39."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULTS = json.loads((ROOT / "scripts" / "features_default.json").read_text(encoding="utf-8"))["features"]
DOC = (ROOT / "docs" / "FEATURES.md").read_text(encoding="utf-8")


def test_the_doc_lists_every_feature_and_only_those():
    ids = set(re.findall(r"^\| `([a-z-]+)` \|", DOC, re.M))
    assert ids == set(DEFAULTS), (ids ^ set(DEFAULTS))


def test_each_row_carries_the_plain_words_default_and_lock_from_the_defaults_file():
    for fid, d in DEFAULTS.items():
        row = next(l for l in DOC.splitlines() if l.startswith(f"| `{fid}` |"))
        assert d["name"] in row and d["what"] in row and d["if_off"] in row, fid
        assert ("always on" in row) == bool(d["locked"]), fid


def test_the_doc_says_who_changes_what_and_how():
    assert "scripts/features.sh set" in DOC and "owner merges" in DOC and "protected path" in DOC
    assert "`adoption`" in DOC and "locked" in DOC


def test_rule_39_is_in_claude_md_and_points_to_the_doc():
    t = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    m = re.search(r"^39\. \*\*(.+?)\*\*.*$", t, re.M)
    assert m and "docs/FEATURES.md" in m.group(0)
