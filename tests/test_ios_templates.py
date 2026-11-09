"""Story #135 (S5, rule 38): every iOS screen template in ui/ios/templates/ uses only standard SwiftUI.

A text scan, until the macOS CI job compiles and snapshots them: no custom Shape or ButtonStyle, no Path,
no raw colour (red:, hue:, white:), no Canvas, no UIKit view, no import but SwiftUI and Foundation, and no
numeric literal in padding, frame, cornerRadius, offset, a system font size or a stack spacing (token
references pass). The step flow follows DESIGN_PROCESS rule 12."""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
IOS = ROOT / "ui" / "ios"
NUM = r"(?<![\w.])\d"   # a numeric literal; a token like Tokens.space2 is not one (PR #211 second review)
RAW = {
    "custom Shape or ButtonStyle": re.compile(r":\s*(?:[\w.]+\s*[,&]\s*)*(?:Shape|InsettableShape|ButtonStyle|PrimitiveButtonStyle|ToggleStyle|LabelStyle)\b"),
    "Path {": re.compile(r"\bPath\s*[({]"),
    "raw colour": re.compile(r"\b(?:UI|NS)?Color(?:\.init)?\([^)]*\b(?:red|hue|white)\s*:|\.init\(\s*(?:\.\w+\s*,\s*)?(?:red|hue|white)\s*:"),
    "Canvas {": re.compile(r"\bCanvas\s*[({]"),
    "raw gesture": re.compile(r"\.(?:gesture|simultaneousGesture|highPriorityGesture|onTapGesture|onLongPressGesture)\s*[({]|"
                              r"\b(?:DragGesture|TapGesture|LongPressGesture|MagnificationGesture|RotationGesture|SpatialTapGesture)\b"),
    "UIKit view": re.compile(r"\bclass\s+\w+\s*:[^{]*\bUIView\b|\bUIView(?:Controller)?Representable\b"),
    "import other than SwiftUI or Foundation": re.compile(r"^\s*(?:@\w+\s+)?import\s+(?!(?:SwiftUI|Foundation)\b)\w+", re.M),
    "number in a layout modifier": re.compile(
        r"\.(?:padding|frame|cornerRadius|offset|position|lineSpacing|shadow|blur|tracking|kerning)\([^)]*?" + NUM),
    "fixed font size": re.compile(r"\.system\(\s*size:\s*" + NUM),
    "number in spacing:": re.compile(r"\bspacing:\s*" + NUM),
}


def raw_ui(text):
    return [name for name, rx in RAW.items() if rx.search(text)]


BAD = [
    "struct Blob: Shape { func path(in r: CGRect) -> Path { Path() } }",
    "struct Pill : InsettableShape {}",
    "struct Fancy: ButtonStyle { func makeBody(configuration: Configuration) -> some View { configuration.label } }",
    "struct Raw: PrimitiveButtonStyle {}",
    "extension Blob: Shape {}",
    "let p = Path { p in p.move(to: .zero) }",
    "Text(\"x\").foregroundStyle(Color(red: 0.2, green: 0.1, blue: 0.9))",
    "Color(.sRGB, red: 0.2, green: 0.1, blue: 0.9)",
    "Color(hue: 0.5, saturation: 1, brightness: 1)",
    "Color(white: 0.5)",
    "UIColor(red: 1, green: 0, blue: 0, alpha: 1)",
    "Canvas { context, size in }",
    "Canvas(opaque: true) { context, size in }",
    "Text(\"x\").gesture(DragGesture())",
    "Text(\"x\").onTapGesture { }",
    "let g = LongPressGesture()",
    "Text(\"x\").simultaneousGesture(TapGesture())",
    "struct Pill: ToggleStyle {}",
    "struct Tag: LabelStyle {}",
    "struct Chip<T>: Hashable, ButtonStyle {}",
    "struct Both: View & ButtonStyle {}",
    "let c = Color.init(red: 1, green: 0, blue: 0)",
    "let c: Color = .init(red: 1, green: 0, blue: 0)",
    "final class Card: UIView {}",
    "struct Map: UIViewRepresentable {}",
    "struct Picker2: UIViewControllerRepresentable {}",
    "import SnapKit",
    "import UIKit",
    "Text(\"x\").padding(.horizontal, 13)",
    "Text(\"x\").padding(8)",
    "Image(\"x\").frame(width: 120)",
    "Text(\"x\").cornerRadius(12)",
    "Text(\"x\").font(.system(size: 17))",
    "VStack(spacing: 24) {}",
    "Text(\"x\").offset(x: 4)",
]
GOOD = [
    "import SwiftUI\nimport Foundation",
    "Text(\"x\").padding()\nButton(\"Go\") {}.buttonStyle(.borderedProminent)",
    "Text(\"x\").padding(.top, Tokens.space2)",
    "VStack(spacing: Tokens.space3) {}",
    "Image(\"x\").frame(width: Tokens.icon48, height: Tokens.icon48)",
    "Text(\"x\").frame(maxWidth: .infinity)",
    "Text(\"x\").font(Tokens.body)",
    "ProgressView(value: Double(index + 1), total: Double(steps.count))",
]


@pytest.mark.parametrize("text", BAD)
def test_s135_the_scan_catches_each_kind_of_raw_ui(text):
    assert raw_ui(text), text


@pytest.mark.parametrize("text", GOOD)
def test_s135_standard_swiftui_and_token_references_pass_the_scan(text):
    assert raw_ui(text) == [], (text, raw_ui(text))


def templates():
    return sorted((IOS / "templates").glob("*.swift"))


def test_s135_every_template_is_a_public_view_with_a_preview_and_no_raw_ui():
    assert len(templates()) >= 5
    for path in templates():
        text = path.read_text(encoding="utf-8")
        assert f"public struct {path.stem}: View" in text, path.name
        assert "#Preview" in text, path.name
        assert raw_ui(text) == [], (path.name, raw_ui(text))


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
    for path in templates():
        assert path.stem in readme, path.stem
