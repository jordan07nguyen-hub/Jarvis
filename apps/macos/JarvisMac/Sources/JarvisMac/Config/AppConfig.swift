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

    /// Bearer token the backend requires on every request (see backend/README.md
    /// "Security" — printed to the console / saved to backend/data/api_token.txt
    /// on the backend's first run). Set JARVIS_API_TOKEN in the environment
    /// (Xcode scheme or `swift run`) to the same value.
    ///
    /// This is a placeholder for real secret storage: production use should
    /// read this from the macOS Keychain instead of the environment, once
    /// that's wired up (see ROADMAP.md).
    static var backendAPIToken: String? {
        ProcessInfo.processInfo.environment["JARVIS_API_TOKEN"]
    }
}
