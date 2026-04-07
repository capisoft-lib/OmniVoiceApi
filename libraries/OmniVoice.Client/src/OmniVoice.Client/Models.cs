namespace OmniVoice.Client;

/// <summary>Response from GET /health.</summary>
public sealed class HealthResponse
{
    public string Status { get; set; } = "";
    public bool ModelLoaded { get; set; }
    public string VoicesDir { get; set; } = "";
}

/// <summary>Response from POST /voices.</summary>
public sealed class VoiceUploadResponse
{
    public string SavedAs { get; set; } = "";
    public string VoicesDir { get; set; } = "";
}

/// <summary>JSON body for POST /tts.</summary>
public sealed class TtsRequest
{
    public string Text { get; set; } = "";
    public string? Voice { get; set; }
    public string Language { get; set; } = "French";
    public string? RefText { get; set; }
}
