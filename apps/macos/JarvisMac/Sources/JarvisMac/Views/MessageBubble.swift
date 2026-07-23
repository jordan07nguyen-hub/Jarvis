import SwiftUI

struct MessageBubble: View {
    let message: ChatMessage

    private var isUser: Bool { message.role == .user }

    var body: some View {
        HStack {
            if isUser { Spacer(minLength: 40) }
            Text(message.content.isEmpty ? "…" : message.content)
                .padding(.horizontal, 12)
                .padding(.vertical, 8)
                .background(isUser ? Color.accentColor.opacity(0.85) : Color.gray.opacity(0.2))
                .foregroundColor(isUser ? .white : .primary)
                .clipShape(RoundedRectangle(cornerRadius: 12))
            if !isUser { Spacer(minLength: 40) }
        }
    }
}
