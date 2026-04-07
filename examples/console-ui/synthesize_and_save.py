#!/usr/bin/env python3
"""Minimal OmniVoiceApi client: health check, optional voice upload, POST /tts, save WAV."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import httpx


def main() -> int:
    parser = argparse.ArgumentParser(description="Call OmniVoiceApi POST /tts and save WAV output")
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:8765",
        help="API base URL (no trailing slash)",
    )
    parser.add_argument("--text", required=True, help="Text to synthesize")
    parser.add_argument("--language", default="French", help="Language (default: French)")
    parser.add_argument(
        "--voice",
        default=None,
        help="Basename of a WAV already on the server (cloning); omit for auto voice",
    )
    parser.add_argument(
        "--upload",
        type=Path,
        default=None,
        help="Local audio file to upload via POST /voices before TTS (saved as --upload-name)",
    )
    parser.add_argument(
        "--upload-name",
        default="demo",
        help="Stem for POST /voices `name` field (saved as <stem>.wav on server)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("omnivoice_api_out.wav"),
        help="Output WAV path",
    )
    args = parser.parse_args()
    base = args.url.rstrip("/")

    with httpx.Client(timeout=600.0) as client:
        r = client.get(f"{base}/health")
        r.raise_for_status()
        health = r.json()
        print("health:", health)

        if args.upload is not None:
            if not args.upload.is_file():
                print(f"Upload file not found: {args.upload}", file=sys.stderr)
                return 1
            files = {"file": (args.upload.name, args.upload.read_bytes())}
            data = {"name": args.upload_name}
            ur = client.post(f"{base}/voices", data=data, files=files)
            if ur.status_code >= 400:
                print(ur.text, file=sys.stderr)
            ur.raise_for_status()
            print("upload:", ur.json())
            voice_for_tts = f"{Path(args.upload_name).stem}.wav"
        else:
            voice_for_tts = args.voice

        body = {
            "text": args.text,
            "language": args.language,
        }
        if voice_for_tts:
            body["voice"] = voice_for_tts

        tr = client.post(f"{base}/tts", json=body)
        if tr.status_code >= 400:
            print(tr.text, file=sys.stderr)
        tr.raise_for_status()
        args.output.write_bytes(tr.content)
        print(f"Wrote {args.output} ({len(tr.content)} bytes)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
