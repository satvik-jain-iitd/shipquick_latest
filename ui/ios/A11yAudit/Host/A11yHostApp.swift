// Story #220: the host app for the accessibility audit. It shows one template, picked by `-screen <Name>`
// (a launch argument lands in UserDefaults). A new template gets one case here and one test in Tests/.
import ShipQuickUI
import SwiftUI

@main
struct A11yHostApp: App {
    var body: some Scene {
        WindowGroup { screen }
    }

    @ViewBuilder private var screen: some View {
        switch UserDefaults.standard.string(forKey: "screen") ?? "" {
        case "SignInTemplate": SignInTemplate()
        case "ListTemplate": ListTemplate()
        case "DetailTemplate": DetailTemplate()
        case "SettingsTemplate": SettingsTemplate()
        case "StepFlowTemplate": StepFlowTemplate()
        default: Text("Unknown screen")
        }
    }
}
