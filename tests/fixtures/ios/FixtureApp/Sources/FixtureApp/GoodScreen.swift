// Fixture (story #221): the good screen. Only a kit template and kit tokens; the lint must pass it.
import ShipQuickUI
import SwiftUI

public struct GoodScreen: View {
    public init() {}

    public var body: some View {
        VStack(spacing: ShipQuickTokens.Spacing.md) {
            Text("Welcome")
                .font(ShipQuickTokens.Fonts.titleBold)
                .foregroundStyle(ShipQuickTokens.Colors.onSurface)
                .padding(.top, ShipQuickTokens.Spacing.lg)
            ListTemplate()
        }
        .background(ShipQuickTokens.Colors.background)
    }
}
