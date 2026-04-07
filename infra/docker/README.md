# OmniVoiceApi — Docker

GPU-oriented image (PyTorch with CUDA 12.8 wheels). Requires [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) on the host.

## Build

From the **repository root**:

```bash
docker build -f infra/docker/Dockerfile -t omnivoice-api:latest .
```

## Run (Compose)

From `infra/docker`:

```bash
docker compose up --build
```

The API listens on **8765**. Open `http://127.0.0.1:8765/docs` for Swagger UI.

- **Hugging Face cache** is persisted in volume `hf_cache` (first run downloads the model).
- **Voices** are stored under `/data/voices` (volume `voices_data`). Use `POST /voices` or mount reference WAVs there.

## Run (Docker only)

```bash
docker run --gpus all -p 8765:8765 \
  -e OMNIVOICE_MODEL=k2-fsa/OmniVoice \
  -e OMNIVOICE_DEVICE=cuda \
  -v omnivoice_hf:/root/.cache/huggingface \
  -v omnivoice_voices:/data/voices \
  omnivoice-api:latest
```

## CPU-only hosts

The image is built with CUDA-enabled PyTorch, which can still run on CPU (`OMNIVOICE_DEVICE=cpu`), but the image is large. For a smaller CPU-only image, build a variant that installs CPU wheels from `https://download.pytorch.org/whl/cpu`.

## Publishing

Tag and push to your registry (example):

```bash
docker tag omnivoice-api:latest yourdockerhub/omnivoice-api:latest
docker push yourdockerhub/omnivoice-api:latest
```
