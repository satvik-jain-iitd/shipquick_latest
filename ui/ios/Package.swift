// swift-tools-version:5.9
// ShipQuickUI: the kit's iOS screen templates, built only from Apple's SwiftUI (rule 38). No dependencies.
import PackageDescription

let package = Package(
    name: "ShipQuickUI",
    platforms: [.iOS(.v17)],
    products: [
        .library(name: "ShipQuickUI", targets: ["ShipQuickUI"]),
    ],
    targets: [
        .target(name: "ShipQuickUI", path: "templates"),
    ]
)
