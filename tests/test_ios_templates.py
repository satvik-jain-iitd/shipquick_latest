"""Story #135 (S5, rule 38): the five iOS screen templates use only standard SwiftUI.

A text scan, until the macOS CI job compiles and snapshots them: no custom Shape, no Color(red:, no
.padding( with a bare number, no Canvas, no UIView subclass. The step flow follows DESIGN_PROCESS rule 12."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IOS = ROOT / "ui" / "ios"
TEMPLATES = ["SignInTemplate", "ListTemplate", "DetailTemplate", "SettingsTemplate", "StepFlowTemplate"]
RAW = {
    "custom Shape": re.compile(r"\b(?:struct|class)\s+\w+\s*:[^{]*\bShape\b"),
    "Color(red:": re.compile(r"\b(?:UI)?Color\(\s*red:"),
    ".padding( with a bare number": re.compile(r"\.padding\([^)]*\d"),
    "Canvas {": re.compile(r"\bCanvas\s*\{"),
    "UIView subclass": re.compile(r"\bclass\s+\w+\s*:[^{]*\bUIView\b"),
}


def raw_ui(text):
    return [name for name, rx in RAW.items() if rx.search(text)]


def test_s135_the_scan_catches_each_kind_of_raw_ui():
    bad = {
        "custom Shape": "struct Blob: Shape { func path(in r: CGRect) -> Path { Path() } }",
        "Color(red:": "Text(\"x\").foregroundStyle(Color(red: 0.2, green: 0.1, blue: 0.9))",
        ".padding( with a bare number": "Text(\"x\").padding(.horizontal, 13)",
        "Canvas {": "Canvas { context, size in }",
        "UIView subclass": "final class Card: UIView {}",
    }
    for name, text in bad.items():
        assert raw_ui(text) == [name], (name, raw_ui(text))
    assert raw_ui("Text(\"x\").padding()\nButton(\"Go\") {}.buttonStyle(.borderedProminent)") == []


def test_s135_the_five_templates_exist_and_use_no_raw_ui():
    for name in TEMPLATES:
        path = IOS / "templates" / f"{name}.swift"
        text = path.read_text(encoding="utf-8")
        assert f"public struct {name}: View" in text, name
        assert "#Preview" in text, name
        assert raw_ui(text) == [], (name, raw_ui(text))


def test_s135_the_step_flow_keeps_the_main_button_last_at_the_bottom_above_the_keyboard():
    text = (IOS / "templates" / "StepFlowTemplate.swift").read_text(encoding="utf-8")
    inset = text[text.index(".safeAreaInset(edge: .bottom"):]
    alt, main = inset.index(".buttonStyle(.bordered)"), inset.index(".buttonStyle(.borderedProminent)")
    assert alt < main, "the bordered alternative sits above the filled main button"
    assert "TextField(" in text, "one step types, so the inset rides above the keyboard"
    assert ".ignoresSafeArea(.keyboard" not in text, "the bottom bar must not hide under the keyboard"


def test_s135_the_package_has_no_dependencies_and_the_readme_says_how_to_use_it():
    pkg = (IOS / "Package.swift").read_text(encoding="utf-8")
    assert 'name: "ShipQuickUI"' in pkg
    assert "dependencies:" not in pkg and ".package(" not in pkg
    readme = (IOS / "README.md").read_text(encoding="utf-8")
    assert '.package(path: "knowledge/shipquick_latest/ui/ios")' in readme
    for name in TEMPLATES:
        assert name in readme, name
