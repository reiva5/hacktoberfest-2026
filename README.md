# hacktoberfest-2026 · Startup ASEAN Gateway

Hacktoberfest Kuala Lumpur, 31 Oct 2026. One place for ASEAN founders to find startup programs and funding they **actually qualify for**, and for Startup ASEAN to see where the region has gaps.

- A crawler collects program pages; **Gemma** (open model) extracts them into structured records, eligibility included.
- A founder uploads a **pitch deck** → Gemma reads it into a profile → ranked matches with reasons, deadlines and sources.
- A **gap map** shows open programs by country × stage.

| Read this | For |
|---|---|
| [AGENTS.md](AGENTS.md) | How we work: rules, ownership, commands, architecture. Coding agents read this too |
| [docs/PRODUCT.md](docs/PRODUCT.md) | Problem, users, MVP vs next phase, risks |
| [docs/DEMO.md](docs/DEMO.md) | The 4-minute demo script and fallbacks |
| [docs/BACKLOG.md](docs/BACKLOG.md) | Who's doing what |
| [docs/DECISIONS.md](docs/DECISIONS.md) | What we decided and why |
| [gateway-roadmap.html](gateway-roadmap.html) | Visual roadmap (open in a browser) |

## Quick start

```bash
python -m venv .venv
.venv/Scripts/activate            # macOS/Linux: source .venv/bin/activate
pip install -e ".[api,vision,render,dev]" -c constraints.txt
cp .env.example .env
pytest -q
```

**Build the UI without a model:**

```bash
python -m gateway seed-sample     # fictional sample programs
python -m gateway serve           # http://localhost:8000/docs
```

Start the UI in a second terminal with `python web\serve.py`, then open
http://localhost:5173. This also works with real crawled data; omit `seed-sample`
when you want to keep your database free of fictional records.

**Run the real pipeline with hosted Gemma 4:** in your ignored `.env`, set
`LLM_PROVIDER=gemini`, `LLM_MODEL=gemma-4-31b-it` and
`LLM_SMALL_MODEL=gemma-4-31b-it`. Set `LLM_API_KEY_FILE` to the absolute path
of an external UTF-8 file containing only your Google AI Studio key.
Do not paste the key into commands, logs or Git. The client sends it in an
authentication header and does not include response bodies in request errors.

```bash
python -m playwright install chromium
python -m gateway ingest https://cradle.com.my/cip-spark/
python -m gateway crawl
python -m gateway stats
```

For local inference, install [Ollama](https://ollama.com), run `ollama pull gemma4:e4b`,
and set `LLM_PROVIDER=openai`, `LLM_MODEL=gemma4:e4b`, `LLM_SMALL_MODEL=gemma4:e4b`,
`LLM_BASE_URL=http://localhost:11434/v1` and `LLM_API_KEY=ollama`.
Unset `LLM_API_KEY_FILE` when switching to local inference.

All commands are listed in [AGENTS.md](AGENTS.md#commands).

## Seed sources

`sources.yaml` uses programme directories and detail pages instead of organisation homepages.
The 31 Oct review checked the replacement URLs with the crawler's honest user agent and
`clean.py`, using the existing Playwright fallback for pages with under 500 characters of
static text. No model extraction or full crawl was run as part of this review.

- Cradle CIP Spark/Sprint, Antler Singapore, ADB NextFin Asia and Thai NIA financial support
  provide programme details directly. NIA supplies the non-English seed.
- MYStartup's founder programmes, Startup SG Tech eligibility, MDEC Digital Content Grant
  and SGInnovate's public calls require Playwright/Chromium. MDEC links detailed eligibility
  PDFs; the HTML pipeline does not ingest those PDFs automatically.
- MRANTI's GAP page still describes its 2025 cohort. A seed is not evidence of an open call:
  verify dates before the demo, and do not assume support or investor access means cash funding.
- Vietnam NIC is deferred until a current programme page is found; the verified alternative
  is an archived 2024 call. Cambodia Techo's linked accelerator sites and F6S return HTTP 403
  and are not active seeds. This is a discovery gap, not evidence that those countries lack funding.
- The existing Devpost discovery seed is retained, but its static response contains navigation
  rather than opportunity details. Confirm actual listing content before relying on it.

Offline seed configuration checks: `python -m pytest -q tests/test_sources.py`.
Before model ingestion, start with one detail page:
`python -m gateway ingest https://cradle.com.my/cip-spark/`.

## Gemma options

Only Gemma 4 is allowed, including discovery and deck processing. Older Gemma and
proprietary models are rejected before a request is sent. Set `LLM_PROVIDER` in
`.env`; environment variables take precedence.

| Where | Notes |
|---|---|
| Gemini API (`LLM_PROVIDER=gemini`) | `gemma-4-26b-a4b-it` or `gemma-4-31b-it` only. Uses Google's fixed HTTPS endpoint; ignores `LLM_BASE_URL`. Set `LLM_API_KEY_FILE` or `LLM_API_KEY`; file takes precedence |
| Ollama (`LLM_PROVIDER=openai`) | Gemma 4 E4B is the default local model; larger Gemma 4 variants need more memory |
| vLLM or another OpenAI-compatible Gemma 4 server | Point `LLM_BASE_URL` at it and set `LLM_API_KEY` or `LLM_API_KEY_FILE`. Use a Gemma 4 model ID |

Gemini requests include the output schema in the system instruction; every result
is validated with Pydantic, with one correction retry for invalid JSON. API failures,
blocked responses and truncated output are reported explicitly. Crawled pages and
their schemas are sent to Google for hosted inference; keys, local configuration,
SQLite and page caches remain untracked. `crawl --cached` reuses saved page HTML,
but changed or forced extraction still needs a model connection.

Transient Gemini API HTTP 500/502/503/504 failures are retried once after two
seconds using the same Gemma 4 model. Persistent failures are reported without
response bodies or credentials; authentication and quota errors are not retried.

## Team

- @adhibskr: product, business, pitch and web UI (Claude Code)
- @reiva5: engineering: pipeline, data and API (GitHub Copilot)
