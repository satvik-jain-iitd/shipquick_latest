// Template: the detail of one item. Copy it, then change only the content (rule 38).
import SwiftUI

public struct DetailTemplate: View {
    @State private var confirmDelete = false

    public init() {}

    public var body: some View {
        NavigationStack {
            Form {
                Section {
                    LabeledContent("Status") { Text("Active").foregroundStyle(ShipQuickTokens.Colors.onSurfaceMuted) }
                    LabeledContent("Owner") { Text("Name").foregroundStyle(ShipQuickTokens.Colors.onSurfaceMuted) }
                    LabeledContent("Updated") { Text("Today").foregroundStyle(ShipQuickTokens.Colors.onSurfaceMuted) }
                }
                Section {
                    Text("A short note about this item. Long text wraps.")
                        .textSelection(.enabled)
                } header: {
                    Text("Notes").foregroundStyle(ShipQuickTokens.Colors.onSurfaceMuted)
                }
                Section {
                    Button("Delete item", role: .destructive) { confirmDelete = true }
                        .foregroundStyle(ShipQuickTokens.Colors.error)
                }
            }
            .navigationTitle("Item")
            .toolbar {
                ToolbarItem(placement: .primaryAction) {
                    ShareLink(item: "Item")
                }
            }
            .confirmationDialog("Delete this item?", isPresented: $confirmDelete, titleVisibility: .visible) {
                Button("Delete", role: .destructive) {}
            }
        }
    }
}

#Preview { DetailTemplate() }
