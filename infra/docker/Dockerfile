# OmniVoiceApi — CUDA image for GPU inference (PyTorch cu128 + NVIDIA Container Toolkit).
# Base: official NVIDIA CUDA 12.8 runtime (aligns with PyTorch cu128 wheels).
#
# Build from repository root:
#   docker build -f infra/docker/Dockerfile -t omnivoice-api:cuda12.8 .
#
# Run (requires nvidia-container-toolkit + driver on host, e.g. RTX 3090):
#   docker run --gpus all -p 8765:8765 ... omnivoice-api:cuda12.8

FROM nvidia/cuda:13.2.1-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    OMNIVOICE_VOICES_DIR=/data/voices \
    HF_HOME=/root/.cache/huggingface \
    NVIDIA_VISIBLE_DEVICES=all \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Python 3.10 (matches requires-python >=3.10)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    ffmpeg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/python3 /usr/local/bin/python \
    && ln -sf /usr/bin/pip3 /usr/local/bin/pip

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY omnivoice ./omnivoice
COPY apps ./apps

# PyTorch CUDA 12.8 wheels + OmniVoice with API extras
RUN pip install --upgrade pip setuptools wheel && \
    pip install -e ".[api]" \
        --extra-index-url https://download.pytorch.org/whl/cu128

EXPOSE 8765

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8765", "--app-dir", "apps/api"]
