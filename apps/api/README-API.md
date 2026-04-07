# OmniVoiceApi — HTTP API reference

Production-style **text-to-speech** API: one loaded [OmniVoice](https://huggingface.co/k2-fsa/OmniVoice) model, optional **voice cloning** via reference WAV files under a dedicated directory.

## Run the server

From the **repository root**, with a virtual environment and `omnivoice` installed (`pip install -e ".[api]"`):

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8765 --app-dir apps/api
```

Or use the CLI (same defaults + env resolution):

```bash
omnivoice-api --host 0.0.0.0 --port 8765
```

## Environment variables

| Variable | Description |
|----------|-------------|
| `OMNIVOICE_MODEL` | Hugging Face model id or local checkpoint path (default: `k2-fsa/OmniVoice`) |
| `OMNIVOICE_VOICES_DIR` | Directory for uploaded voices and `voice` basename lookup (default: current working directory) |
| `OMNIVOICE_DEVICE` | `cuda`, `mps`, or `cpu` (default: auto-detect) |

CLI flags `--model`, `--voices-dir`, and `--device` override these when set.

## Endpoints

### `GET /health`

JSON: `status`, `model_loaded`, `voices_dir`.

### `GET /tts`

Informational JSON only (browsers would otherwise get a 405 on POST). Use **POST /tts** for audio.

### `POST /tts`

**Request:** `Content-Type: application/json`

Body schema (`TtsRequest`):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | yes | Text to synthesize |
| `language` | string | no | Language (default: `French`) |
| `voice` | string | no | Basename of a WAV under the voices directory (cloning). Omit for **auto voice** |
| `ref_text` | string | no | Optional transcript of the reference; else `<stem>.ref.txt` sidecar if present |

**Response:** `200` with `Content-Type: audio/wav` (mono, model sample rate, typically 24 kHz).

**Example (curl):**

```bash
curl -sS -X POST "http://127.0.0.1:8765/tts" \
  -H "Content-Type: application/json" \
  -d '{"text":"Bonjour.","language":"French"}' \
  -o out.wav
```

### `POST /voices`

Multipart form:

- `name`: safe basename (saved as `<stem>.wav`)
- `file`: audio file (WAV, MP3, M4A, etc.; decoding via torchaudio / pydub+FFmpeg)

**Response:** JSON with `saved_as` and `voices_dir`.

## OpenAPI

- Swagger UI: `/docs` (alias `/swagger`)
- ReDoc: `/redoc`
- Schema: `/openapi.json`

## Error codes

| Code | Typical cause |
|------|----------------|
| 400 | Invalid voice name, decode error, empty upload |
| 404 | Referenced `voice` WAV not found |
| 503 | Model not loaded yet |
