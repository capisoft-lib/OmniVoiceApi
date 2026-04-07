"""Split text into phrase chunks using punctuation (sentence boundaries)."""

from __future__ import annotations

import re

# Sentence-ending punctuation (Latin + common CJK), ellipsis, semicolons, blank lines.
_SPLIT_PATTERN = re.compile(
    r"(?<=[.!?…。！？])\s+|(?<=[;；])\s+|\n\s*\n+",
    re.MULTILINE,
)


def split_into_phrases(text: str) -> list[str]:
    """
    Split *text* into phrases using punctuation and paragraph breaks.

    - Splits after ``. ! ? …`` and ``。！？`` when followed by whitespace.
    - Splits on blank lines (paragraphs).
    - If nothing matches, returns the whole stripped text as a single phrase.
    """
    text = text.strip()
    if not text:
        return []
    parts = _SPLIT_PATTERN.split(text)
    phrases = [p.strip() for p in parts if p.strip()]
    if not phrases:
        return [text]
    return phrases
