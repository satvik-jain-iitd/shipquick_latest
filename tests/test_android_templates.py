"""Story #134 (S4): five Android screen templates, built only from Compose Material 3 parts (rule 38).
A text scan until the S7 lint lands: no hand-drawn UI, no raw colour, no custom Shape, no Material 2 import.
The step flow follows docs/DESIGN_PROCESS.md section 12: filled button last, outline above it, keyboard-aware."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "ui" / "android" / "templates"
WANT = {"SignInTemplate.kt", "ListTemplate.kt", "DetailTemplate.kt", "SettingsTemplate.kt", "StepFlowTemplate.kt"}
FORBIDDEN = {
    "Canvas(": re.compile(r"\bCanvas\("),
    "drawBehind": re.compile(r"\bdrawBehind\b"),
    "Color(0x": re.compile(r"\bColor\(0x"),
    "custom Shape class": re.compile(r"\b(class|object)\s+\w+[^{\n]*:\s*[\w.]*Shape\b"),
    # Material 2. The icon set lives under androidx.compose.material.icons and is what Google's M3 guides use.
    "Material 2 import": re.compile(r"^import androidx\.compose\.material\.(?!icons\.)", re.M),
}


def test_s134_the_five_templates_exist():
    assert {p.name for p in TEMPLATES.glob("*.kt")} == WANT


def test_s134_the_templates_use_no_hand_drawn_ui():
    hits = [f"{p.name}: {label}" for p in sorted(TEMPLATES.glob("*.kt"))
            for label, rx in FORBIDDEN.items() if rx.search(p.read_text(encoding="utf-8"))]
    assert TEMPLATES.is_dir() and not hits, hits


def test_s134_the_scan_catches_each_forbidden_pattern():
    bad = ["Canvas(Modifier) {}", "Modifier.drawBehind { }", "val c = Color(0xFF00FF00)",
           "class Blob : Shape {", "import androidx.compose.material.Button"]
    for text, rx in zip(bad, FORBIDDEN.values()):
        assert rx.search(text), text
    assert not FORBIDDEN["Material 2 import"].search("import androidx.compose.material.icons.Icons")
    assert not FORBIDDEN["Material 2 import"].search("import androidx.compose.material3.Button")


def test_s134_the_step_flow_puts_the_filled_button_last_and_rides_the_keyboard():
    text = (TEMPLATES / "StepFlowTemplate.kt").read_text(encoding="utf-8")
    assert "imePadding()" in text
    outline, filled = text.find("OutlinedButton("), text.rfind("\n            Button(")
    assert -1 < outline < filled, "the outline button must come before the filled one"
