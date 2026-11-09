"""Story #134 (S4): five Android screen templates, built only from Compose Material 3 parts (rule 38).
A text scan until the S7 lint lands. Imports come from an allow-list, and banned patterns (hand-drawn UI,
raw colour, custom or hand-made shapes) are refused. Google's own patterns (clickable, selectable, toggleable,
verticalScroll) stay allowed. An experimental M3 API needs @OptIn(ExperimentalMaterial3Api::class).
The step flow follows docs/DESIGN_PROCESS.md section 12: filled button last, outline above it, keyboard-aware."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "ui" / "android" / "templates"
WANT = {"SignInTemplate.kt", "ListTemplate.kt", "DetailTemplate.kt", "SettingsTemplate.kt", "StepFlowTemplate.kt"}
IMPORT = re.compile(r"^import\s+(\S+)", re.M)
# M3, its foundation, runtime and ui layers, Google's icon set (what the M3 guides use), and the Kotlin stdlib.
ALLOWED_IMPORT = re.compile(r"androidx\.compose\.(material3|foundation|runtime|ui)\.\S+|androidx\.compose\.material\.icons\.\S+|kotlin\.\S+")
BANNED = {
    "Canvas(": re.compile(r"\bCanvas\s*\("),
    "drawBehind": re.compile(r"\bdrawBehind\b"),
    "drawWithContent": re.compile(r"\bdrawWithContent\b"),
    "Color(": re.compile(r"\bColor\s*\("),
    ".background(Color.": re.compile(r"\.background\(\s*Color\."),
    "GenericShape": re.compile(r"\bGenericShape\b"),
    "RoundedCornerShape(": re.compile(r"\bRoundedCornerShape\s*\("),
    "custom Shape class": re.compile(r"\b(class|object)\s+\w+[^{\n]*:\s*[\w.]*Shape\b"),
}
# Experimental in the stable M3 releases. Calling one needs the opt-in on the file or the function.
EXPERIMENTAL = re.compile(r"\b(TopAppBar|CenterAlignedTopAppBar|MediumTopAppBar|LargeTopAppBar|ModalBottomSheet|"
                          r"TooltipBox|SearchBar|DockedSearchBar|DatePicker|DateRangePicker|TimePicker|TimeInput)\s*\(")
OPT_IN = "@OptIn(ExperimentalMaterial3Api::class)"


def problems(text):
    """Every rule a template's text breaks."""
    bad = [f"import {i} is not on the allow-list" for i in IMPORT.findall(text) if not ALLOWED_IMPORT.fullmatch(i)]
    bad += [f"banned: {label}" for label, rx in BANNED.items() if rx.search(text)]
    if EXPERIMENTAL.search(text) and (OPT_IN not in text or "import androidx.compose.material3.ExperimentalMaterial3Api" not in text):
        bad.append(f"an experimental M3 API without {OPT_IN}")
    return bad


def templates():
    return sorted(TEMPLATES.glob("*.kt"))


def test_s134_the_five_templates_exist():
    assert {p.name for p in templates()} == WANT


def test_s134_the_templates_break_no_rule():
    hits = [f"{p.name}: {b}" for p in templates() for b in problems(p.read_text(encoding="utf-8"))]
    assert TEMPLATES.is_dir() and not hits, hits


GOOD = "import androidx.compose.material3.Button\nimport androidx.compose.ui.Modifier\n"


def test_s134_each_banned_pattern_is_caught():
    for label, line in {
        "Canvas(": "Canvas(Modifier) {}",
        "drawBehind": "Modifier.drawBehind { }",
        "drawWithContent": "Modifier.drawWithContent { drawContent() }",
        "Color(": "val c = Color (0xFF00FF00)",
        ".background(Color.": "Modifier.background(Color.Red)",
        "GenericShape": "val s = GenericShape { _, _ -> }",
        "RoundedCornerShape(": "shape = RoundedCornerShape(8.dp)",
        "custom Shape class": "class Blob : Shape {",
    }.items():
        assert f"banned: {label}" in problems(GOOD + line), label


def test_s134_an_import_off_the_allow_list_is_caught():
    for imp in ["androidx.compose.material.Button", "com.google.android.material.button.MaterialButton",
                "android.widget.Button", "com.example.fancyui.Chip", "androidx.compose.animation.Crossfade"]:
        assert f"import {imp} is not on the allow-list" in problems(GOOD + f"import {imp}\n"), imp


def test_s134_googles_own_patterns_stay_allowed():
    text = GOOD + "\n".join(f"import {i}" for i in [
        "androidx.compose.material.icons.Icons", "androidx.compose.foundation.clickable",
        "androidx.compose.foundation.selection.selectable", "androidx.compose.foundation.selection.toggleable",
        "androidx.compose.foundation.verticalScroll", "androidx.compose.runtime.remember", "kotlin.math.max",
    ]) + "\nModifier.clickable { }.verticalScroll(s)\ncolor = MaterialTheme.colorScheme.error\n"
    assert problems(text) == []


def test_s134_an_experimental_api_without_the_opt_in_is_caught():
    call = "\nTopAppBar(title = { Text(\"Hi\") })\n"
    assert any("experimental" in b for b in problems(GOOD + call))
    opted = GOOD + "import androidx.compose.material3.ExperimentalMaterial3Api\n" + OPT_IN + "\nfun A() {" + call + "}"
    assert problems(opted) == []


def test_s134_the_step_flow_puts_the_filled_button_last_and_rides_the_keyboard():
    text = (TEMPLATES / "StepFlowTemplate.kt").read_text(encoding="utf-8")
    assert "imePadding()" in text
    outline, filled = text.find("OutlinedButton("), text.rfind("\n            Button(")
    assert -1 < outline < filled, "the outline button must come before the filled one"
