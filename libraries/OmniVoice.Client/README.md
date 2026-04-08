# OmniVoice.Client

.NET 9 library for calling **OmniVoiceApi** (`GET /health`, `POST /voices`, `POST /tts`).

[![NuGet](https://img.shields.io/nuget/v/OmniVoice.Client.svg)](https://www.nuget.org/packages/OmniVoice.Client)

## Install

**From NuGet.org:**

```bash
dotnet add package OmniVoice.Client
```

**Links:**

- [NuGet package](https://www.nuget.org/packages/OmniVoice.Client)

**From this repository** (development):

```bash
dotnet add reference path/to/libraries/OmniVoice.Client/src/OmniVoice.Client/OmniVoice.Client.csproj
```

## Usage

```csharp
using OmniVoice.Client;

using var client = new OmniVoiceClient(new Uri("http://127.0.0.1:8765"));
var health = await client.GetHealthAsync();
var wav = await client.SynthesizeAsync(new TtsRequest {
    Text = "Bonjour.",
    Language = "French",
});
await File.WriteAllBytesAsync("out.wav", wav);
```

## Build

```bash
dotnet build OmniVoice.Client.sln
```

## Example

```bash
dotnet run --project examples/OmniVoice.Client.Example -- http://127.0.0.1:8765
```
