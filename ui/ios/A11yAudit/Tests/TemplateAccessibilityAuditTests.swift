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
        // Every issue is collected first, so one red run names all of them: the check, the element type and its label.
        var found: [String] = []
        try app.performAccessibilityAudit(for: .all) { issue in
            let element = issue.element.map { "type \($0.elementType.rawValue) '\($0.label)' id '\($0.identifier)'" } ?? "no element"
            found.append("\(issue.compactDescription): \(element)")
            return true
        }
        XCTAssertTrue(found.isEmpty, "\(screen): \(found.count) accessibility issues\n" + found.joined(separator: "\n"))
    }
}
