# OmniVoiceApi — MAUI sample

Cross-platform sample that calls **OmniVoice.Client** to synthesize speech and plays the returned WAV with [Plugin.Maui.Audio](https://github.com/jfversluis/Plugin.Maui.Audio).

## Prerequisites

- .NET 9 SDK with MAUI workload: `dotnet workload install maui`
- A running OmniVoiceApi instance (see root [README](../../README.md))

## URLs

| Environment | Base URL |
|-------------|----------|
| Windows / desktop loopback | `http://127.0.0.1:8765` |
| Android emulator → host | `http://10.0.2.2:8765` |

Cleartext HTTP is enabled on Android for development only (`AndroidManifest.xml`).

## Build

```bash
dotnet build OmniVoiceApi.Maui.csproj -f net9.0-windows10.0.19041.0
dotnet build OmniVoiceApi.Maui.csproj -f net9.0-android
```

## Run

Open `OmniVoiceApi.Maui.csproj` in Visual Studio 2022 and set the target (Windows or Android).
