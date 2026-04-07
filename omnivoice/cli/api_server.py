"""Lightweight HTTP API: keeps OmniVoice loaded, POST /tts for voice cloning."""

from __future__ import annotations

import argparse
import logging
import os
import tempfile
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Annotated, Optional

import torch
import torchaudio
import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import RedirectResponse, Response
from pydantic import BaseModel, Field

from omnivoice.api.settings import default_voices_dir, resolve_api_config
from omnivoice.models.omnivoice import OmniVoice

LOG = logging.getLogger("omnivoice.api")

TAGS_METADATA = [
    {
        "name": "tts",
        "description": "Speech synthesis (model stays loaded between requests).",
    },
    {
        "name": "voices",
        "description": "Upload reference audio; stored only under the configured voices directory.",
    },
    {
        "name": "meta",
        "description": "Service status.",
    },
]

API_DESCRIPTION = """\
**OmniVoice** HTTP API: one loaded model, voice cloning via reference WAV files.

Reference voices live **only** under the configured voices directory (`--voices-dir` or `OMNIVOICE_VOICES_DIR`, default: current working directory). Use **POST /voices** to upload. **POST /tts** accepts optional `voice` (basename in that folder, e.g. `myvoice.wav`); omit it for **auto voice**.

Configuration: `OMNIVOICE_MODEL`, `OMNIVOICE_VOICES_DIR`, `OMNIVOICE_DEVICE` (see OmniVoiceApi docs).

Interactive **Swagger UI**: [`/docs`](/docs) (alias [`/swagger`](/swagger)) · **ReDoc**: [`/redoc`](/redoc) · **OpenAPI JSON**: [`/openapi.json`](/openapi.json)
"""

MAX_VOICE_UPLOAD_BYTES = 50 * 1024 * 1024


def get_best_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


class TtsRequest(BaseModel):
    model_config = {
        "json_schema_extra": {
            "examples": [
                {"text": "Bonjour.", "language": "French"},
                {
                    "text": "Bonjour.",
                    "voice": "MorganFreeman_ref.wav",
                    "language": "French",
                },
            ]
        }
    }

    text: str = Field(..., min_length=1, description="Text to synthesize")
    voice: Optional[str] = Field(
        default=None,
        description=(
            "Reference WAV basename under the voices directory (voice cloning). "
            "Omit or leave empty for **auto voice** (no reference)."
        ),
    )
    language: str = Field(default="French", description="Language name or code")
    ref_text: Optional[str] = Field(
        default=None,
        description="Optional transcript of the reference audio; if omitted, "
        "uses <voice_stem>.ref.txt next to the WAV when present, else ASR.",
    )


class VoiceUploadResponse(BaseModel):
    saved_as: str = Field(description="Filename written under the voices directory")
    voices_dir: str


def _validate_voice_save_name(name: str) -> str:
    """Return safe stem for `<stem>.wav` (no path components)."""
    raw = name.strip()
    if not raw or len(raw) > 200:
        raise HTTPException(status_code=400, detail="Invalid name (empty or too long)")
    if any(sep in raw for sep in ("/", "\\")) or ".." in raw:
        raise HTTPException(
            status_code=400,
            detail="name must be a plain basename without path separators",
        )
    base = Path(raw).name
    if base != raw:
        raise HTTPException(status_code=400, detail="name must not contain path components")
    stem = Path(raw).stem
    if not stem:
        raise HTTPException(status_code=400, detail="Invalid name")
    for c in stem:
        if c in "<>:\"|?*\x00":
            raise HTTPException(
                status_code=400,
                detail="name contains forbidden characters",
            )
    return stem


def _write_mono_wav_resampled(
    *,
    data: bytes,
    original_filename: str,
    out_path: Path,
    target_sr: int,
) -> None:
    """Decode arbitrary audio bytes, convert to mono WAV at target_sr."""
    suffix = Path(original_filename).suffix.lower() or ".wav"
    src_tmp: str | None = None
    pydub_tmp: str | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(data)
            src_tmp = tmp.name

        try:
            wav, sr = torchaudio.load(src_tmp)
        except Exception as e_torch:
            LOG.debug("torchaudio.load failed (%s), trying pydub", e_torch)
            try:
                from pydub import AudioSegment
            except ImportError as e:
                raise HTTPException(
                    status_code=500,
                    detail="Cannot decode this format (torchaudio failed and pydub is missing).",
                ) from e
            try:
                seg = AudioSegment.from_file(src_tmp)
            except Exception as e_pydub:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Could not decode audio. For formats like MP3/M4A, install "
                        "FFmpeg and ensure pydub can use it."
                    ),
                ) from e_pydub
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as pw:
                pydub_tmp = pw.name
            seg.export(pydub_tmp, format="wav")
            wav, sr = torchaudio.load(pydub_tmp)

        if wav.dim() == 1:
            wav = wav.unsqueeze(0)
        if wav.shape[0] > 1:
            wav = wav.mean(dim=0, keepdim=True)
        if sr != target_sr:
            wav = torchaudio.functional.resample(wav, sr, target_sr)
        torchaudio.save(str(out_path), wav, target_sr)
    finally:
        for p in (src_tmp, pydub_tmp):
            if p:
                try:
                    os.unlink(p)
                except OSError:
                    pass


def create_app(
    *,
    model_id: str,
    voices_dir: Path,
    device: str | None,
) -> FastAPI:
    device_resolved = device or get_best_device()
    voices_root = voices_dir.resolve()
    voices_root.mkdir(parents=True, exist_ok=True)

    model_holder: dict[str, OmniVoice | None] = {"model": None}

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        LOG.info("Loading model %s on %s ...", model_id, device_resolved)
        model_holder["model"] = OmniVoice.from_pretrained(
            model_id,
            device_map=device_resolved,
            dtype=torch.float16,
        )
        m = model_holder["model"]
        LOG.info("Model ready (sampling_rate=%s).", m.sampling_rate)
        yield

    app = FastAPI(
        title="OmniVoice TTS API",
        description=API_DESCRIPTION,
        version="0.1.0",
        lifespan=lifespan,
        openapi_tags=TAGS_METADATA,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    @app.get("/swagger", include_in_schema=False)
    def swagger_alias() -> RedirectResponse:
        """Convenience redirect; Swagger UI is served at `/docs` (FastAPI default)."""
        return RedirectResponse(url="/docs", status_code=307)

    def resolve_voice_file(voice: str) -> Path:
        # Only accept a basename to avoid path traversal
        name = Path(voice).name
        if name != voice or ".." in voice:
            raise HTTPException(status_code=400, detail="Invalid voice name")
        path = (voices_root / name).resolve()
        try:
            path.relative_to(voices_root)
        except ValueError as e:
            raise HTTPException(status_code=400, detail="Invalid voice path") from e
        if not path.is_file():
            raise HTTPException(
                status_code=404,
                detail=f"Voice file not found: {name} (voices dir: {voices_root})",
            )
        return path

    def ref_text_for_voice(wav_path: Path, override: str | None) -> str | None:
        if override is not None:
            s = override.strip()
            return s if s else None
        sidecar = wav_path.parent / f"{wav_path.stem}.ref.txt"
        if sidecar.is_file():
            return sidecar.read_text(encoding="utf-8").strip() or None
        return None

    @app.get(
        "/health",
        tags=["meta"],
        summary="Health check",
        description="Returns load status and configured voices directory.",
    )
    def health() -> dict:
        return {
            "status": "ok",
            "model_loaded": model_holder["model"] is not None,
            "voices_dir": str(voices_root),
        }

    @app.post(
        "/voices",
        tags=["voices"],
        summary="Upload a reference voice",
        description=(
            "Upload an audio file; it is converted to **mono WAV** at the model sample rate "
            "and saved as `<name>.wav` under the voices directory. "
            "Input can be WAV, MP3, M4A, etc. (formats supported by torchaudio or pydub+FFmpeg)."
        ),
        response_model=VoiceUploadResponse,
        responses={
            400: {"description": "Invalid name, decode error, or file too large"},
            503: {"description": "Model not ready"},
        },
    )
    async def upload_voice(
        name: Annotated[
            str,
            Form(
                description=(
                    "Final basename without path: the file is always saved as `<name>.wav` "
                    "(any extension in this field is stripped)."
                ),
            ),
        ],
        file: Annotated[
            UploadFile,
            File(description="Reference recording to convert and store."),
        ],
    ) -> VoiceUploadResponse:
        model = model_holder["model"]
        if model is None:
            raise HTTPException(status_code=503, detail="Model not loaded yet")
        stem = _validate_voice_save_name(name)
        out_path = (voices_root / f"{stem}.wav").resolve()
        try:
            out_path.relative_to(voices_root)
        except ValueError as e:
            raise HTTPException(status_code=400, detail="Invalid voice path") from e

        data = await file.read()
        if not data:
            raise HTTPException(status_code=400, detail="Empty file")
        if len(data) > MAX_VOICE_UPLOAD_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"File too large (max {MAX_VOICE_UPLOAD_BYTES // (1024 * 1024)} MiB)",
            )

        orig_name = file.filename or "upload.wav"
        target_sr = int(model.sampling_rate)
        try:
            _write_mono_wav_resampled(
                data=data,
                original_filename=orig_name,
                out_path=out_path,
                target_sr=target_sr,
            )
        except HTTPException:
            raise
        except Exception as e:
            LOG.exception("Voice upload failed")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save voice: {e!s}",
            ) from e

        LOG.info("Saved voice sample as %s (sr=%s)", out_path.name, target_sr)
        return VoiceUploadResponse(saved_as=out_path.name, voices_dir=str(voices_root))

    @app.get(
        "/tts",
        tags=["tts"],
        summary="TTS — how to call (no audio on GET)",
        description=(
            "Browsers issue **GET** when you open a URL; synthesis is **POST** only. "
            "This endpoint returns a short JSON hint instead of **405 Method Not Allowed**."
        ),
    )
    def tts_get_info() -> dict[str, str | dict[str, str]]:
        return {
            "message": "Use POST /tts with Content-Type: application/json; response is audio/wav.",
            "body": {
                "text": "required",
                "language": "optional (default French)",
                "voice": "optional WAV basename in voices dir; omit for auto voice",
                "ref_text": "optional (cloning only)",
            },
            "docs": "/docs",
        }

    @app.post(
        "/tts",
        tags=["tts"],
        summary="Text-to-speech",
        description=(
            "Synthesize speech as **WAV** (`audio/wav`). "
            "If `voice` is set, it must be a basename under the voices directory (cloning). "
            "If `voice` is omitted, uses **auto voice**. "
            "With cloning, optional `ref_text` or sidecar `<stem>.ref.txt` avoids ASR."
        ),
        response_class=Response,
        responses={
            200: {
                "description": "Generated mono WAV at the model sample rate (typically 24 kHz).",
                "content": {
                    "audio/wav": {"schema": {"type": "string", "format": "binary"}},
                },
            },
            400: {"description": "Invalid voice name or path"},
            404: {"description": "Voice WAV not found"},
            503: {"description": "Model not ready"},
        },
    )
    def tts(body: TtsRequest) -> Response:
        model = model_holder["model"]
        if model is None:
            raise HTTPException(status_code=503, detail="Model not loaded yet")

        voice_key = (body.voice or "").strip()
        if voice_key:
            wav_path = resolve_voice_file(voice_key)
            ref_text = ref_text_for_voice(wav_path, body.ref_text)
            ref_audio = str(wav_path)
            log_voice = wav_path.name
        else:
            ref_audio = None
            ref_text = None
            log_voice = "(auto)"

        LOG.info("TTS: voice=%s language=%s text=%s...", log_voice, body.language, body.text[:60])
        audios = model.generate(
            text=body.text,
            language=body.language,
            ref_audio=ref_audio,
            ref_text=ref_text,
        )

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            out_path = tmp.name
        try:
            torchaudio.save(out_path, audios[0], model.sampling_rate)
            data = Path(out_path).read_bytes()
        finally:
            try:
                os.unlink(out_path)
            except OSError:
                pass

        return Response(content=data, media_type="audio/wav")

    return app


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    parser = argparse.ArgumentParser(description="OmniVoice TTS HTTP API")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address")
    parser.add_argument("--port", type=int, default=8765, help="Port")
    parser.add_argument(
        "--model",
        default=None,
        help="Model id or checkpoint path (default: OMNIVOICE_MODEL or k2-fsa/OmniVoice)",
    )
    parser.add_argument(
        "--voices-dir",
        type=Path,
        default=None,
        help=(
            "Directory for voice library: uploads (POST /voices) and TTS reference lookup "
            "(default: OMNIVOICE_VOICES_DIR or current working directory; created if missing)"
        ),
    )
    parser.add_argument(
        "--device",
        default=None,
        help="cuda / mps / cpu (default: OMNIVOICE_DEVICE or auto)",
    )
    args = parser.parse_args()
    model_id, voices_dir, device = resolve_api_config(
        model_id=args.model,
        voices_dir=args.voices_dir,
        device=args.device,
    )
    app = create_app(
        model_id=model_id,
        voices_dir=voices_dir,
        device=device,
    )
    docs_host = "127.0.0.1" if args.host in ("0.0.0.0", "::") else args.host
    LOG.info(
        "Swagger UI: http://%s:%s/docs | ReDoc: http://%s:%s/redoc | OpenAPI: http://%s:%s/openapi.json",
        docs_host,
        args.port,
        docs_host,
        args.port,
        docs_host,
        args.port,
    )
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
