#!/usr/bin/env bash
# Run on the Linux host (with Docker + NVIDIA Container Toolkit). Pulls and starts OmniVoiceApi.
set -euo pipefail

IMAGE="${OMNIVOICE_IMAGE:-capitaine/omnivoice-api:cuda12.8}"
NAME="${OMNIVOICE_CONTAINER_NAME:-omnivoice-api}"
PORT="${OMNIVOICE_PORT:-8765}"

echo "Pulling ${IMAGE} ..."
docker pull "${IMAGE}"

echo "Replacing container ${NAME} if it exists ..."
docker stop "${NAME}" 2>/dev/null || true
docker rm "${NAME}" 2>/dev/null || true

echo "Starting ${NAME} on port ${PORT} ..."
docker run -d \
  --restart unless-stopped \
  --name "${NAME}" \
  --gpus all \
  --shm-size=2g \
  -p "${PORT}:8765" \
  -e OMNIVOICE_MODEL="${OMNIVOICE_MODEL:-k2-fsa/OmniVoice}" \
  -e OMNIVOICE_DEVICE="${OMNIVOICE_DEVICE:-cuda}" \
  -e OMNIVOICE_VOICES_DIR=/data/voices \
  -e HF_HOME=/root/.cache/huggingface \
  -e TRANSFORMERS_CACHE=/root/.cache/huggingface/hub \
  -v omnivoice_hf:/root/.cache/huggingface \
  -v omnivoice_voices:/data/voices \
  "${IMAGE}"

echo "Done. API: http://$(hostname -I | awk '{print $1}'):${PORT}/docs"
docker ps --filter "name=${NAME}"
