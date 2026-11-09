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

    public var body: some View {
        NavigationStack {
            Form {
                Section("Account") {
                    NavigationLink("Profile") { Text("Profile") }
                    NavigationLink("Privacy") { Text("Privacy") }
                }
                Section("Preferences") {
                    Toggle("Notifications", isOn: $notifications)
                    Picker("Appearance", selection: $appearance) {
                        ForEach(Appearance.allCases) { Text($0.rawValue).tag($0) }
                    }
                }
                Section {
                    Button("Sign out", role: .destructive) { confirmSignOut = true }
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
