// Template: the detail of one item. Copy it, then change only the content (rule 38).
import SwiftUI

public struct DetailTemplate: View {
    @State private var confirmDelete = false

    public init() {}

    public var body: some View {
        NavigationStack {
            Form {
                Section {
                    LabeledContent("Status", value: "Active")
                    LabeledContent("Owner", value: "Name")
                    LabeledContent("Updated", value: "Today")
                }
                Section("Notes") {
                    Text("A short note about this item. Long text wraps.")
                        .textSelection(.enabled)
                }
                Section {
                    Button("Delete item", role: .destructive) { confirmDelete = true }
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
