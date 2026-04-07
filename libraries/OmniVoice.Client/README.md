# OmniVoice.Client

.NET 8 library for calling **OmniVoiceApi** (`GET /health`, `POST /voices`, `POST /tts`).

## Install (local project reference)

```bash
dotnet add package OmniVoice.Client
# or: ProjectReference to src/OmniVoice.Client/OmniVoice.Client.csproj
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
