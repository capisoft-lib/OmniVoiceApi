# OmniVoice — text-to-speech API & clients

<p align="center">
  <img width="200" height="200" alt="OmniVoice" src="https://zhu-han.github.io/omnivoice/pics/omnivoice.jpg" />
</p>

<p align="center">
  <a href="https://huggingface.co/k2-fsa/OmniVoice"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Model-FFD21E" alt="Hugging Face Model"></a>
  &nbsp;
  <a href="https://huggingface.co/spaces/k2-fsa/OmniVoice"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Space-blue" alt="Hugging Face Space"></a>
  &nbsp;
  <a href="https://arxiv.org/abs/2604.00688"><img src="https://img.shields.io/badge/arXiv-Paper-B31B1B.svg" alt="arXiv"></a>
  &nbsp;
  <a href="https://zhu-han.github.io/omnivoice"><img src="https://img.shields.io/badge/GitHub.io-Demo_Page-blue?logo=GitHub&style=flat-square" alt="Demo"></a>
  &nbsp;
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License"></a>
</p>

**OmniVoice** is a multilingual zero-shot text-to-speech model (voice cloning, voice design, 600+ languages). **This repository** packages it as **OmniVoiceApi**: a production-style monorepo with a **FastAPI** server, **Docker** (CUDA), Python and **.NET** clients, and a sample **MAUI** app — similar in spirit to our speech-to-text stack, but focused entirely on **TTS**.

> **Speech-to-text in the same family:** for transcription and translation over HTTP, see **[FastWhisperApi](https://github.com/capisoft-lib/FastWhisperApi)** (faster-whisper). OmniVoice here is **speech synthesis**, not Whisper.

**Jump to:** [Repository layout](#repository-layout) · [Quick start](#quick-start) · [HTTP API](#http-api) · [Docker Hub](#5-docker-api-cuda) · [Model features](#model-features) · [Python library & CLI](#python-package-installation) · [Citation](#citation)

---

## Repository layout

```
apps/
  api/                      # uvicorn entry, OpenAPI (see README-API.md)
examples/
  console-ui/               # Python client: synthesize via HTTP
  maui/                     # .NET MAUI sample (OmniVoiceApi.Maui)
infra/
  docker/                   # Dockerfile, compose, deploy scripts
libraries/
  OmniVoice.Client/         # .NET client (NuGet: OmniVoice.Client)
omnivoice/                  # Core model package + CLIs (omnivoice-api, omnivoice-demo, …)
docs/                       # Voice design, generation params, languages, …
```

Architecture notes: [docs/architecture.md](docs/architecture.md).

---

## Quick start

### 1) API (local Python)

```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Linux / macOS:
# source .venv/bin/activate

pip install torch==2.8.0 torchaudio==2.8.0 --extra-index-url https://download.pytorch.org/whl/cu128
pip install -e ".[api]"

uvicorn app.main:app --host 0.0.0.0 --port 8765 --app-dir apps/api
```

Or run the same app via: `omnivoice-api --host 0.0.0.0 --port 8765` (optional: `--voices-dir`, `--device cuda|cpu|mps`).

Copy [.env.example](.env.example) to `.env` and set `OMNIVOICE_*` if needed. Full HTTP reference: [apps/api/README-API.md](apps/api/README-API.md).

### 2) Console example (Python)

```bash
pip install -r examples/console-ui/requirements-recorder.txt
python examples/console-ui/synthesize_and_save.py --url http://127.0.0.1:8765 --text "Bonjour."
```

### 3) C# client

```bash
dotnet build libraries/OmniVoice.Client/OmniVoice.Client.sln
dotnet run --project libraries/OmniVoice.Client/examples/OmniVoice.Client.Example -- http://127.0.0.1:8765
```

Package: `dotnet add package OmniVoice.Client` — details: [libraries/OmniVoice.Client/README.md](libraries/OmniVoice.Client/README.md).

### 4) MAUI sample

Open `examples/maui/OmniVoiceApi.Maui/OmniVoiceApi.Maui.csproj` in Visual Studio, or:

```bash
dotnet build examples/maui/OmniVoiceApi.Maui/OmniVoiceApi.Maui.csproj -f net9.0-windows10.0.19041.0
```

**Windows** build is tested; **Android** is set up for dev (cleartext HTTP; emulator often uses `http://10.0.2.2:8765`). iOS / Mac Catalyst targets exist but are not validated in this repo.

### 5) Docker API (CUDA)

Pre-built image (GPU, NVIDIA Container Toolkit required on the host):

```bash
docker pull capitaine/omnivoice-api:cuda12.8
# or: capitaine/omnivoice-api:latest
```

From source:

```bash
docker compose -f infra/docker/docker-compose.yml up --build
```

Or: `pwsh -File infra/docker/deploy.ps1` / `bash infra/docker/deploy.sh`.

**Docker Hub:** [capitaine/omnivoice-api](https://hub.docker.com/r/capitaine/omnivoice-api). Persistent caches and voices: see [infra/docker/README.md](infra/docker/README.md).

---

## HTTP API

The server keeps **one loaded model** and exposes:

| Endpoint | Role |
|----------|------|
| `POST /tts` | JSON in → mono **WAV** out |
| `POST /tts/stream` | Phrase-split synthesis; streamed **wav-first-pcm-tail-v1** (first frame full PCM16 WAV, then raw s16le tails to concatenate) |
| `POST /voices` | Upload reference audio for cloning |
| `GET /health` | Status |

Interactive docs: **`/docs`** (Swagger). Streaming format and client merge example: [apps/api/README-API.md](apps/api/README-API.md).

---

## Model features

- **600+ languages** — see [docs/languages.md](docs/languages.md).
- **Voice cloning** from short reference audio.
- **Voice design** via natural-language instructions (no reference) — [docs/voice-design.md](docs/voice-design.md).
- **Auto voice** when no reference or instruction is given.
- **Control**: non-verbal tags (e.g. `[laughter]`), pronunciation hints; tunable steps, speed, duration — [docs/generation-parameters.md](docs/generation-parameters.md).
- **Fast inference** — diffusion LM–style architecture; see the [paper](https://arxiv.org/abs/2604.00688).

---

## Python package installation

Use a fresh virtual environment. Install **PyTorch** for your platform ([pytorch.org](https://pytorch.org/get-started/locally/)), then OmniVoice:

```bash
# PyPI
pip install omnivoice

# Latest upstream source (no clone)
pip install git+https://github.com/k2-fsa/OmniVoice.git

# Editable from a clone
git clone https://github.com/k2-fsa/OmniVoice.git
cd OmniVoice
pip install -e .
```

**uv:** `git clone` … `cd OmniVoice` → `uv sync` (optional mirror: `uv sync --default-index "https://mirrors.aliyun.com/pypi/simple"`).

---

## Try the model (Gradio / Hugging Face)

- Local UI: `omnivoice-demo --ip 0.0.0.0 --port 8001`
- Hosted: [Hugging Face Space — k2-fsa/OmniVoice](https://huggingface.co/spaces/k2-fsa/OmniVoice)

If Hub downloads fail, try `export HF_ENDPOINT="https://hf-mirror.com"` (or your preferred mirror).

---

## Python API (library)

Voice cloning (with optional `ref_text`; omit to use ASR / sidecar):

```python
from omnivoice import OmniVoice
import torch
import torchaudio

model = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cuda:0", dtype=torch.float16)
# Apple Silicon: device_map="mps"

audio = model.generate(
    text="Hello, this is a test of zero-shot voice cloning.",
    ref_audio="ref.wav",
    ref_text="Transcription of the reference audio.",
)
torchaudio.save("out.wav", audio[0], model.sampling_rate)
```

Voice design and auto voice use the same `generate()` API; see [docs/voice-design.md](docs/voice-design.md) and [docs/generation-parameters.md](docs/generation-parameters.md).

---

## Command-line tools

| Command | Description |
|---------|-------------|
| `omnivoice-demo` | Gradio web UI — [omnivoice/cli/demo.py](omnivoice/cli/demo.py) |
| `omnivoice-api` | OmniVoiceApi HTTP server — [omnivoice/cli/api_server.py](omnivoice/cli/api_server.py) |
| `omnivoice-infer` | Single utterance to WAV — [omnivoice/cli/infer.py](omnivoice/cli/infer.py) |
| `omnivoice-infer-batch` | Multi-GPU batch (JSONL) — [omnivoice/cli/infer_batch.py](omnivoice/cli/infer_batch.py) |

Run `--help` on any command. For batch JSONL fields, see `infer_batch.py` or the [upstream OmniVoice repo](https://github.com/k2-fsa/OmniVoice).

---

## Training & evaluation

Pipelines and configs live under [examples/](examples/). Upstream discussions: [k2-fsa/OmniVoice issues](https://github.com/k2-fsa/OmniVoice/issues).

---

## Security & contributing

- [SECURITY.md](SECURITY.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CHANGELOG.md](CHANGELOG.md)

---

## Discussion (upstream model)

[GitHub Issues — k2-fsa/OmniVoice](https://github.com/k2-fsa/OmniVoice/issues)

WeChat group / official account (K2-FSA):

| Wechat Group | Wechat Official Account |
| ------------ | ----------------------- |
| ![wechat](https://k2-fsa.org/zh-CN/assets/pic/wechat_group.jpg) | ![wechat](https://k2-fsa.org/zh-CN/assets/pic/wechat_account.jpg) |

---

## Citation

```bibtex
@article{zhu2026omnivoice,
      title={OmniVoice: Towards Omnilingual Zero-Shot Text-to-Speech with Diffusion Language Models},
      author={Zhu, Han and Ye, Lingxuan and Kang, Wei and Yao, Zengwei and Guo, Liyong and Kuang, Fangjun and Han, Zhifeng and Zhuang, Weiji and Lin, Long and Povey, Daniel},
      journal={arXiv preprint arXiv:2604.00688},
      year={2026}
}
```
