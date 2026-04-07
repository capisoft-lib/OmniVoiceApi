# OmniVoiceApi — GPU-ready image (PyTorch CUDA 12.8 wheels on Linux).
# Build from repository root:
#   docker build -f infra/docker/Dockerfile -t omnivoice-api:latest .

FROM python:3.14-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    OMNIVOICE_VOICES_DIR=/data/voices \
    HF_HOME=/root/.cache/huggingface

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Package source + ASGI app tree
COPY pyproject.toml README.md LICENSE ./
COPY omnivoice ./omnivoice
COPY apps ./apps

# CUDA 12.8 PyTorch wheels (via extra index) + OmniVoice with API extras
RUN pip install --upgrade pip setuptools wheel && \
    pip install -e ".[api]" \
        --extra-index-url https://download.pytorch.org/whl/cu128

EXPOSE 8765

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8765", "--app-dir", "apps/api"]
