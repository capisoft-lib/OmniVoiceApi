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

### `POST /tts/stream`

Same JSON body as **`POST /tts`** (`TtsRequest`). The server **splits `text` into phrases** using punctuation (`.`, `!`, `?`, `…`, `。`, `！`, `？`, paragraph breaks), synthesizes each phrase, and streams **one continuous utterance**: the first frame is a **mono 16-bit PCM WAV** for phrase 1; each later frame is **raw PCM s16le** (same sample rate) to append after the previous phrase’s samples. Bytes are sent after each phrase completes (pseudo-streaming).

**Response:** `200` with `Content-Type: application/octet-stream` and header:

`X-OmniVoice-Stream-Format: wav-first-pcm-tail-v1`

**Framing:** repeated blocks of:

1. **4 bytes** — unsigned big-endian length `N` of the following payload  
2. **N bytes** — first block: complete WAV; following blocks: mono PCM s16le to concatenate in time order

**Example (Python consumer — merge into one WAV):**

```python
import io
import struct
import wave

import httpx

r = httpx.post(
    "http://127.0.0.1:8765/tts/stream",
    json={"text": "Bonjour. Comment allez-vous ?", "language": "French"},
    timeout=600.0,
)
r.raise_for_status()
assert r.headers.get("X-OmniVoice-Stream-Format") == "wav-first-pcm-tail-v1"
data = r.content
i = 0
first_wav: bytes | None = None
pcm_tail = bytearray()
while i + 4 <= len(data):
    n = struct.unpack(">I", data[i : i + 4])[0]
    i += 4
    payload = data[i : i + n]
    i += n
    if first_wav is None:
        first_wav = payload
    else:
        pcm_tail.extend(payload)

assert first_wav is not None
with wave.open(io.BytesIO(first_wav), "rb") as wf_in:
    params = wf_in.getparams()
    frames = wf_in.readframes(wf_in.getnframes()) + bytes(pcm_tail)

with wave.open("out_stream_merged.wav", "wb") as wf_out:
    wf_out.setparams(params)
    wf_out.writeframes(frames)
```

For **true streaming** over the wire, use `httpx` or `requests` with `stream=True` and parse length-prefixed blocks as they arrive instead of buffering `r.content`.

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
