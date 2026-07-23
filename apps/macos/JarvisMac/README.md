# JarvisMac

A SwiftUI chat client for the JARVIS backend, packaged as a Swift Package
(macOS 14+) rather than an `.xcodeproj` — no Xcode project file needed to
get started.

**Status**: UI skeleton only (connection status, streaming chat, message
list). Not build-verified — this was written in a Linux environment with
no Swift toolchain, so treat it as reviewed-but-unbuilt until someone runs
it on a real Mac. Deeper macOS integrations (menu bar orb, Shortcuts,
Keychain, voice, system control) are future roadmap phases, not here yet.

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

## Structure

- `Sources/JarvisMac/JarvisApp.swift` — app entry point.
- `Sources/JarvisMac/Views/` — `ContentView` (chat screen), `MessageBubble`.
- `Sources/JarvisMac/Services/JarvisClient.swift` — WebSocket client,
  implements the `/ws/chat` protocol (send `{session_id, message}`,
  receive streamed `chunk`/`done`/`error` frames).
- `Sources/JarvisMac/Models/ChatMessage.swift` — message model.
- `Sources/JarvisMac/Config/AppConfig.swift` — backend URL configuration.
