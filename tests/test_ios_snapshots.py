"""Story #219 (S5d, rule 38): snapshot tests and Prefire for ui/ios.

Text checks only (this Mac has no Xcode; the macOS CI job runs the Swift tests). The ui/ios package has a
test target with swift-snapshot-testing and Prefire pinned to exact versions, one XCTest per template that
loops over light and dark, the smallest and the largest Dynamic Type size, iPhone SE and iPhone Pro Max,
every template has a #Preview (Prefire's input), ci.yml runs the tests on a pinned Xcode and simulator with
a timeout and the gate waits for the job, the reference-image folder is a protected path, and
ui/ios/SNAPSHOTS.md tells how the references are recorded and refreshed."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IOS = ROOT / "ui" / "ios"
PACKAGE = (IOS / "Package.swift").read_text(encoding="utf-8")
CI = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
TEST_DIR = IOS / "ShipQuickUITests"
SNAPSHOTS = TEST_DIR / "__Snapshots__"
TEMPLATES = sorted(p.stem for p in (IOS / "templates").glob("*Template.swift"))


def job(name):
    """The text of one ci.yml job: from its key to the next two-space key."""
    m = re.search(rf"^  {name}:\n(.*?)(?=^  [a-z][a-z-]*:\s*$|\Z)", CI, re.M | re.S)
    assert m, f"no job {name} in ci.yml"
    return m.group(1)


def test_s219_the_package_has_a_test_target_with_snapshot_testing_and_prefire_pinned_exactly():
    assert re.search(r'url: "https://github\.com/pointfreeco/swift-snapshot-testing(?:\.git)?",\s*exact: "\d+\.\d+\.\d+"', PACKAGE)
    assert re.search(r'url: "https://github\.com/BarredEwe/Prefire(?:\.git)?",\s*exact: "\d+\.\d+\.\d+"', PACKAGE)
    test = PACKAGE.split(".testTarget(", 1)[1]
    assert 'name: "ShipQuickUITests"' in test
    assert '.product(name: "SnapshotTesting", package: "swift-snapshot-testing")' in test
    assert '.plugin(name: "PrefireTestsPlugin", package: "Prefire")' in test
    # rule 38: the library a child resolves still has no dependency; the test packages sit behind the env guard
    guard = 'environment["SHIPQUICK_SNAPSHOTS"]'
    assert guard in PACKAGE
    assert ".package(" not in PACKAGE.split(guard, 1)[0]
    assert (IOS / ".prefire.yml").exists()
    assert "target: ShipQuickUI" in (IOS / ".prefire.yml").read_text(encoding="utf-8")


def test_s219_one_snapshot_test_per_template_over_the_whole_matrix():
    text = (TEST_DIR / "TemplateSnapshotTests.swift").read_text(encoding="utf-8")
    assert "import SnapshotTesting" in text and "import XCTest" in text
    assert TEMPLATES, "no templates"
    for name in TEMPLATES:
        assert re.search(rf"func test{name}\(\)", text), f"no test for {name}"
        assert f"{name}()" in text
    for cell in (".light", ".dark", ".extraSmall", ".accessibilityExtraExtraExtraLarge", ".iPhoneSe", "ProMax"):
        assert cell in text, cell
    assert "SNAPSHOT_TESTING_RECORD" in text  # the comment tells how record mode is switched on


def test_s219_every_template_has_a_preview_for_prefire():
    for name in TEMPLATES:
        text = (IOS / "templates" / f"{name}.swift").read_text(encoding="utf-8")
        assert re.search(r"^#Preview\s*\{", text, re.M), f"{name} has no #Preview"


def test_s219_ci_runs_the_snapshot_tests_on_a_pinned_xcode_and_simulator_with_a_timeout():
    j = job("ui-ios-snapshots")
    assert "needs: [ui-changes]" in j and "needs.ui-changes.outputs.ui == 'true'" in j
    assert "runs-on: macos-15" in j
    assert re.search(r"^    timeout-minutes: \d+$", j, re.M)
    assert "xcode-select -s /Applications/Xcode_16.4.app" in j
    assert "xcodebuild test" in j and "platform=iOS Simulator,name=iPhone 16,OS=18.5" in j
    # #375 review: SPM makes exactly one scheme, the product's, and xcodebuild -list -json prints a non-JSON line after
    # the JSON once Prefire is resolved, so the job names the scheme and never parses xcodebuild output
    assert "xcodebuild test -scheme ShipQuickUI " in j
    assert "json.load" not in j
    assert "TEST_RUNNER_SNAPSHOT_TESTING_RECORD" in j
    assert "upload-artifact@" in j and "__Snapshots__" in j
    assert re.search(r"^  workflow_dispatch:\n    inputs:\n      record:", CI, re.M), "ci.yml has no record input"
    gate = job("gate")
    assert "ui-ios-snapshots" in gate.split("needs: [", 1)[1].split("]", 1)[0]
    assert 'echo "ui-ios-snapshots: ${{ needs.ui-ios-snapshots.result }}"' in gate


def test_s219_the_reference_images_are_a_protected_path():
    lines = (ROOT / "scripts" / "protected_paths.txt").read_text(encoding="utf-8").splitlines()
    assert "ui/ios/ShipQuickUITests/__Snapshots__/*" in lines


def test_s219_the_doc_tells_how_references_are_recorded_and_refreshed():
    text = (IOS / "SNAPSHOTS.md").read_text(encoding="utf-8")
    for word in ("record", "workflow_dispatch", "gh run download", "__Snapshots__", "protected", "Xcode 16.4", "iOS 18.5"):
        assert word in text, word
    readme = (IOS / "README.md").read_text(encoding="utf-8")
    assert "SNAPSHOTS.md" in readme
