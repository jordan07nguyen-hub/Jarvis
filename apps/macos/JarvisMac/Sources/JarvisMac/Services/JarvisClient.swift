import Foundation

/// Talks to the JARVIS backend's `/ws/chat` endpoint and publishes chat
/// state for SwiftUI views. Protocol matches
/// `backend/jarvis_backend/api/routes/websocket.py`:
/// send {"session_id", "message"}, receive a stream of
/// {"type": "chunk", "text"} frames then {"type": "done"} (or "error").
@MainActor
final class JarvisClient: ObservableObject {
    @Published var messages: [ChatMessage] = []
    @Published var isConnected: Bool = false
    @Published var isStreaming: Bool = false
    @Published var lastError: String?

    private var task: URLSessionWebSocketTask?
    private let sessionID = UUID().uuidString

    func connect() {
        guard task == nil else { return }
        guard let token = AppConfig.backendAPIToken, !token.isEmpty else {
            lastError = "Set JARVIS_API_TOKEN to the token printed by the backend on first run."
            return
        }

        var request = URLRequest(url: AppConfig.backendWebSocketURL)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")

        let session = URLSession(configuration: .default)
        let task = session.webSocketTask(with: request)
        self.task = task
        task.resume()
        isConnected = true
        listen()
    }

    func disconnect() {
        task?.cancel(with: .goingAway, reason: nil)
        task = nil
        isConnected = false
    }

    func send(_ text: String) {
        guard !text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return }
        if task == nil { connect() }

        messages.append(ChatMessage(role: .user, content: text))
        let reply = ChatMessage(role: .assistant, content: "")
        messages.append(reply)
        isStreaming = true

        let payload: [String: String] = ["session_id": sessionID, "message": text]
        guard let data = try? JSONSerialization.data(withJSONObject: payload),
              let json = String(data: data, encoding: .utf8) else { return }

        task?.send(.string(json)) { [weak self] error in
            if let error {
                Task { @MainActor in self?.lastError = error.localizedDescription }
            }
        }
    }

    private func listen() {
        task?.receive { [weak self] result in
            guard let self else { return }
            Task { @MainActor in
                switch result {
                case .failure(let error):
                    self.lastError = error.localizedDescription
                    self.isConnected = false
                    self.isStreaming = false
                case .success(let message):
                    if case .string(let text) = message {
                        self.handle(frame: text)
                    }
                    self.listen()
                }
            }
        }
    }

    private func handle(frame: String) {
        guard let data = frame.data(using: .utf8),
              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let type = json["type"] as? String
        else { return }

        switch type {
        case "chunk":
            guard let text = json["text"] as? String, var last = messages.last else { return }
            last.content += text
            messages[messages.count - 1] = last
        case "done":
            isStreaming = false
        case "error":
            isStreaming = false
            lastError = json["message"] as? String ?? "Unknown error"
        default:
            break
        }
    }
}
