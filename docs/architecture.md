# Architecture overview

Text-to-speech is powered by [**OmniVoice**](https://huggingface.co/k2-fsa/OmniVoice) (zero-shot multilingual TTS).

## Components

- `apps/api`: FastAPI service exposing `/health`, `/voices`, and `/tts`.
- `examples/console-ui`: Python HTTP client (`synthesize_and_save.py`) for terminal usage.
- `examples/maui`: cross-platform .NET MAUI sample (Windows / Android; iOS / Mac Catalyst from template).
- `libraries/OmniVoice.Client`: .NET 9 client library for the same HTTP API.
- `infra/docker`: container build and Compose deployment for the API.

## Data flow

1. Client (console, MAUI, or any HTTP client) optionally uploads reference audio with `POST /voices` (stored as mono WAV under the configured voices directory).
2. Client sends JSON to `POST /tts` with `text`, optional `language`, optional `voice` basename for cloning.
3. API loads one OmniVoice model at startup; each request returns `audio/wav` bytes.
4. MAUI sample plays the WAV via Plugin.Maui.Audio after synthesis.
