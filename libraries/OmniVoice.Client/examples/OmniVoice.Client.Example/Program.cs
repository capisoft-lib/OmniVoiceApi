using OmniVoice.Client;

var url = args.Length > 0 ? args[0] : "http://127.0.0.1:8765";
using var client = new OmniVoiceClient(new Uri(url));

var health = await client.GetHealthAsync().ConfigureAwait(false);
Console.WriteLine($"health: status={health.Status} model_loaded={health.ModelLoaded} voices_dir={health.VoicesDir}");

var wav = await client.SynthesizeAsync(
    new TtsRequest { Text = "Bonjour.", Language = "French" }).ConfigureAwait(false);

var outPath = Path.Combine(AppContext.BaseDirectory, "omnivoice_client_out.wav");
await File.WriteAllBytesAsync(outPath, wav).ConfigureAwait(false);
Console.WriteLine($"Wrote {outPath} ({wav.Length} bytes)");
