"""Story #220 (S5e, rule 38): an XCUITest accessibility audit per iOS template screen.

Text checks only (this Mac has no Xcode; the macOS CI job runs the UI tests). A small host app shows one template
picked by a launch argument, one XCUITest per template launches it and calls performAccessibilityAudit() (iOS 17+),
an XcodeGen spec makes the app and the UI test target, the CI job ui-ios-snapshots generates the project with a
pinned, checksummed XcodeGen and runs the audit, and ui/ios/ACCESSIBILITY.md lists the HIG items no machine checks,
each tagged review-only."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IOS = ROOT / "ui" / "ios"
AUDIT = IOS / "A11yAudit"
CI = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
TEMPLATES = sorted(p.stem for p in (IOS / "templates").glob("*Template.swift"))


def job(name):
    m = re.search(rf"^  {name}:\n(.*?)(?=^  [a-z][a-z-]*:\s*$|\Z)", CI, re.M | re.S)
    assert m, f"no job {name} in ci.yml"
    return m.group(1)


def test_s220_one_audit_test_per_template_calls_perform_accessibility_audit():
    text = (AUDIT / "Tests" / "TemplateAccessibilityAuditTests.swift").read_text(encoding="utf-8")
    assert "import XCTest" in text and "XCUIApplication()" in text
    assert "performAccessibilityAudit(" in text
    assert TEMPLATES, "no templates"
    for name in TEMPLATES:
        assert re.search(rf'func test{name}\(\) throws \{{ try audit\("{name}"\) \}}', text), f"no audit test for {name}"


def test_s220_the_host_app_shows_every_template_by_launch_argument():
    text = (AUDIT / "Host" / "A11yHostApp.swift").read_text(encoding="utf-8")
    assert "@main" in text and "import ShipQuickUI" in text
    for name in TEMPLATES:
        assert f'case "{name}": {name}()' in text, f"the host app cannot show {name}"


def test_s220_the_xcodegen_spec_has_the_app_and_a_ui_test_target():
    spec = (AUDIT / "project.yml").read_text(encoding="utf-8")
    assert re.search(r"^  ShipQuickUI:\n    path: \.\.$", spec, re.M), "the spec does not use the local ShipQuickUI package"
    assert "type: application" in spec and "type: bundle.ui-testing" in spec
    assert 'iOS: "17.0"' in spec  # performAccessibilityAudit needs iOS 17
    assert "- target: A11yHost" in spec
    # the generated project is never committed (no .gitignore entry: check_disable_comments refuses a new one without an ADR)
    assert not list(AUDIT.glob("*.xcodeproj")), "the generated project is committed"


def test_s220_the_audit_runs_in_the_snapshot_job_with_a_pinned_xcodegen():
    j = job("ui-ios-snapshots")
    assert re.search(r"releases/download/\d+\.\d+\.\d+/xcodegen\.zip", j), "XcodeGen is not pinned to a release"
    assert re.search(r"shasum -a 256 -c", j) and re.search(r"[0-9a-f]{64}", j), "the XcodeGen zip is not checksummed"
    assert "xcodegen generate --spec ui/ios/A11yAudit/project.yml" in j
    assert "xcodebuild test -project ui/ios/A11yAudit/A11yAudit.xcodeproj -scheme A11yHost" in j
    assert "platform=iOS Simulator,name=iPhone 16,OS=18.5" in j
    assert re.search(r"^    timeout-minutes: \d+$", j, re.M)
    # the audit must run after the snapshots fail too, so one red never hides the other
    assert re.search(r"- name: Run the accessibility audit[^\n]*\n        if: \$\{\{ !cancelled\(\) \}\}", j)


def test_s220_the_review_only_list_names_what_no_machine_checks():
    text = (IOS / "ACCESSIBILITY.md").read_text(encoding="utf-8")
    assert "performAccessibilityAudit" in text and "TemplateAccessibilityAuditTests.swift" in text
    rows = [line for line in text.splitlines() if "`review-only`" in line]
    assert len(rows) >= 4, "too few review-only items"
    body = " ".join(rows).lower()
    for item in ("navigation", "gesture", "voiceover", "reduce motion"):
        assert item in body, item
    assert "ACCESSIBILITY.md" in (IOS / "README.md").read_text(encoding="utf-8")
