"""Story #185 (S7, rule 38): the child lint configs never drift from the kit's own template tests.

test_android_templates.py and test_ios_templates.py ban patterns in the kit's templates. A child is checked by
detekt and Konsist (Android) and SwiftLint (iOS). Each pattern the template tests ban must also be in a lint config,
so the two lists cannot grow apart. The configs and fixtures are read as text; nothing runs here."""
import re
from pathlib import Path

import pytest

import test_android_templates as android
import test_ios_templates as ios

ROOT = Path(__file__).resolve().parent.parent
ALINT = ROOT / "ui" / "android" / "lint"
ILINT = ROOT / "ui" / "ios" / "lint"
FIX = ROOT / "tests" / "fixtures"

# Android: banned label -> the text that must be in detekt.yml (an import) or in the Konsist test.
DETEKT = {
    "Canvas(": "androidx.compose.foundation.Canvas",
    "drawBehind": "androidx.compose.ui.draw.drawBehind",
    "drawWithContent": "androidx.compose.ui.draw.drawWithContent",
    "Color(": "androidx.compose.ui.graphics.Color",
    ".background(Color.": "androidx.compose.ui.graphics.Color",
    "GenericShape": "androidx.compose.foundation.shape.GenericShape",
    "RoundedCornerShape(": "androidx.compose.foundation.shape.RoundedCornerShape",
}
KONSIST = {
    "Canvas(": "no_canvas",
    "drawBehind": "no_draw_modifiers",
    "drawWithContent": "no_draw_modifiers",
    "Color(": "no_raw_color",
    ".background(Color.": "no_raw_color",
    "GenericShape": "no_hand_made_shape",
    "RoundedCornerShape(": "no_hand_made_shape",
    "custom Shape class": "no_custom_shape_class",
}
# iOS: banned label -> the custom rule id in swiftlint.yml that refuses it.
SWIFTLINT = {
    "custom Shape or ButtonStyle": "no_custom_shape_or_style",
    "Path {": "no_path",
    "raw colour": "no_raw_color",
    "Canvas {": "no_canvas",
    "UIKit view": "no_uikit_view",
    "import other than SwiftUI or Foundation": "no_uikit_or_ui_kit_import",
    "number in a layout modifier": "no_number_in_layout_modifier",
    "fixed font size": "no_fixed_font_size",
    "number in spacing:": "no_number_in_spacing",
}


EXTRA = {"no_custom_font"}   # Font.custom outside Tokens: no template ban, the templates never name a font


def text(path):
    return path.read_text(encoding="utf-8")


def swift_rules():
    """{rule id: its regex}, read from the custom_rules block of swiftlint.yml."""
    rules, current = {}, None
    for line in text(ILINT / "swiftlint.yml").splitlines():
        m = re.match(r"^  (\w+):\s*$", line)
        if m:
            current = m.group(1)
        m = re.match(r"^    regex: '(.*)'\s*$", line)
        if m and current:
            rules[current] = re.compile(m.group(1), re.M)
    return rules


def test_s185_every_android_template_ban_has_a_lint_twin():
    assert set(android.BANNED) == set(KONSIST), "a template ban with no Konsist twin (or the reverse)"
    detekt, konsist = text(ALINT / "detekt.yml"), text(ALINT / "UiRulesKonsistTest.kt")
    for label, imp in DETEKT.items():
        assert f"'{imp}'" in detekt, f"{label}: {imp} is not in detekt.yml"
    for label, name in KONSIST.items():
        assert f"fun {name}()" in konsist, f"{label}: {name} is not a Konsist test"


def test_s185_detekt_bans_the_off_list_imports_the_template_test_refuses():
    pat = text(ALINT / "detekt.yml")
    for needle in [r"androidx\.compose\.material\.(?!icons\.)", r"com\.google\.android\.material\.", r"android\.widget\.", r"com\.example\.fancyui\."]:
        assert needle in pat, needle
    rx = re.compile(re.search(r"forbiddenPatterns: '(.*)'", pat).group(1))
    for imp in ["androidx.compose.material.Button", "com.google.android.material.button.MaterialButton",
                "android.widget.Button", "com.example.fancyui.Chip"]:
        assert rx.search(imp), imp
    for ok in ["androidx.compose.material3.Button", "androidx.compose.material.icons.Icons", "androidx.compose.foundation.clickable"]:
        assert not rx.search(ok), ok


def test_s185_the_two_android_tiers_use_the_same_rule_with_a_different_severity():
    local, ci = text(ALINT / "detekt.yml"), text(ALINT / "detekt-ci.yml")
    assert "severity: warning" in local and "maxIssues: -1" in local
    assert "severity: error" in ci and "maxIssues: 0" in ci
    assert "ForbiddenImport" in ci and "forbiddenPatterns" not in ci, "the CI tier changes severity only"


def test_s185_every_ios_template_ban_has_a_swiftlint_rule():
    assert set(ios.RAW) == set(SWIFTLINT), "a template ban with no SwiftLint twin (or the reverse)"
    rules = swift_rules()
    for label, rule in SWIFTLINT.items():
        assert rule in rules, f"{label}: {rule} is not in swiftlint.yml"
    assert set(rules) == set(SWIFTLINT.values()) | EXTRA, "a SwiftLint rule no template ban explains"


def test_s185_swiftlint_has_the_disable_rules_and_every_rule_is_a_warning_locally():
    cfg = text(ILINT / "swiftlint.yml")
    assert "blanket_disable_command" in cfg and "superfluous_disable_command" in cfg
    assert cfg.count("severity: warning") >= len(swift_rules()) + 2
    assert "severity: error" not in cfg, "the CI tier is `swiftlint --strict`, not a second file"


@pytest.mark.parametrize("rule", sorted(set(SWIFTLINT.values()) | EXTRA))
def test_s185_the_bad_ios_screen_breaks_each_rule_and_the_good_one_none(rule):
    rx = swift_rules()[rule]
    assert rx.search(text(FIX / "ios" / "Bad" / "BadScreen.swift")), rule
    assert not rx.search(text(FIX / "ios" / "Good" / "GoodScreen.swift")), rule


def test_s185_the_bad_android_screen_names_every_forbidden_import_and_banned_text():
    bad = text(FIX / "android" / "src" / "bad" / "BadScreen.kt")
    for imp in set(DETEKT.values()) | {"androidx.compose.material.Button", "com.google.android.material.button.MaterialButton", "com.example.fancyui.FancyChip"}:
        assert f"import {imp}" in bad, imp
    assert "import android.widget.Button" in bad
    for label, rx in android.BANNED.items():
        assert rx.search(bad), f"the bad screen never breaks: {label}"
    good = text(FIX / "android" / "src" / "good" / "GoodScreen.kt")
    assert android.problems(good) == [], android.problems(good)


def test_s185_the_good_fixtures_pass_the_template_scans():
    assert ios.raw_ui(text(FIX / "ios" / "Good" / "GoodScreen.swift")) == []
