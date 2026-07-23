import SwiftUI

@main
struct JarvisApp: App {
    @StateObject private var client = JarvisClient()

    var body: some Scene {
        WindowGroup("JARVIS") {
            ContentView()
                .environmentObject(client)
                .frame(minWidth: 420, minHeight: 560)
        }
        .windowResizability(.contentSize)
    }
}
