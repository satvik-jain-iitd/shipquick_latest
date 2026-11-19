// Template: settings. Copy it, then change only the content (rule 38).
import SwiftUI

public struct SettingsTemplate: View {
    enum Appearance: String, CaseIterable, Identifiable {
        case system = "System", light = "Light", dark = "Dark"
        var id: Self { self }
    }

    @State private var notifications = true
    @State private var appearance = Appearance.system
    @State private var confirmSignOut = false

    public init() {}

    /// Section titles in the muted token colour (4.5:1 or more), not the system grey the audit flags.
    private func sectionTitle(_ text: String) -> some View {
        Text(text).foregroundStyle(ShipQuickTokens.Colors.onSurfaceMuted)
    }

    public var body: some View {
        NavigationStack {
            Form {
                Section {
                    NavigationLink("Profile") { Text("Profile") }
                    NavigationLink("Privacy") { Text("Privacy") }
                } header: { sectionTitle("Account") }
                Section {
                    Toggle("Notifications", isOn: $notifications)
                    Picker("Appearance", selection: $appearance) {
                        ForEach(Appearance.allCases) { Text($0.rawValue).tag($0) }
                    }
                } header: { sectionTitle("Preferences") }
                Section {
                    Button("Sign out", role: .destructive) { confirmSignOut = true }
                        .foregroundStyle(ShipQuickTokens.Colors.error)
                }
            }
            .navigationTitle("Settings")
            .alert("Sign out?", isPresented: $confirmSignOut) {
                Button("Sign out", role: .destructive) {}
                Button("Cancel", role: .cancel) {}
            }
        }
    }
}

#Preview { SettingsTemplate() }
