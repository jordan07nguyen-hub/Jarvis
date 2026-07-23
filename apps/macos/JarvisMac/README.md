# JarvisMac

A SwiftUI chat client for the JARVIS backend, packaged as a Swift Package
(macOS 14+) rather than an `.xcodeproj` — no Xcode project file needed to
get started.

**Status**: chat UI (connection status, streaming, message list) plus a
first pass at voice — JARVIS speaks its replies (`VoiceOutput`,
`AVSpeechSynthesizer`) and can listen for "Hey Jarvis" and act on what
follows (`VoiceInputManager`, on-device `SFSpeechRecognizer`). Not
build-verified — this was written in a Linux environment with no Swift
toolchain, so treat it as reviewed-but-unbuilt until someone runs it on a
real Mac. Deeper macOS integrations (menu bar orb, Shortcuts, Keychain,
system control) are future roadmap phases, not here yet.

## Voice

Two independent toggles in the header bar:

- **Speaker icon** — JARVIS speaks each completed reply out loud via
  on-device text-to-speech. No network call, no extra API key.
- **Mic icon** — continuous on-device listening for "Hey Jarvis". Say it
  followed by your request ("Hey Jarvis, what's the news on X") and the
  words after the wake phrase are sent to the backend automatically.
  Opt-in only — JARVIS never listens unless you turn this on, and
  recognition runs on-device (`requiresOnDeviceRecognition = true`), not
  in the cloud.

Both require macOS permission prompts (microphone, speech recognition) on
first use — this app is a raw Swift Package executable rather than a full
`.app` bundle, so it embeds an `Info.plist` (with the usage-description
strings macOS requires to show those prompts) directly into the binary via
a linker flag in `Package.swift` — a standard trick for command-line Swift
tools that need TCC-gated APIs. If the permission prompt never appears or
is silently denied, that embedding is the first thing to check; granting
access manually in System Settings > Privacy & Security is the fallback.

News/current-facts questions ("what's happening with X") are answered via
Claude's server-side web search tool on the backend — see
`backend/README.md`, no extra setup needed on this side.

## Run it

On a Mac with Xcode / Xcode Command Line Tools installed:

```bash
cd apps/macos/JarvisMac
swift run
```

This builds and launches the app as a native window. Alternatively, open
the folder in Xcode (`File > Open...` on `Package.swift`) and run from
there — Xcode treats a `Package.swift` with an executable target as a
runnable app target.

Make sure the backend is running first (`../../backend`, see its README)
on `http://localhost:8000`. To point at a different backend, set
`JARVIS_BACKEND_WS_URL` in the environment (e.g. in the Xcode scheme's
"Arguments > Environment Variables", or `JARVIS_BACKEND_WS_URL=ws://... swift run`).

The backend requires a bearer token on every request (see
`backend/README.md`'s Security section) — copy the token it prints on
first run (or that you set via `JARVIS_API_TOKEN`) into this app's
`JARVIS_API_TOKEN` environment variable the same way. Without it the app
shows a connection error instead of silently failing. This is a stand-in
for real Keychain-backed storage, tracked in `../../ROADMAP.md`.

## Structure

- `Sources/JarvisMac/JarvisApp.swift` — app entry point.
- `Sources/JarvisMac/Views/` — `ContentView` (chat screen), `MessageBubble`.
- `Sources/JarvisMac/Services/JarvisClient.swift` — WebSocket client,
  implements the `/ws/chat` protocol (send `{session_id, message}`,
  receive streamed `chunk`/`done`/`error` frames).
- `Sources/JarvisMac/Services/VoiceOutput.swift` — text-to-speech for
  assistant replies (`AVSpeechSynthesizer`).
- `Sources/JarvisMac/Services/VoiceInputManager.swift` — "Hey Jarvis" wake
  word + on-device speech recognition (`SFSpeechRecognizer`).
- `Sources/JarvisMac/Models/ChatMessage.swift` — message model.
- `Sources/JarvisMac/Config/AppConfig.swift` — backend URL configuration.
- `Sources/JarvisMac/Info.plist` — embedded via a linker flag in
  `Package.swift` so mic/speech permission prompts show custom text
  without needing a full `.app` bundle.
