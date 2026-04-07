using OmniVoice.Client;
using Plugin.Maui.Audio;

namespace OmniVoiceApi.Maui;

public partial class MainPage : ContentPage
{
    private readonly IAudioManager _audioManager;
    private byte[]? _lastWav;
    private IAudioPlayer? _player;

    public MainPage()
    {
        InitializeComponent();
        _audioManager = AudioManager.Current;
    }

    private async void OnSynthesizeClicked(object? sender, EventArgs e)
    {
        SynthesizeBtn.IsEnabled = false;
        StatusLabel.Text = "Synthesis…";
        try
        {
            var baseUri = new Uri(BaseUrlEntry.Text.Trim());
            using var client = new OmniVoiceClient(baseUri);
            var health = await client.GetHealthAsync().ConfigureAwait(true);
            if (!health.ModelLoaded)
                StatusLabel.Text = "Warning: model not loaded yet.";

            var wav = await client.SynthesizeAsync(
                new TtsRequest
                {
                    Text = TextEditor.Text ?? "",
                    Language = string.IsNullOrWhiteSpace(LanguageEntry.Text)
                        ? "French"
                        : LanguageEntry.Text.Trim(),
                }).ConfigureAwait(true);

            _lastWav = wav;
            PlayBtn.IsEnabled = true;
            StatusLabel.Text = $"OK — {wav.Length} bytes (ready to play)";

            await PlayLastAsync().ConfigureAwait(true);
        }
        catch (Exception ex)
        {
            StatusLabel.Text = ex.Message;
            await DisplayAlert("Error", ex.ToString(), "OK");
        }
        finally
        {
            SynthesizeBtn.IsEnabled = true;
        }
    }

    private async void OnPlayClicked(object? sender, EventArgs e)
    {
        await PlayLastAsync().ConfigureAwait(true);
    }

    private Task PlayLastAsync()
    {
        if (_lastWav is null || _lastWav.Length == 0)
            return Task.CompletedTask;

        _player?.Stop();
        _player?.Dispose();
        _player = null;

        var stream = new MemoryStream(_lastWav);
        _player = _audioManager.CreatePlayer(stream);
        _player.Play();
        return Task.CompletedTask;
    }

    protected override void OnDisappearing()
    {
        _player?.Stop();
        _player?.Dispose();
        base.OnDisappearing();
    }
}
