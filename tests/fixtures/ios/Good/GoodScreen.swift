// Fixture (story #185): a screen with no hand-drawn UI. The lint must pass it with no finding.
// SwiftLint reads text only; this file is never compiled, so Tokens need not exist.
import SwiftUI
import Foundation

struct GoodScreen: View {
    @State private var name = ""

    var body: some View {
        VStack(spacing: Tokens.space3) {
            Text("Hello").font(.body).padding(.top, Tokens.space2)
            TextField("Name", text: $name)
            Button("Go") {}.buttonStyle(.borderedProminent)
            Image(systemName: "star").frame(width: Tokens.icon48, height: Tokens.icon48)
        }
    }
}
