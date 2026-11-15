---
title: Cody — Grounded Voice Intelligence
emoji: 🪷
colorFrom: yellow
colorTo: red
sdk: gradio
sdk_version: 6.25.0
app_file: app.py
short_description: Multilingual grounded voice and text assistant
python_version: "3.12"
startup_duration_timeout: 1h
---

# Cody

Cody is a multilingual voice and text assistant. It transcribes speech, retrieves passages
from its knowledge base, and returns a grounded answer with citations. When the available
evidence is insufficient, Cody says so rather than inventing an answer.

The browser interface is served by a Gradio Space wrapper (`app.py`) or the FastAPI app
(`cody_voice.web`). Both use the same retrieval and answer pipeline. The serving configuration
uses BGE-M3 embeddings and a language-partitioned FAISS HNSW index. The index and chunk mapping
are stored under `space_artifacts/`; model weights are downloaded on first startup.

## Run locally

Use Python 3.12 and install the dependencies:

```bash
python -m pip install -r requirements.txt
```

Set provider keys in your shell or add them to a local `.env` file. Start the FastAPI app with:

```bash
python -m uvicorn cody_voice.web:app --host 127.0.0.1 --port 8000
```

Open <http://127.0.0.1:8000>. The service reads `results/final_retriever_config.json` by
default. Set `HH_RAG_RETRIEVER_CONFIG` to use another config file. The model cache path in
that config must exist locally or be downloaded before the app can become ready.

## Speech providers

Gnani provides Prisma speech-to-text and Timbre text-to-speech through the
[`gnani-vachana`](https://pypi.org/project/gnani-vachana/) SDK. Add `GNANI_API_KEY` to enable
these services. Sarvam Saaras can provide speech-to-text with `SARVAM_API_KEY`; it is also
used as a transcription fallback when Gnani is selected and available.

`HH_RAG_STT_PROVIDER` selects `gnani` or `sarvam` (default: `gnani`).
`HH_RAG_TTS_PROVIDER` selects `gnani` or `off` (default: `gnani`). Text-to-speech is available
only when a Gnani key is configured. A provider smoke check is available at
`scripts/gnani_smoke.py`:

```bash
python scripts/gnani_smoke.py --language en-IN
```

## Hugging Face Spaces

This repository is configured as a Gradio Space with `app.py` as its entry point. To publish
it, create or select a Space owned by your Hugging Face account and push this repository to
that Space. Add `GNANI_API_KEY` and, optionally, `SARVAM_API_KEY` as Space secrets. The Space
downloads the pinned BGE-M3 model, extractive QA model, and configured GGUF model during
startup; allow time and storage for these downloads.

The Space wrapper defaults to extractive-only answers to avoid slow generation calls. Set
`HH_RAG_FALLBACK=generative` in the Space variables to enable the configured generation
chain. The local FastAPI app defaults to the generative chain unless `HH_RAG_FALLBACK` is set.

## Configuration

| Variable | Purpose |
| --- | --- |
| `GNANI_API_KEY` | Gnani Prisma speech-to-text and Timbre text-to-speech |
| `SARVAM_API_KEY` | Sarvam speech-to-text and optional fallback |
| `HH_RAG_STT_PROVIDER` | Speech-to-text provider: `gnani` or `sarvam` |
| `HH_RAG_TTS_PROVIDER` | Text-to-speech provider: `gnani` or `off` |
| `HH_RAG_FALLBACK` | Answer fallback mode: `generative`, `fast_tier_only`, or `off` |
| `HH_RAG_GENERATOR` | Generation backend selection; `resilient` uses the configured chain |
| `HH_RAG_GENERATION_CHAIN` | Generation order, such as `local,groq` |
| `GROQ_API_KEY` | Optional Groq generation credentials |
| `HH_RAG_RETRIEVER_CONFIG` | Retrieval artifact configuration path |
| `HH_RAG_DEVICE` | Embedding device: `auto`, `cpu`, or a supported accelerator |
| `HH_RAG_API_TOKEN` | Optional bearer token for the FastAPI endpoints |
| `HH_RAG_BIND_HOST` / `HH_RAG_PORT` | FastAPI bind address and port |

Do not commit API keys or other secrets.

## Docker

Build and run the FastAPI service:

```bash
docker build -t cody-voice-rag .
docker run --rm --env-file .env -p 8000:8000 cody-voice-rag
```

Or start it with `docker compose up --build`. The container expects the configured model,
FAISS index, and chunk artifacts to be available at runtime. Follow the artifact paths in
`results/final_retriever_config.json`; model and data caches are not included in the image.

## Evaluation tools

The `eval/` directory contains scripts for retrieval, generation, guardrail, latency, and
speech evaluations. For example:

```bash
python eval/evaluate_retrieval.py --help
python eval/evaluate_generation.py --help
python eval/evaluate_e2e.py --help
```

Voice E2E evaluation requires recordings listed in an evaluation manifest, along with the
credentials and frozen retrieval artifacts used by the selected providers. Results are written
under `results/`; generated measurements are not included in a clean checkout.

## Project layout

- `app.py` — Gradio Space entry point.
- `src/cody_voice/` — Cody's retrieval, orchestration, speech, generation, and web application code.
- `src/cody_voice/static/` — browser interface assets.
- `scripts/` — artifact preparation and provider smoke-check scripts.
- `eval/` — evaluation and recording tools.
- `space_artifacts/` — serving index and chunk mapping used by the Space.
- `results/final_retriever_config.json` — retrieval model and artifact configuration.
