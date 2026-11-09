"""Story #134 (S4): the Android library. Google's own Compose Material 3 components page is counted in
docs/research/android-m3-components.md, and every row there gets an S2 doc, a contract and an android topic."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIST = ROOT / "docs" / "research" / "android-m3-components.md"
SOURCE = "https://developer.android.com/develop/ui/compose/components"


def rows():
    """(component, doc folder cell, compose api, page url) for each table row."""
    out = []
    for line in LIST.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and cells[0].isdigit():
            out.append((cells[1], cells[2].strip("`"), cells[3].strip("`"), cells[5]))
    return out


def test_s134_the_counted_list_names_its_source_its_date_and_a_count_that_matches_the_table():
    text = LIST.read_text(encoding="utf-8")
    assert SOURCE in text and "2026-11-09" in text
    count = int(re.search(r"^Count: (\d+)", text, re.M).group(1))
    assert count == len(rows()) > 0
    assert [int(line.strip("|").split("|")[0]) for line in text.splitlines()
            if line.startswith("|") and line.strip("|").split("|")[0].strip().isdigit()] == list(range(1, count + 1))


def test_s134_every_listed_component_with_a_folder_has_a_doc_a_contract_and_an_android_topic():
    built = [r for r in rows() if r[1].startswith("ui/components/")]
    assert built, "no row names a doc folder yet"
    for component, folder, api, page in built:
        name = Path(folder).name
        doc = ROOT / folder / f"{name}.doc.mjs"
        assert doc.exists() and (ROOT / folder / f"{name}.contract.json").exists(), component
        body = json.loads(doc.read_text(encoding="utf-8").split("export default", 1)[1].strip().rstrip(";"))
        assert body["platforms"]["android"] == api, f"{component}: table says {api}"
        assert page.startswith("https://developer.android.com/"), component
        assert (ROOT / "ui" / "integration" / "docs" / f"android-{name.lower()}.doc.mjs").exists(), component


def test_s134_every_component_on_googles_page_has_a_doc_folder():
    pending = [r[0] for r in rows() if not r[1].startswith("ui/components/")]
    assert not pending, f"no doc folder yet: {pending}"


def android_props(name):
    contract = json.loads((ROOT / "ui" / "components" / name / f"{name}.contract.json").read_text(encoding="utf-8"))
    return set(contract["core"]) | set(contract["platforms"].get("android", {}))


def test_s134_the_navigation_bar_documents_its_items():
    # NavigationBarItem(selected, onClick, icon, label): Google's navigation-bar page and the M3 reference.
    assert {"content", "selected", "onClick", "icon", "label"} <= android_props("NavigationBar")
