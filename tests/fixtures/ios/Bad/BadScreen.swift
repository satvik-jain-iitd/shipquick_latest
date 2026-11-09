// Fixture (story #185): a screen that breaks every iOS UI lint rule at least once. The lint must fail it.
// SwiftLint reads text only; this file is never compiled.
import SwiftUI
import UIKit
import SnapKit
import Combine

struct Blob: Shape {
    func path(in rect: CGRect) -> Path {
        Path { p in p.move(to: .zero) }
    }
}

struct Chip<T>: Hashable, LabelStyle {}

struct Both: View & ToggleStyle {}

struct Fancy: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View { configuration.label }
}

struct Wrapped: UIViewRepresentable {}

struct BadScreen: View {
    var body: some View {
        VStack(spacing: 24) {
            Text("Hello")
                .font(.system(size: 17))
                .font(Font.custom("Inter", size: 17))
                .foregroundStyle(Color(red: 0.2, green: 0.1, blue: 0.9))
                .padding(8)
            Canvas { context, size in }
            Canvas(opaque: true) { context, size in }
                .gesture(DragGesture())
                .onTapGesture { }
                .highPriorityGesture(TapGesture())
            Rectangle().fill(Color.init(red: 1, green: 0, blue: 0))
        }
    }
}
