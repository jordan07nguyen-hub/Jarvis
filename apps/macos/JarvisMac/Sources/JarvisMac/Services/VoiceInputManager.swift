import AVFoundation
import Speech

/// Continuous on-device listening for the "Hey Jarvis" wake word.
///
/// Uses `requiresOnDeviceRecognition = true` — recognition runs locally
/// (no audio sent anywhere), which is both the private option and the
/// low-power one (see the "will it overheat" answer: this is designed to
/// idle at low CPU, unlike running a full local LLM). Opt-in only —
/// call `startContinuous()` explicitly; JARVIS never listens by default.
@MainActor
final class VoiceInputManager: NSObject, ObservableObject {
    @Published var isListening = false
    @Published var lastHeard = ""
    @Published var permissionError: String?

    /// Called with the words spoken immediately after "Hey Jarvis".
    var onCommand: ((String) -> Void)?

    private let wakePhrase = "hey jarvis"
    private let recognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
    private let audioEngine = AVAudioEngine()
    private var request: SFSpeechAudioBufferRecognitionRequest?
    private var task: SFSpeechRecognitionTask?
    private var shouldKeepListening = false

    func startContinuous() {
        guard !shouldKeepListening else { return }
        shouldKeepListening = true

        SFSpeechRecognizer.requestAuthorization { [weak self] status in
            Task { @MainActor in
                guard let self, self.shouldKeepListening else { return }
                guard status == .authorized else {
                    self.permissionError =
                        "Speech recognition not authorized — enable it in System Settings > Privacy & Security > Speech Recognition."
                    self.shouldKeepListening = false
                    return
                }
                self.requestMicAndStart()
            }
        }
    }

    func stop() {
        shouldKeepListening = false
        teardownSession()
    }

    private func requestMicAndStart() {
        AVCaptureDevice.requestAccess(for: .audio) { [weak self] granted in
            Task { @MainActor in
                guard let self, self.shouldKeepListening else { return }
                guard granted else {
                    self.permissionError =
                        "Microphone access not granted — enable it in System Settings > Privacy & Security > Microphone."
                    self.shouldKeepListening = false
                    return
                }
                self.beginSession()
            }
        }
    }

    private func beginSession() {
        guard let recognizer, recognizer.isAvailable else {
            permissionError = "Speech recognizer unavailable right now."
            shouldKeepListening = false
            return
        }

        let request = SFSpeechAudioBufferRecognitionRequest()
        request.shouldReportPartialResults = true
        request.requiresOnDeviceRecognition = true
        self.request = request

        let inputNode = audioEngine.inputNode
        let format = inputNode.outputFormat(forBus: 0)
        inputNode.installTap(onBus: 0, bufferSize: 1024, format: format) { buffer, _ in
            request.append(buffer)
        }

        audioEngine.prepare()
        do {
            try audioEngine.start()
        } catch {
            permissionError = "Could not start the audio engine: \(error.localizedDescription)"
            shouldKeepListening = false
            teardownSession()
            return
        }

        isListening = true
        permissionError = nil

        task = recognizer.recognitionTask(with: request) { [weak self] result, error in
            Task { @MainActor in
                guard let self else { return }
                if let result {
                    let transcript = result.bestTranscription.formattedString
                    self.lastHeard = transcript
                    self.checkForWakeWord(in: transcript)
                }
                if error != nil || (result?.isFinal ?? false) {
                    self.restartIfNeeded()
                }
            }
        }
    }

    private func checkForWakeWord(in transcript: String) {
        let lower = transcript.lowercased()
        guard let range = lower.range(of: wakePhrase) else { return }
        let command = String(lower[range.upperBound...]).trimmingCharacters(in: .whitespacesAndNewlines)
        guard !command.isEmpty else { return }
        onCommand?(command)
        restartIfNeeded()
    }

    private func restartIfNeeded() {
        teardownSession()
        if shouldKeepListening {
            beginSession()
        }
    }

    private func teardownSession() {
        task?.cancel()
        task = nil
        request?.endAudio()
        request = nil
        audioEngine.inputNode.removeTap(onBus: 0)
        if audioEngine.isRunning {
            audioEngine.stop()
        }
        isListening = false
    }
}
