# Copilot instructions

The full instructions for this repo are in [AGENTS.md](../AGENTS.md); read it first. The essentials:

- **Project:** a Startup ASEAN gateway for startup programs and funding. A crawler and Gemma extract programs; founders upload a pitch deck and get matched programs; Startup ASEAN sees a gap map. Hackathon demo on 31 Oct 2026.
- **Your usual area is `web/`.** The UI talks to the pipeline only through the HTTP API (`python -m gateway serve`, contract in `docs/openapi.json` and `gateway/schema.py`). Never read SQLite or import Python from the UI.
- **To build the UI without a model:** run `python -m gateway seed-sample`, then `python -m gateway serve`. `/deck` and `/ingest` need Gemma and can take minutes on a laptop, so show progress and handle timeouts.
- **Display rules:**
  - Every program card shows its source link and "verified on" date.
  - Show match `reasons` and `warnings` exactly as the API returns them; don't recompute eligibility.
  - Label the gap map "coverage so far".
- **Product model:** Gemma 4 only through `gateway/llm.py`. Gemini API is allowed only for hosted Gemma 4 (`gemma-4-31b-it` or `gemma-4-26b-a4b-it`), never Gemini models. No OpenAI, Anthropic or other proprietary models. Keep API keys external and out of logs and Git.
- **Contract changes** (`gateway/schema.py`, `gateway/api.py`) need `python -m gateway openapi` and a `[contract]` PR title; the other owner approves.
- **Workflow:**
  - Branch as `web/<topic>`, keep PRs small, and make sure CI passes.
  - Never commit `.env`, `data/` or keys.
  - Don't push to `main`.
