"""Story #135 (S5, rule 38): the iOS library starts from Apple's own counted list.

docs/research/ios-swiftui-components.md names its source, its date and a count that equals its table.
Every row with no Compose Material 3 twin ("none (iOS-only)") has its own doc folder in ui/components/
whose `platforms.ios` is that exact SwiftUI type, and a generated `ios-<name>` topic."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from check_ui_docs import read_doc  # noqa: E402

LIST = ROOT / "docs" / "research" / "ios-swiftui-components.md"
IOS_ONLY = "none (iOS-only)"


def android_components():
    """Full names of the component rows of docs/research/android-m3-api.md."""
    text = (ROOT / "docs" / "research" / "android-m3-api.md").read_text(encoding="utf-8")
    cells = [[c.strip() for c in l.strip().strip("|").split("|")] for l in text.splitlines() if l.startswith("|")]
    return {f"{c[5].strip('`')}.{c[1].strip('`')}" for c in cells if c[0].isdigit() and c[2] == "component"}


def rows():
    """Counted table rows: | n | HIG component | SwiftUI type | iOS since | Doc URL | Same as M3 component | Our doc |"""
    out = []
    for line in LIST.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and cells[0].isdigit():
            out.append(cells)
    return out


def test_s135_the_counted_list_names_its_source_date_and_a_count_equal_to_its_rows():
    text = LIST.read_text(encoding="utf-8")
    assert "https://developer.apple.com/design/human-interface-guidelines/components" in text
    assert "2026-11-09" in text
    m = re.search(r"^Count: (\d+)$", text, re.M)
    assert m, "no 'Count: N' line"
    got = rows()
    assert got and int(m.group(1)) == len(got)
    assert [int(r[0]) for r in got] == list(range(1, len(got) + 1)), "rows are numbered 1..N"
    for r in got:
        assert len(r) == 7, r
        assert r[2].startswith("`SwiftUI."), r
        assert r[4].startswith("https://developer.apple.com/documentation/swiftui/"), r


def test_s135_every_ios_only_row_has_a_doc_folder_and_an_ios_topic():
    only = [r for r in rows() if r[5] == IOS_ONLY]
    assert only, "no iOS-only row"
    for r in only:
        name, swift = r[6].strip("`"), r[2].strip("`")
        doc = read_doc(ROOT / "ui" / "components" / name / f"{name}.doc.mjs")
        assert doc["platforms"]["ios"] == swift, (name, doc["platforms"])
        # No M3 card twin, but the doc may carry an Android component row of the generated API list (PR #255
        # review 2: Text is both SwiftUI.Text and androidx.compose.material3.Text).
        assert doc["platforms"]["android"] in {None, *android_components()}, name
        assert (ROOT / "ui" / "integration" / "docs" / f"ios-{name.lower()}.doc.mjs").exists(), name


def test_s135_a_shared_row_names_its_m3_component_and_no_new_doc():
    for r in rows():
        if r[5] != IOS_ONLY:
            assert r[5] and r[6] == "-", r
