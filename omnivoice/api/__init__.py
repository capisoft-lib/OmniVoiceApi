"""HTTP API configuration helpers for OmniVoiceApi."""

from omnivoice.api.phrases import split_into_phrases
from omnivoice.api.settings import resolve_api_config

__all__ = ["resolve_api_config", "split_into_phrases"]
