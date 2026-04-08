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

## Deploy on a remote host (SSH)

From your workstation (with SSH access to the server), using the **pre-built Hub image**:

```powershell
# Windows — replace user@10.1.200.10 with your SSH login
pwsh -File infra/docker/deploy-remote.ps1 -SshTarget 'user@10.1.200.10'
```

This copies [remote-docker-run.sh](remote-docker-run.sh) to `/tmp/` and runs it with `sudo`. The script pulls **`capitaine/omnivoice-api:cuda12.8`**, recreates container **`omnivoice-api`**, maps port **8765**, and uses Docker volumes **`omnivoice_hf`** / **`omnivoice_voices`** for cache and voices. Override defaults by editing the script or setting env vars on the server before running (see `OMNIVOICE_*` at the top of `remote-docker-run.sh`).

Manual equivalent on the server:

```bash
docker pull capitaine/omnivoice-api:cuda12.8
sudo bash /path/to/infra/docker/remote-docker-run.sh
```

API URL after deploy: **`http://<server-ip>:8765/docs`** (e.g. `http://10.1.200.10:8765/docs`).

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

Sample **`POST /tts`** (model warm, batch size 1; wall-clock synthesis time — conditions may vary):

| GPU | Synthesis time | Generated audio |
|-----|----------------|-----------------|
| **RTX 3090** | **3.4 s** | **22 s** |
| **RTX 3060 Ti** | **5.4 s** | **22 s** |

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
