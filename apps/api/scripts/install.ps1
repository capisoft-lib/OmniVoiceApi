# Install OmniVoice + API extras for local development (Windows).
# Run from repository root after creating a venv.

$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path (Join-Path $PSScriptRoot "..\..\.."))

python -m pip install --upgrade pip
pip install torch==2.8.0 torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/cu128
pip install -e ".[api]"

Write-Host "Done. Activate your venv, then:"
Write-Host "  uvicorn app.main:app --host 0.0.0.0 --port 8765 --app-dir apps/api"
