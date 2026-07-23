import SwiftUI

@main
struct JarvisApp: App {
    @StateObject private var client = JarvisClient()
    @StateObject private var voiceOutput = VoiceOutput()
    @StateObject private var voiceInput = VoiceInputManager()

    var body: some Scene {
        WindowGroup("JARVIS") {
            ContentView()
                .environmentObject(client)
                .environmentObject(voiceOutput)
                .environmentObject(voiceInput)
                .frame(minWidth: 420, minHeight: 560)
        }
        .windowResizability(.contentSize)
    }
}
