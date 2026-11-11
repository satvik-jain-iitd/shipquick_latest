// Story #219: one snapshot test per template, over the whole matrix, with swift-snapshot-testing.
// The reference images live in __Snapshots__/TemplateSnapshotTests/ and are recorded on CI, never on a Mac
// (another simulator draws differently). Record mode: the env var SNAPSHOT_TESTING_RECORD=all, which the CI job
// passes as TEST_RUNNER_SNAPSHOT_TESTING_RECORD when it is dispatched with record=true. See ../SNAPSHOTS.md.
import SnapshotTesting
import SwiftUI
import XCTest
@testable import ShipQuickUI

final class TemplateSnapshotTests: XCTestCase {
    func testSignInTemplate() { matrix(SignInTemplate()) }
    func testListTemplate() { matrix(ListTemplate()) }
    func testDetailTemplate() { matrix(DetailTemplate()) }
    func testSettingsTemplate() { matrix(SettingsTemplate()) }
    func testStepFlowTemplate() { matrix(StepFlowTemplate()) }

    /// Light and dark, the smallest and the largest Dynamic Type size, iPhone SE and iPhone Pro Max: eight images per template.
    private func matrix<V: View>(_ view: V, file: StaticString = #filePath, testName: String = #function, line: UInt = #line) {
        let schemes: [(String, UIUserInterfaceStyle)] = [("light", .light), ("dark", .dark)]
        let sizes: [(String, UIContentSizeCategory)] = [("xs", .extraSmall), ("ax5", .accessibilityExtraExtraExtraLarge)]
        let devices: [(String, ViewImageConfig)] = [("se", .iPhoneSe), ("promax", .iPhone13ProMax)]
        for (scheme, style) in schemes {
            for (size, category) in sizes {
                for (device, config) in devices {
                    // shortcut: displayScale 1 keeps every PNG far under the 500 KB commit limit; switch to the device's own
                    // scale when a 1x image hides a real pixel bug.
                    let traits = UITraitCollection(traitsFrom: [
                        UITraitCollection(userInterfaceStyle: style),
                        UITraitCollection(preferredContentSizeCategory: category),
                        UITraitCollection(displayScale: 1),
                    ])
                    assertSnapshot(
                        of: view,
                        as: .image(perceptualPrecision: 0.98, layout: .device(config: config), traits: traits),
                        named: "\(scheme)-\(size)-\(device)",
                        file: file, testName: testName, line: line
                    )
                }
            }
        }
    }
}
