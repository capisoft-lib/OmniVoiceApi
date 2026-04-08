# OmniVoiceApi — TTS HTTP API & clients

<p align="center">
  <img width="200" height="200" alt="OmniVoice" src="https://zhu-han.github.io/omnivoice/pics/omnivoice.jpg" />
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License"></a>
</p>

**OmniVoiceApi** is a production-style monorepo: **FastAPI** text-to-speech (voice cloning, streaming), **Docker** (CUDA), Python and **.NET** clients, and a sample **MAUI** app. Inference uses the open **OmniVoice** weights ([Hugging Face `k2-fsa/OmniVoice`](https://huggingface.co/k2-fsa/OmniVoice)); research, training, and the core Python package live in the **[upstream GitHub repo](https://github.com/k2-fsa/OmniVoice)** — this README focuses on **this** API layout only.

> **Speech-to-text (sibling stack):** **[FastWhisperApi](https://github.com/capisoft-lib/FastWhisperApi)** — same idea (HTTP API, Docker, clients), for transcription/translation.

**Jump to:** [Layout](#repository-layout) · [Quick start](#quick-start) · [HTTP API](#http-api) · [Performance](#performance) · [Docker Hub](#5-docker-api-cuda)

---

## Repository layout

```
apps/
  api/                      # uvicorn entry, OpenAPI (see README-API.md)
examples/
  console-ui/               # Python: call POST /tts
  maui/                     # .NET MAUI sample
infra/
  docker/                   # image, compose, remote deploy
libraries/
  OmniVoice.Client/         # .NET client (NuGet: OmniVoice.Client)
omnivoice/                  # vendored package + CLIs when installed from this tree
docs/                       # architecture, API-related notes
```

More detail: [docs/architecture.md](docs/architecture.md).

---

## Quick start

### 1) API (local Python)

```bash
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate

pip install torch==2.8.0 torchaudio==2.8.0 --extra-index-url https://download.pytorch.org/whl/cu128
pip install -e ".[api]"

uvicorn app.main:app --host 0.0.0.0 --port 8765 --app-dir apps/api
```

Or: `omnivoice-api --host 0.0.0.0 --port 8765`. HTTP reference: [apps/api/README-API.md](apps/api/README-API.md).

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

[libraries/OmniVoice.Client/README.md](libraries/OmniVoice.Client/README.md)

### 4) MAUI sample

`examples/maui/OmniVoiceApi.Maui/` — Windows build tested; Android dev-friendly (cleartext HTTP).

### 5) Docker API (CUDA)

```bash
docker pull capitaine/omnivoice-api:cuda12.8
docker compose -f infra/docker/docker-compose.yml up --build
```

Or: `pwsh -File infra/docker/deploy.ps1` / `bash infra/docker/deploy.sh`. Details: [infra/docker/README.md](infra/docker/README.md).

**Docker Hub:** [capitaine/omnivoice-api](https://hub.docker.com/r/capitaine/omnivoice-api)

---

## HTTP API

| Endpoint | Role |
|----------|------|
| `POST /tts` | JSON → mono WAV |
| `POST /tts/stream` | Phrase streaming (`wav-first-pcm-tail-v1`) |
| `POST /voices` | Upload reference voice |
| `GET /health` | Status |

Swagger: **`/docs`**. Streaming: [apps/api/README-API.md](apps/api/README-API.md).

---

## Performance

Sample **`POST /tts`** runs (model warm, batch size 1, same text/settings; wall-clock server time for synthesis — your conditions may differ):

| GPU | Approx. synthesis time | Generated audio length |
|-----|------------------------|-------------------------|
| NVIDIA GeForce **RTX 3090** | **3.4 s** | **22 s** |
| NVIDIA GeForce **RTX 3060 Ti** | **5.4 s** | **22 s** |

---

## Upstream model & library

Training, paper, Gradio demo, `pip install omnivoice`, `omnivoice-infer`, and the full feature set are maintained by the **K2-FSA / OmniVoice** project:

**https://github.com/k2-fsa/OmniVoice**

---

## Environment

Copy [.env.example](.env.example) to `.env` and set `OMNIVOICE_*` for local runs.

---

## Security & contributing

- [SECURITY.md](SECURITY.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CHANGELOG.md](CHANGELOG.md)

---

## Citation (model)

If you use the OmniVoice model academically, cite the paper linked from the [upstream repository](https://github.com/k2-fsa/OmniVoice).

```bibtex
@article{zhu2026omnivoice,
      title={OmniVoice: Towards Omnilingual Zero-Shot Text-to-Speech with Diffusion Language Models},
      author={Zhu, Han and Ye, Lingxuan and Kang, Wei and Yao, Zengwei and Guo, Liyong and Kuang, Fangjun and Han, Zhifeng and Zhuang, Weiji and Lin, Long and Povey, Daniel},
      journal={arXiv preprint arXiv:2604.00688},
      year={2026}
}
```
