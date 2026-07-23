import Foundation

enum AppConfig {
    /// Backend WebSocket URL. Override at build/run time by setting
    /// JARVIS_BACKEND_WS_URL in the environment (Xcode scheme or `swift run`).
    static var backendWebSocketURL: URL {
        if let raw = ProcessInfo.processInfo.environment["JARVIS_BACKEND_WS_URL"],
           let url = URL(string: raw) {
            return url
        }
        return URL(string: "ws://localhost:8000/ws/chat")!
    }
}
