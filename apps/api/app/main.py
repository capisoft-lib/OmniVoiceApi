"""
OmniVoiceApi ASGI application for uvicorn.

Run from repository root (with `omnivoice` installed, e.g. ``pip install -e ".[api]"``)::

    uvicorn app.main:app --host 0.0.0.0 --port 8765 --app-dir apps/api

Environment variables (optional): ``OMNIVOICE_MODEL``, ``OMNIVOICE_VOICES_DIR``, ``OMNIVOICE_DEVICE``.
"""

from __future__ import annotations

import logging

from omnivoice.api.settings import resolve_api_config
from omnivoice.cli.api_server import create_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

_model_id, _voices_dir, _device = resolve_api_config()
app = create_app(model_id=_model_id, voices_dir=_voices_dir, device=_device)
