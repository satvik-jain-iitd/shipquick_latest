// Template: a searchable list that opens a detail. Copy it, then change only the content (rule 38).
import SwiftUI

public struct ListTemplate: View {
    struct Item: Identifiable, Hashable {
        let id = UUID()
        let title: String
        let symbol: String
    }

    @State private var query = ""
    private let items = [
        Item(title: "First item", symbol: "doc"),
        Item(title: "Second item", symbol: "folder"),
        Item(title: "Third item", symbol: "star"),
    ]

    private var shown: [Item] {
        query.isEmpty ? items : items.filter { $0.title.localizedCaseInsensitiveContains(query) }
    }

    public init() {}

    public var body: some View {
        NavigationStack {
            List(shown) { item in
                NavigationLink(value: item) {
                    Label(item.title, systemImage: item.symbol)
                }
            }
            .navigationTitle("Items")
            .navigationDestination(for: Item.self) { item in
                Text(item.title).navigationTitle(item.title)
            }
            .searchable(text: $query)
            .toolbar {
                ToolbarItem(placement: .primaryAction) {
                    Button("Add", systemImage: "plus") {}
                }
            }
            .overlay {
                if shown.isEmpty {
                    ContentUnavailableView.search(text: query)
                }
            }
        }
    }
}

#Preview { ListTemplate() }
