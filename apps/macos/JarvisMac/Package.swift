// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "JarvisMac",
    platforms: [.macOS(.v14)],
    targets: [
        .executableTarget(
            name: "JarvisMac",
            path: "Sources/JarvisMac",
            exclude: ["Info.plist"],
            // Embeds Info.plist into the raw executable so macOS shows the
            // custom microphone/speech-recognition permission prompts even
            // without a full .app bundle. Standard trick for SPM CLI tools
            // that need TCC-gated APIs — see the macOS app README.
            linkerSettings: [
                .unsafeFlags([
                    "-Xlinker", "-sectcreate",
                    "-Xlinker", "__TEXT",
                    "-Xlinker", "__info_plist",
                    "-Xlinker", "Sources/JarvisMac/Info.plist",
                ])
            ]
        )
    ]
)
