"""Story #218 (S5c, rule 38): the two-tier iOS lint runner for a child.

`ui/tool/ios_lint.sh` runs SwiftLint (and SwiftFormat in lint mode) on the Swift files changed against the base
branch, with the committed baseline. CI=1 makes it strict (an error fails); otherwise it only warns.
SwiftLint is not on this Mac: the runner is tested with stub binaries that record their arguments, the rule
regexes are tested in Python, and CI (job ui-ios-lint) runs the real tools on the fixtures."""
import fnmatch
import json
import os
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "ui" / "tool" / "ios_lint.sh"
ILINT = ROOT / "ui" / "ios" / "lint"
BASELINE = ILINT / "swiftlint-baseline.json"
FIX = ROOT / "tests" / "fixtures" / "ios"
GOOD = FIX / "Good" / "GoodScreen.swift"
STUB = "#!/usr/bin/env bash\nprintf '%s\\n' \"$@\" >> \"$RECORD/$(basename \"$0\").args\"\n"


def stubs(tmp_path):
    """A bin folder with fake swiftlint and swiftformat that record their arguments."""
    bin_dir, record = tmp_path / "bin", tmp_path / "record"
    bin_dir.mkdir(exist_ok=True)
    record.mkdir(exist_ok=True)
    for name in ("swiftlint", "swiftformat"):
        p = bin_dir / name
        p.write_text(STUB, encoding="utf-8")
        p.chmod(0o755)
    return bin_dir, record


def run(tmp_path, *files, cwd=ROOT, ci=None, env=None):
    bin_dir, record = stubs(tmp_path)
    e = {k: v for k, v in os.environ.items() if k != "CI"}
    e.update({"PATH": f"{bin_dir}:{e['PATH']}", "RECORD": str(record)})
    if ci is not None:
        e["CI"] = ci
    e.update(env or {})
    proc = subprocess.run(["bash", str(TOOL), *map(str, files)], cwd=cwd, env=e, capture_output=True, text=True)
    args = {n: (record / f"{n}.args").read_text(encoding="utf-8").split("\n")[:-1] for n in ("swiftlint", "swiftformat") if (record / f"{n}.args").exists()}
    return proc, args


def test_s218_ci_tier_runs_swiftlint_strict_with_the_baseline_on_the_given_files(tmp_path):
    proc, args = run(tmp_path, GOOD, ci="1")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    sl = args["swiftlint"]
    assert "--strict" in sl
    assert sl[sl.index("--config") + 1] == "ui/ios/lint/swiftlint.yml"
    assert sl[sl.index("--baseline") + 1] == "ui/ios/lint/swiftlint-baseline.json"
    assert sl[-1].endswith("tests/fixtures/ios/Good/GoodScreen.swift")
    sf = args["swiftformat"]
    assert "--lint" in sf and "--lenient" not in sf
    assert sf[sf.index("--config") + 1] == "ui/ios/.swiftformat"


def test_s218_local_tier_warns_only(tmp_path):
    proc, args = run(tmp_path, GOOD)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "--strict" not in args["swiftlint"]
    assert "--baseline" in args["swiftlint"], "the baseline filters both tiers"
    assert "--lenient" in args["swiftformat"]


def test_s218_ci_is_true_on_github_and_counts_as_the_ci_tier(tmp_path):
    _, args = run(tmp_path, GOOD, ci="true")
    assert "--strict" in args["swiftlint"]


def repo(tmp_path):
    r = tmp_path / "child"
    r.mkdir()
    git = lambda *a: subprocess.run(["git", "-C", str(r), *a], check=True, capture_output=True)
    git("init", "-q", "-b", "main")
    for name in ("Kept.swift", "Changed.swift", "Note.md"):
        (r / name).write_text("import SwiftUI\n", encoding="utf-8")
    git("add", "-A")
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "base")
    return r


KIT = {"SWIFTLINT_CONFIG": str(ILINT / "swiftlint.yml"), "SWIFTLINT_BASELINE": str(BASELINE), "SWIFTFORMAT_CONFIG": str(ROOT / "ui" / "ios" / ".swiftformat")}


def test_s218_only_the_changed_and_new_swift_files_are_linted(tmp_path):
    r = repo(tmp_path)
    (r / "Changed.swift").write_text("import SwiftUI\nimport UIKit\n", encoding="utf-8")
    (r / "New.swift").write_text("import SwiftUI\n", encoding="utf-8")
    (r / "Note.md").write_text("changed\n", encoding="utf-8")
    proc, args = run(tmp_path, cwd=r, env={"LINT_BASE": "HEAD", **KIT})
    assert proc.returncode == 0, proc.stdout + proc.stderr
    files = {a for a in args["swiftlint"] if a.endswith(".swift")}
    assert files == {"Changed.swift", "New.swift"}
    assert {a for a in args["swiftformat"] if a.endswith(".swift")} == files


def test_s218_nothing_changed_exits_0_and_runs_no_tool(tmp_path):
    r = repo(tmp_path)
    proc, args = run(tmp_path, cwd=r, env={"LINT_BASE": "HEAD", **KIT})
    assert proc.returncode == 0 and args == {}, proc.stdout + proc.stderr
    assert "no Swift file changed" in proc.stdout


def test_s218_a_missing_swiftlint_fails_the_ci_tier_and_only_warns_locally(tmp_path):
    gone = {"SWIFTLINT_BIN": str(tmp_path / "no-swiftlint"), "SWIFTFORMAT_BIN": str(tmp_path / "no-swiftformat")}
    strict, _ = run(tmp_path, GOOD, ci="1", env=gone)
    assert strict.returncode != 0 and "swiftlint is not installed" in strict.stdout + strict.stderr
    local, _ = run(tmp_path, GOOD, env=gone)
    assert local.returncode == 0 and "swiftlint is not installed" in local.stdout + local.stderr


def test_s218_the_baseline_is_committed_empty_and_protected():
    assert json.loads(BASELINE.read_text(encoding="utf-8")) == [], "SwiftLint 0.65.1 reads a JSON array of violations; the kit starts clean"
    globs = [l.strip() for l in (ROOT / "scripts" / "protected_paths.txt").read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    rel = BASELINE.relative_to(ROOT).as_posix()
    assert any(fnmatch.fnmatchcase(rel, g) for g in globs), f"{rel} matches no glob in scripts/protected_paths.txt"


def swift_rules():
    """{rule id: (regex, excluded pattern or None)} from the custom_rules block of swiftlint.yml."""
    rules, current = {}, None
    for line in (ILINT / "swiftlint.yml").read_text(encoding="utf-8").splitlines():
        if m := re.match(r"^  (\w+):\s*$", line):
            current = m.group(1)
            rules[current] = [None, None]
        elif m := re.match(r"^    regex: '(.*)'\s*$", line):
            rules[current][0] = re.compile(m.group(1), re.M)
        elif m := re.match(r"^    excluded: '(.*)'\s*$", line):
            rules[current][1] = re.compile(m.group(1))
    return {k: tuple(v) for k, v in rules.items() if v[0]}


TOKEN_RULES = {"no_raw_color", "no_fixed_font_size", "no_custom_font", "no_number_in_layout_modifier", "no_number_in_spacing"}


def test_s218_the_tokens_fixture_breaks_the_token_rules_but_is_excluded_from_them():
    tokens = FIX / "Good" / "Tokens.swift"
    rules = swift_rules()
    text = tokens.read_text(encoding="utf-8")
    for rule in ("no_raw_color", "no_fixed_font_size", "no_custom_font"):
        rx, excluded = rules[rule]
        assert rx.search(text), f"{rule}: the Tokens fixture must hold what the rule refuses"
        assert excluded and excluded.fullmatch(tokens.as_posix()), f"{rule}: Tokens.swift is not excluded"
    assert {r for r, (_, ex) in rules.items() if ex} == TOKEN_RULES, "exactly the token rules skip Tokens.swift"
    for rule, (rx, excluded) in rules.items():
        if not excluded:
            assert not rx.search(text), f"{rule} fires on the Tokens fixture, so the Good folder fails"


@pytest.mark.parametrize("bad, rule", [
    ("Color(red: 1, green: 0, blue: 0)", "no_raw_color"),
    ("UIColor(red: 1, green: 0, blue: 0, alpha: 1)", "no_raw_color"),
    (".font(.system(size: 17))", "no_fixed_font_size"),
    ("Font.custom(\"Inter\", size: 17)", "no_custom_font"),
    ("import SnapKit", "no_import_outside_allowlist"),
    ("import UIKit", "no_import_outside_allowlist"),
])
def test_s218_each_named_bad_snippet_breaks_its_rule(bad, rule):
    rx, _ = swift_rules()[rule]
    assert rx.search(bad), f"{rule} does not match {bad!r}"


@pytest.mark.parametrize("good", ["Color.red", "Color(\"Brand\")", ".font(.body)", "Tokens.font", "import SwiftUI", "import Foundation", "@testable import ShipQuickUI"])
def test_s218_a_good_snippet_breaks_no_rule(good):
    for rule, (rx, _) in swift_rules().items():
        assert not rx.search(good), f"{rule} fires on {good!r}"


def test_s218_swiftformat_config_and_ci_job_run_the_two_tiers():
    options = [l for l in (ROOT / "ui" / "ios" / ".swiftformat").read_text(encoding="utf-8").splitlines() if l.startswith("--")]
    assert any(re.match(r"--swift-?version\s+\d", l) for l in options), "the config pins the Swift version"
    assert not any(l.startswith(("--lint", "--lenient")) for l in options), "lint mode is the runner's flag, so the same file serves `swiftformat .` too"
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    job = ci[ci.index("  ui-ios-lint:"):ci.index("  secret-scan:")]
    assert "CI=1 bash ui/tool/ios_lint.sh" in job and "CI= bash ui/tool/ios_lint.sh" in job, "both tiers run through the runner"
    assert re.search(r"SwiftFormat/releases/download/\d+\.\d+\.\d+/swiftformat\.zip", job) and job.count("shasum -a 256 -c") >= 2, "SwiftFormat is pinned by version and SHA-256 like SwiftLint"
    assert "timeout-minutes:" in job


def test_s218_a_missing_base_ref_fails_the_ci_tier_and_only_warns_locally(tmp_path):
    r = repo(tmp_path)
    (r / "Bad.swift").write_text("let c = Color(red: 1, green: 0, blue: 0)\n", encoding="utf-8")
    git = lambda *a: subprocess.run(["git", "-C", str(r), *a], check=True, capture_output=True)
    git("add", "-A")
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "bad")
    # No LINT_BASE: the default origin/dev does not exist here, like a shallow checkout.
    strict, args = run(tmp_path, cwd=r, ci="1", env=KIT)
    out = strict.stdout + strict.stderr
    assert strict.returncode != 0 and "LINT_BASE" in out and "fetch-depth" in out, out
    local, _ = run(tmp_path, cwd=r, env=KIT)
    assert local.returncode == 0 and "LINT_BASE" in local.stdout + local.stderr


def test_s218_a_missing_swiftformat_alone_fails_the_ci_tier_and_only_warns_locally(tmp_path):
    gone = {"SWIFTFORMAT_BIN": str(tmp_path / "no-swiftformat")}
    strict, _ = run(tmp_path, GOOD, ci="1", env=gone)
    assert strict.returncode != 0 and "swiftformat is not installed" in strict.stdout + strict.stderr
    local, _ = run(tmp_path, GOOD, env=gone)
    assert local.returncode == 0 and "swiftformat is not installed" in local.stdout + local.stderr


def test_s218_an_adopted_child_gets_configs_that_exist(tmp_path):
    """#366 review: adopt.sh --platforms ios puts the config at ui/platforms/lint/swiftlint.yml and copies no
    baseline and no .swiftformat; the runner, run by its kit path, must pass only paths that exist."""
    r = repo(tmp_path)
    (r / "ui" / "platforms" / "lint").mkdir(parents=True)
    (r / "ui" / "platforms" / "lint" / "swiftlint.yml").write_text("included: []\n", encoding="utf-8")
    proc, args = run(tmp_path, "Kept.swift", cwd=r, ci="1")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    sl, sf = args["swiftlint"], args["swiftformat"]
    assert sl[sl.index("--config") + 1] == "ui/platforms/lint/swiftlint.yml"
    for flag, a in (("--config", sl), ("--baseline", sl), ("--config", sf)):
        if flag in a:
            p = a[a.index(flag) + 1]
            assert (r / p).is_file(), f"{flag} {p} does not exist in the child"
