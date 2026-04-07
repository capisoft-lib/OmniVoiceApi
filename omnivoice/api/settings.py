"""Environment and default resolution for the OmniVoice TTS HTTP API."""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_MODEL_ID = "k2-fsa/OmniVoice"


def default_voices_dir() -> Path:
    return Path.cwd()


def resolve_api_config(
    *,
    model_id: str | None = None,
    voices_dir: Path | None = None,
    device: str | None = None,
) -> tuple[str, Path, str | None]:
    """
    Resolve model path, voices directory, and device.

    Explicit arguments override environment variables:
    ``OMNIVOICE_MODEL``, ``OMNIVOICE_VOICES_DIR``, ``OMNIVOICE_DEVICE``.
    """
    m = (model_id or os.environ.get("OMNIVOICE_MODEL", DEFAULT_MODEL_ID)).strip()
    if not m:
        m = DEFAULT_MODEL_ID

    if voices_dir is not None:
        vd = voices_dir
    else:
        env_voices = os.environ.get("OMNIVOICE_VOICES_DIR")
        vd = Path(env_voices) if env_voices else default_voices_dir()

    if device is not None:
        d: str | None = device.strip() if device.strip() else None
    else:
        env_d = os.environ.get("OMNIVOICE_DEVICE")
        d = env_d.strip() if env_d and env_d.strip() else None

    return m, vd, d
