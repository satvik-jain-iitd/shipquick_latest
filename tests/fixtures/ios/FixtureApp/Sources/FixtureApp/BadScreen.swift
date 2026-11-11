// Fixture (story #221): the bad screen. A raw colour, a fixed font size and a hand-drawn Shape.
// It compiles, so only the lint can catch it; the lint must fail it and name each rule.
import SwiftUI

struct Blob: Shape {
    func path(in rect: CGRect) -> Path {
        Path(ellipseIn: rect)
    }
}

public struct BadScreen: View {
    public init() {}

    public var body: some View {
        VStack {
            Text("Hello")
                .font(.system(size: 17))
                .foregroundStyle(Color(red: 0.2, green: 0.1, blue: 0.9))
            Blob()
        }
    }
}
