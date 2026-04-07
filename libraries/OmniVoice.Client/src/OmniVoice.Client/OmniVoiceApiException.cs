namespace OmniVoice.Client;

/// <summary>Thrown when the OmniVoiceApi returns a non-success HTTP status.</summary>
public sealed class OmniVoiceApiException : Exception
{
    public OmniVoiceApiException(int statusCode, string? responseBody, Exception? inner = null)
        : base($"OmniVoiceApi returned {(System.Net.HttpStatusCode)statusCode}: {responseBody}", inner)
    {
        StatusCode = statusCode;
        ResponseBody = responseBody;
    }

    public int StatusCode { get; }
    public string? ResponseBody { get; }
}
