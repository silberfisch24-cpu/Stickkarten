// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "StickCore",
    platforms: [.iOS(.v16), .macOS(.v13)],
    products: [
        .library(name: "StickCore", targets: ["StickCore"]),
        .library(name: "StickPDF", targets: ["StickPDF"]),
    ],
    targets: [
        // Reine Fachlogik (Foundation only) — Port der Web-App src/StickkartenGeneratorV4.jsx.
        .target(name: "StickCore"),
        // Vektor-PDF (CoreGraphics/CoreText): Lochmuster 1:1 und Anleitung.
        .target(name: "StickPDF", dependencies: ["StickCore"]),
        .testTarget(
            name: "StickCoreTests",
            dependencies: ["StickCore"],
            resources: [.copy("Golden")]
        ),
        .testTarget(
            name: "StickPDFTests",
            dependencies: ["StickPDF", "StickCore"]
        ),
    ]
)
