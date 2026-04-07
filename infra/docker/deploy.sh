#!/usr/bin/env bash
# Build and start OmniVoiceApi with GPU (NVIDIA Container Toolkit required).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
echo "Building omnivoice-api:cuda12.8 from $ROOT ..."
docker compose -f infra/docker/docker-compose.yml build
echo "Starting container (detached)..."
docker compose -f infra/docker/docker-compose.yml up -d
echo ""
echo "API:  http://127.0.0.1:8765/docs"
echo "Logs: docker compose -f infra/docker/docker-compose.yml logs -f"
