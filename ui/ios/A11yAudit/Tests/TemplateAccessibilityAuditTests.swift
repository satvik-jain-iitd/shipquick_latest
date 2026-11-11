// Story #220: one accessibility audit per template (iOS 17+). performAccessibilityAudit() checks contrast,
// Dynamic Type, hit regions (44 pt), element labels and more on the screen that is shown. A failure names the
// element and the issue. What no machine checks is in ../../ACCESSIBILITY.md, tagged review-only.
import XCTest

final class TemplateAccessibilityAuditTests: XCTestCase {
    /// Findings on Apple's own stock controls, drawn in system colours: rule 38 forbids a raw colour to fix them.
    /// Each is "<screen>|<check>|<element label>" (empty label: the audit named no element). A new finding, or a known
    /// one on another screen or element, still fails. Each has a row in ../../ACCESSIBILITY.md with its reason.
    /// shortcut: matched by label, not by element frame; drop an entry when Apple's control passes or when the
    /// templates get contrast-checked token colours.
    private let knownSystemFindings: Set<String> = [
        "ListTemplate|Dynamic Type font sizes are unsupported|",
        "ListTemplate|Text clipped|",
        "ListTemplate|Text clipped|Search",
        "SettingsTemplate|Contrast nearly passed|",
        "SettingsTemplate|Text clipped|System",
        "SettingsTemplate|Text clipped|Appearance",
        "SignInTemplate|Contrast failed|Create account",
        "SignInTemplate|Contrast failed|Sign in",
        "SignInTemplate|Contrast nearly passed|",
        "StepFlowTemplate|Hit area is too small|",
        "StepFlowTemplate|Contrast nearly passed|One line on what the app does.",
        "StepFlowTemplate|Contrast nearly passed|Continue",
    ]

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
        // Every new issue is collected first, so one red run names all of them: the check, the element type and its label.
        var found: [String] = []
        try app.performAccessibilityAudit(for: .all) { issue in
            let key = "\(screen)|\(issue.compactDescription)|\(issue.element?.label ?? "")"
            if !self.knownSystemFindings.contains(key) {
                let element = issue.element.map { "type \($0.elementType.rawValue) '\($0.label)' id '\($0.identifier)'" } ?? "no element"
                found.append("\(issue.compactDescription): \(element)")
            }
            return true
        }
        XCTAssertTrue(found.isEmpty, "\(screen): \(found.count) accessibility issues\n" + found.joined(separator: "\n"))
    }
}
