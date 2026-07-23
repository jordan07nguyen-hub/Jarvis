import SwiftUI

struct ContentView: View {
    @EnvironmentObject private var client: JarvisClient
    @EnvironmentObject private var voiceOutput: VoiceOutput
    @EnvironmentObject private var voiceInput: VoiceInputManager
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

            if let error = voiceInput.permissionError {
                Text(error)
                    .font(.caption)
                    .foregroundColor(.orange)
                    .padding(.horizontal)
            }

            inputBar
        }
        .onAppear {
            client.connect()
            client.onAssistantReplyComplete = { [weak voiceOutput] text in
                voiceOutput?.speak(text)
            }
            voiceInput.onCommand = { [weak client] command in
                client?.send(command)
            }
        }
    }

    private var header: some View {
        HStack {
            Circle()
                .fill(client.isConnected ? Color.green : Color.gray)
                .frame(width: 8, height: 8)
            Text("JARVIS")
                .font(.headline)
            Spacer()

            if voiceOutput.isSpeaking {
                Image(systemName: "waveform")
                    .foregroundColor(.accentColor)
            }

            Toggle(isOn: $voiceOutput.isEnabled) {
                Image(systemName: voiceOutput.isEnabled ? "speaker.wave.2" : "speaker.slash")
            }
            .toggleStyle(.button)
            .help("Speak replies out loud")

            Toggle(isOn: Binding(
                get: { voiceInput.isListening },
                set: { listening in
                    if listening {
                        voiceInput.startContinuous()
                    } else {
                        voiceInput.stop()
                    }
                }
            )) {
                Image(systemName: voiceInput.isListening ? "mic.fill" : "mic.slash")
            }
            .toggleStyle(.button)
            .help("Listen for \"Hey Jarvis\"")
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
