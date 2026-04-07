using System.Net.Http.Json;
using System.Text.Json;

namespace OmniVoice.Client;

/// <summary>HTTP client for OmniVoiceApi (TTS).</summary>
public sealed class OmniVoiceClient : IDisposable
{
    private readonly HttpClient _http;
    private readonly bool _disposeClient;
    private readonly JsonSerializerOptions _jsonRead;
    private readonly JsonSerializerOptions _jsonWrite;

    /// <summary>Creates a client with a new <see cref="HttpClient"/> pointing at <paramref name="baseAddress"/>.</summary>
    public OmniVoiceClient(Uri baseAddress)
        : this(CreateHttpClient(baseAddress), disposeClient: true)
    {
    }

    /// <summary>Uses an existing <see cref="HttpClient"/> (must have <see cref="HttpClient.BaseAddress"/> set).</summary>
    public OmniVoiceClient(HttpClient httpClient, bool disposeClient = false)
    {
        _http = httpClient ?? throw new ArgumentNullException(nameof(httpClient));
        _disposeClient = disposeClient;
        if (_http.BaseAddress is null)
            throw new ArgumentException("HttpClient.BaseAddress must be set.", nameof(httpClient));

        _jsonRead = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
            PropertyNameCaseInsensitive = true,
        };
        _jsonWrite = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
            DefaultIgnoreCondition = System.Text.Json.Serialization.JsonIgnoreCondition.WhenWritingNull,
        };
    }

    private static HttpClient CreateHttpClient(Uri baseAddress)
    {
        return new HttpClient { BaseAddress = NormalizeBase(baseAddress) };
    }

    private static Uri NormalizeBase(Uri u)
    {
        var s = u.ToString();
        return s.EndsWith('/') ? u : new Uri(s + "/");
    }

    /// <summary>GET /health</summary>
    public async Task<HealthResponse> GetHealthAsync(CancellationToken cancellationToken = default)
    {
        using var resp = await _http.GetAsync("health", cancellationToken).ConfigureAwait(false);
        await EnsureSuccessAsync(resp, cancellationToken).ConfigureAwait(false);
        var result = await resp.Content.ReadFromJsonAsync<HealthResponse>(_jsonRead, cancellationToken)
            .ConfigureAwait(false);
        return result ?? throw new InvalidOperationException("Empty health response.");
    }

    /// <summary>POST /voices (multipart)</summary>
    public async Task<VoiceUploadResponse> UploadVoiceAsync(
        string name,
        Stream fileStream,
        string fileName,
        CancellationToken cancellationToken = default)
    {
        using var content = new MultipartFormDataContent();
        content.Add(new StringContent(name), "name");
        content.Add(new StreamContent(fileStream), "file", fileName);
        using var resp = await _http.PostAsync("voices", content, cancellationToken).ConfigureAwait(false);
        await EnsureSuccessAsync(resp, cancellationToken).ConfigureAwait(false);
        var result = await resp.Content.ReadFromJsonAsync<VoiceUploadResponse>(_jsonRead, cancellationToken)
            .ConfigureAwait(false);
        return result ?? throw new InvalidOperationException("Empty upload response.");
    }

    /// <summary>POST /tts — returns WAV bytes.</summary>
    public async Task<byte[]> SynthesizeAsync(TtsRequest request, CancellationToken cancellationToken = default)
    {
        using var req = new HttpRequestMessage(HttpMethod.Post, "tts");
        req.Content = JsonContent.Create(request, options: _jsonWrite);
        using var resp = await _http.SendAsync(req, cancellationToken).ConfigureAwait(false);
        await EnsureSuccessAsync(resp, cancellationToken).ConfigureAwait(false);
        return await resp.Content.ReadAsByteArrayAsync(cancellationToken).ConfigureAwait(false);
    }

    private static async Task EnsureSuccessAsync(HttpResponseMessage resp, CancellationToken ct)
    {
        if (resp.IsSuccessStatusCode)
            return;
        var body = await resp.Content.ReadAsStringAsync(ct).ConfigureAwait(false);
        throw new OmniVoiceApiException((int)resp.StatusCode, body);
    }

    public void Dispose()
    {
        if (_disposeClient)
            _http.Dispose();
    }
}
