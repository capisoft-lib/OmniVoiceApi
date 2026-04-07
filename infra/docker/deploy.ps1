# Build and start OmniVoiceApi with GPU (NVIDIA Container Toolkit required).
# Run from anywhere:  pwsh -File infra/docker/deploy.ps1

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $RepoRoot

Write-Host "Building omnivoice-api:cuda12.8 from $RepoRoot ..."
docker compose -f infra/docker/docker-compose.yml build

Write-Host "Starting container (detached)..."
docker compose -f infra/docker/docker-compose.yml up -d

Write-Host ""
Write-Host "API:  http://127.0.0.1:8765/docs"
Write-Host "Logs: docker compose -f infra/docker/docker-compose.yml logs -f"
