import Foundation

enum ChatRole: String, Codable, Equatable {
    case user
    case assistant
    case system
}

struct ChatMessage: Identifiable, Equatable {
    let id: UUID
    var role: ChatRole
    var content: String

    init(id: UUID = UUID(), role: ChatRole, content: String) {
        self.id = id
        self.role = role
        self.content = content
    }
}
