// Story #220: one accessibility audit per template (iOS 17+). performAccessibilityAudit() checks contrast,
// Dynamic Type, hit regions (44 pt), element labels and more on the screen that is shown. A failure names the
// element and the issue. What no machine checks is in ../../ACCESSIBILITY.md, tagged review-only.
import XCTest

final class TemplateAccessibilityAuditTests: XCTestCase {
    override func setUp() { continueAfterFailure = false }

    func testSignInTemplate() throws { try audit("SignInTemplate") }
    func testListTemplate() throws { try audit("ListTemplate") }
    func testDetailTemplate() throws { try audit("DetailTemplate") }
    func testSettingsTemplate() throws { try audit("SettingsTemplate") }
    func testStepFlowTemplate() throws { try audit("StepFlowTemplate") }

    private func audit(_ screen: String) throws {
        let app = XCUIApplication()
        app.launchArguments = ["-screen", screen]
        app.launch()
        XCTAssertFalse(app.staticTexts["Unknown screen"].exists, "the host app has no case for \(screen)")
        try app.performAccessibilityAudit()
    }
}
