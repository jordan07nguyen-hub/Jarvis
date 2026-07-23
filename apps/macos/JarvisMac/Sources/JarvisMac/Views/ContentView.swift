import SwiftUI

struct ContentView: View {
    @EnvironmentObject private var client: JarvisClient
    @State private var draft: String = ""

    var body: some View {
        VStack(spacing: 0) {
            header

            ScrollViewReader { proxy in
                ScrollView {
                    VStack(alignment: .leading, spacing: 10) {
                        ForEach(client.messages) { message in
                            MessageBubble(message: message)
                                .id(message.id)
                        }
                    }
                    .padding()
                }
                .onChange(of: client.messages) { _, _ in
                    if let last = client.messages.last {
                        withAnimation { proxy.scrollTo(last.id, anchor: .bottom) }
                    }
                }
            }

            if let error = client.lastError {
                Text(error)
                    .font(.caption)
                    .foregroundColor(.red)
                    .padding(.horizontal)
            }

            inputBar
        }
        .onAppear { client.connect() }
    }

    private var header: some View {
        HStack {
            Circle()
                .fill(client.isConnected ? Color.green : Color.gray)
                .frame(width: 8, height: 8)
            Text("JARVIS")
                .font(.headline)
            Spacer()
        }
        .padding()
    }

    private var inputBar: some View {
        HStack {
            TextField("Ask JARVIS…", text: $draft, onCommit: sendDraft)
                .textFieldStyle(.roundedBorder)
            Button("Send", action: sendDraft)
                .disabled(draft.trimmingCharacters(in: .whitespaces).isEmpty)
        }
        .padding()
    }

    private func sendDraft() {
        let text = draft
        draft = ""
        client.send(text)
    }
}
