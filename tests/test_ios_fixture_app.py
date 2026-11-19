"""Story #221 (S5f, rule 38): a tiny SwiftPM fixture app with one good and one bad screen.

GoodScreen uses only the kit's ui/ios module (ShipQuickUI) and its tokens; BadScreen holds a raw colour, a fixed
font size and a hand-drawn Shape. `ui/tool/ios_fixture_check.py` runs the CI tier of `ui/tool/ios_lint.sh` twice and
asserts both outcomes. SwiftLint is not on this Mac: the harness is tested with a stub swiftlint here, the rule
regexes are checked in Python, and CI (job ui-ios-lint, macos-15) runs the real tools."""
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "tests" / "fixtures" / "ios" / "FixtureApp"
SRC = APP / "Sources" / "FixtureApp"
GOOD, BAD = SRC / "GoodScreen.swift", SRC / "BadScreen.swift"
HARNESS = ROOT / "ui" / "tool" / "ios_fixture_check.py"
WANTED = {"no_raw_color", "no_fixed_font_size", "no_custom_shape_or_style"}

sys.path.insert(0, str(ROOT / "tests"))
from test_ios_lint_tool import swift_rules  # noqa: E402  (one parser for the rules file)


def test_s221_the_fixture_app_is_a_swiftpm_package_on_the_kit_module():
    pkg = (APP / "Package.swift").read_text(encoding="utf-8")
    assert re.search(r'\.package\(\s*path:\s*"(?:\.\./){4}ui/ios"\s*\)', pkg), "the app depends on the kit's ui/ios by path"
    assert '"ShipQuickUI"' in pkg and ".iOS(.v17)" in pkg
    assert GOOD.is_file() and BAD.is_file()


def test_s221_the_good_screen_uses_only_kit_components_and_tokens_and_breaks_no_rule():
    text = GOOD.read_text(encoding="utf-8")
    imports = set(re.findall(r"^\s*import\s+(\w+)", text, re.M))
    assert imports == {"ShipQuickUI", "SwiftUI"}, imports
    assert "ShipQuickTokens." in text and "Template()" in text, "it uses a kit template and kit tokens"
    for rule, (rx, _) in swift_rules().items():
        assert not rx.search(text), f"{rule} fires on the good screen"


def test_s221_the_bad_screen_breaks_the_three_named_rules():
    text = BAD.read_text(encoding="utf-8")
    fired = {rule for rule, (rx, _) in swift_rules().items() if rx.search(text)}
    assert WANTED <= fired, f"missing: {WANTED - fired}"
    assert "Color(red:" in text and ".font(.system(size:" in text and re.search(r"struct \w+: Shape", text)


STUB = """#!/usr/bin/env bash
# a fake swiftlint: for a file named Bad*, prints one violation per rule id in $FAKE_RULES and exits 2
for a in "$@"; do case "$a" in *Bad*.swift) bad=$a;; esac; done
[ -z "${bad:-}" ] && exit 0
for r in $FAKE_RULES; do echo "$bad:1:1: error: X Violation: m ($r)"; done
[ -n "$FAKE_RULES" ] && exit 2 || exit 0
"""


def harness(tmp_path, fake_rules):
    b = tmp_path / "bin"
    b.mkdir()
    for name, body in (("swiftlint", STUB), ("swiftformat", "#!/usr/bin/env bash\nexit 0\n")):
        (b / name).write_text(body, encoding="utf-8")
        (b / name).chmod(0o755)
    env = {**os.environ, "PATH": f"{b}:{os.environ['PATH']}", "FAKE_RULES": fake_rules}
    return subprocess.run([sys.executable, str(HARNESS)], cwd=ROOT, env=env, capture_output=True, text=True)


def test_s221_harness_passes_when_good_is_clean_and_bad_names_every_rule(tmp_path):
    p = harness(tmp_path, " ".join(sorted(WANTED)))
    assert p.returncode == 0, p.stdout + p.stderr
    for rule in WANTED:
        assert f"reported as wanted: {rule}" in p.stdout


def test_s221_harness_fails_when_the_bad_screen_passes(tmp_path):
    p = harness(tmp_path, "")
    assert p.returncode == 1 and "the bad screen passed" in p.stdout, p.stdout + p.stderr


def test_s221_harness_fails_naming_a_rule_that_was_not_reported(tmp_path):
    p = harness(tmp_path, "no_raw_color no_fixed_font_size")
    assert p.returncode == 1 and "rule not reported: no_custom_shape_or_style" in p.stdout, p.stdout + p.stderr


def test_s221_ci_lints_and_compiles_the_fixture_app():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    lint = ci[ci.index("  ui-ios-lint:"):ci.index("  secret-scan:")]
    assert "python3 ui/tool/ios_fixture_check.py" in lint
    comp = ci[ci.index("  ui-ios-compile:"):ci.index("  ui-android-lint:")]
    assert "tests/fixtures/ios/FixtureApp" in comp and "-scheme FixtureApp" in comp
