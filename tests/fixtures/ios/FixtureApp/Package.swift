// swift-tools-version:5.9
// Fixture (story #221): a tiny SwiftUI app with one good and one bad screen, on the kit's own ui/ios module.
// CI compiles it (job ui-ios-compile) and lints both screens (job ui-ios-lint, ui/tool/ios_fixture_check.py).
import PackageDescription

let package = Package(
    name: "FixtureApp",
    platforms: [.iOS(.v17)],
    products: [
        .library(name: "FixtureApp", targets: ["FixtureApp"]),
    ],
    dependencies: [
        .package(path: "../../../../ui/ios"),
    ],
    targets: [
        .target(name: "FixtureApp", dependencies: [.product(name: "ShipQuickUI", package: "ios")]),
    ]
)
