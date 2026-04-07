# OmniVoiceApi — Docker (CUDA)

Image **GPU-first**: base [NVIDIA CUDA 12.8 runtime](https://hub.docker.com/r/nvidia/cuda) + PyTorch **cu128** wheels + OmniVoice FastAPI.

## Prerequisites (host)

1. **NVIDIA driver** compatible with CUDA 12.x (e.g. RTX 3090 — driver ≥ 525 recommended).
2. **[NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)** so `docker run --gpus all` works.

Verify:

```bash
nvidia-smi
docker run --rm --gpus all nvidia/cuda:12.8.0-base-ubuntu22.04 nvidia-smi
```

## Build

From the **repository root**:

```bash
docker build -f infra/docker/Dockerfile -t omnivoice-api:cuda12.8 .
```

## Run (Compose)

From `infra/docker`:

```bash
docker compose up --build
```

Or detached:

```bash
docker compose up --build -d
```

- API: **http://127.0.0.1:8765** — Swagger: `/docs`
- First start downloads the model into **`docker-data/huggingface/`** on the host (can take several minutes).
- Reference voices: **`docker-data/voices/`** → `/data/voices` (or `POST /voices`).

### Streaming (`POST /tts/stream`)

Chunked responses use **`X-OmniVoice-Stream-Format: wav-first-pcm-tail-v1`**: first HTTP chunk payload is a mono PCM16 WAV; later payloads are raw s16le audio to append. The image sets **`Cache-Control: no-store`** and **`X-Accel-Buffering: no`** on that route to reduce proxy buffering. If you terminate TLS or proxy in front of the container, enable streaming (e.g. nginx `proxy_buffering off` for that location). See **`apps/api/README-API.md`** for framing and a merge example.

**Persistent bind mounts** (under repository root):

| Host | Container |
|------|-----------|
| `docker-data/huggingface/` | `/root/.cache/huggingface` (HF Hub + Transformers cache) |
| `docker-data/voices/` | `/data/voices` |

Override with `OMNIVOICE_HF_BIND` / `OMNIVOICE_VOICES_BIND` in `.env` (paths relative to `infra/docker/` or absolute). See `.env.example`.

## Run (docker CLI)

From **repository root** (Linux/macOS):

```bash
mkdir -p docker-data/huggingface docker-data/voices

docker run --gpus all --shm-size=2g -p 8765:8765 \
  -e OMNIVOICE_MODEL=k2-fsa/OmniVoice \
  -e OMNIVOICE_DEVICE=cuda \
  -e HF_HOME=/root/.cache/huggingface \
  -e TRANSFORMERS_CACHE=/root/.cache/huggingface/hub \
  -v "$(pwd)/docker-data/huggingface:/root/.cache/huggingface" \
  -v "$(pwd)/docker-data/voices:/data/voices" \
  omnivoice-api:cuda12.8
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force docker-data/huggingface, docker-data/voices | Out-Null
docker run --gpus all --shm-size=2g -p 8765:8765 `
  -e OMNIVOICE_MODEL=k2-fsa/OmniVoice `
  -e OMNIVOICE_DEVICE=cuda `
  -e HF_HOME=/root/.cache/huggingface `
  -e TRANSFORMERS_CACHE=/root/.cache/huggingface/hub `
  -v "${PWD}/docker-data/huggingface:/root/.cache/huggingface" `
  -v "${PWD}/docker-data/voices:/data/voices" `
  omnivoice-api:cuda12.8
```

## Performance (reference)

On **NVIDIA RTX 3090**, a sample run reported **~3.4 s** server-side for **~28 s** of generated audio (conditions: model warm, batch size 1, exact text/settings may vary).

## Publish (registry)

Tag and push to your registry (replace `YOUR_REGISTRY`):

```bash
docker tag omnivoice-api:cuda12.8 YOUR_REGISTRY/omnivoice-api:cuda12.8
docker push YOUR_REGISTRY/omnivoice-api:cuda12.8
```

Example:

```bash
docker tag omnivoice-api:cuda12.8 ghcr.io/capisoft-lib/omnivoice-api:cuda12.8
docker push ghcr.io/capisoft-lib/omnivoice-api:cuda12.8
```

## CPU-only hosts

The image is built for **CUDA**. For CPU inference, use `OMNIVOICE_DEVICE=cpu` (slow; image remains large). A dedicated CPU image would use PyTorch CPU wheels instead.
