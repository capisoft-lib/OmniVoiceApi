# Contributing

Thank you for your interest in improving OmniVoice and OmniVoiceApi.

## Reporting issues

- Use GitHub Issues for bugs, feature requests, and questions about the **HTTP API**, **Docker**, or **.NET client**.
- For upstream model research topics, follow the community channels listed in the main [README](README.md).

## Development setup

1. Python: create a virtual environment, install PyTorch for your platform, then `pip install -e ".[api]"` from the repo root.
2. .NET: install the [.NET 8 SDK](https://dotnet.microsoft.com/download). Build `libraries/OmniVoice.Client/OmniVoice.Client.sln`.
3. MAUI: install the .NET MAUI workload (`dotnet workload install maui`) to build the sample under `examples/maui/`.

## Pull requests

- Keep changes focused and documented in `CHANGELOG.md` when user-visible.
- Run `dotnet build` on the client solution before submitting .NET changes.
- For Python API changes, ensure `uvicorn app.main:app --app-dir apps/api` still starts after `pip install -e ".[api]"`.

## Code style

- Python: match existing formatting and typing in `omnivoice/`.
- C#: follow default .NET conventions; nullable reference types enabled.
