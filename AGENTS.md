# AGENTS.md

Instructions for AI coding agents (Claude Code, GitHub Copilot) and the humans driving them. Read this whole file before changing code. If something here conflicts with a request, ask the human instead of guessing.

## What we're building

Hacktoberfest Kuala Lumpur, 31 Oct 2026. Startup ASEAN asked: *how can Startup ASEAN be the single gateway for discovering opportunities, programs, funding, talent and partners?*

Our answer starts narrow: **programs and funding calls across ASEAN** (accelerators, grants, competitions, government schemes).

1. A crawler collects program pages from seed sources and finds new ones.
2. Gemma, an open-source model, extracts each page into a structured record, including eligibility.
3. A founder uploads a pitch deck; Gemma reads it into a profile; we show programs they actually qualify for, with reasons.
4. Startup ASEAN sees a **gap map**: open programs by country × stage, showing where founders have nowhere to apply.

The pitch line is: aggregate institutions now, invite people later. A working 4-minute demo beats breadth. Product details: [docs/PRODUCT.md](docs/PRODUCT.md). Demo script: [docs/DEMO.md](docs/DEMO.md).

## Team and ownership

| Area | Paths | Owner | Usual agent |
|---|---|---|---|
| Pipeline and data | `gateway/` (except the contract files), `sources.yaml`, `tests/`, `fixtures/` | @reiva5 | GitHub Copilot |
| Web UI | `web/` | @adhibskr | Claude Code |
| Pitch, demo and ops | slides, demo inputs, `docs/DEMO.md` | @adhibskr | Claude Code |
| **Shared contract** | `gateway/schema.py`, `gateway/api.py`, `docs/openapi.json` | both | either; the other person approves the PR |
| Docs | `docs/`, `AGENTS.md`, `README.md` | both | either |

- Stay inside your area in a PR. If you need a change in the other area, open an issue or say so in the PR description.
- The web UI talks to the pipeline **only through the HTTP API**. It never reads SQLite or imports Python.
- Task list: [docs/BACKLOG.md](docs/BACKLOG.md) and GitHub issues.

## Hard rules

1. **The product uses open-source models only.** All model calls go to Gemma through the OpenAI-compatible client in `gateway/llm.py`. Never add OpenAI, Anthropic, Gemini or other proprietary model APIs to the product. Coding agents helping us write code are fine; the product itself is not.
2. **Every model call returns validated JSON.** Use `llm.chat_json(system, user, PydanticModel)`. Don't parse free text from the model.
3. **No CSS selectors or per-site scrapers.** Content comes from `clean.py` (trafilatura) plus model extraction. That's why redesigns don't break us. If a site is awkward, fix it in `sources.yaml` (a better URL), not in code.
4. **Crawl politely.** Respect robots.txt and `CRAWL_DELAY`, and keep the honest `USER_AGENT`. Never spoof a browser user agent or work around a block. e27 returns 403, so we skip it.
5. **No personal data.** No LinkedIn and no scraping of individual profiles. Organisations and public program pages only. Talent comes later as opt-in profiles.
6. **Don't invent facts.** Extraction uses only what's on the page. Sample data in `fixtures/` must be obviously fictional ("Sample …" names, `example.org` URLs).
7. **Never commit secrets or data.** No `.env`, no `data/`, no API keys.
8. **Tests run offline.** Stub `llm.chat_json` (see `tests/test_pipeline.py`). No test may call the network or a model.
9. **Contract changes need care.** If you change `schema.py` or `api.py`:
   - run `python -m gateway openapi` to regenerate `docs/openapi.json`;
   - update `fixtures/sample_programs.json` if fields changed;
   - put `[contract]` at the start of the PR title.

   CI fails if `docs/openapi.json` is out of date.

## Setup

```bash
python -m venv .venv
.venv/Scripts/activate                 # macOS/Linux: source .venv/bin/activate
pip install -e ".[api,vision,render,dev]" -c constraints.txt   # pinned versions, same as CI
python -m playwright install chromium  # only needed for crawling pages built with JavaScript
cp .env.example .env                   # then point LLM_BASE_URL / LLM_MODEL at your Gemma server
```

Gemma: `ollama pull gemma3:4b` (and `gemma3:12b` if your machine can handle it). See the README for options.

## Commands

```bash
pytest -q                                  # offline tests, about 1 second
python -m gateway seed-sample              # load fictional sample programs (no model needed)
python -m gateway serve                    # API on http://localhost:8000, docs at /docs
python -m gateway openapi                  # regenerate docs/openapi.json after contract changes
python -m gateway crawl [--cached] [--only portal]
python -m gateway ingest <url>             # paste-a-URL demo
python -m gateway deck <deck.pdf>          # deck → profile → matches
python -m gateway match --country MY --stage pre-seed --sector fintech --equity-free
python -m gateway gapmap | stats | list | sources | candidates | export
```

**For web UI work, no Gemma is needed:** run `seed-sample`, then `serve`, and build against `http://localhost:8000`. The `/deck` and `/ingest` endpoints do need Gemma.

## Architecture

```
sources.yaml → fetch → clean → extract (Gemma) → validate → dedupe → SQLite
                 │                                                │
                 └ headless browser if page text < 500 chars       ├→ match   ← profile ← deck (Gemma)
                                                                  ├→ gapmap, stats
                                                                  └→ api.py → web/
```

| Module | Job |
|---|---|
| `schema.py` | **The contract.** `ExtractedProgram` (what Gemma fills), `Program` (plus pipeline metadata), `Profile`, `Match` |
| `config.py` | Settings from env or `.env` |
| `llm.py` | OpenAI-compatible client; JSON-schema output; one self-correcting retry |
| `fetch.py` | robots.txt, per-host delay, disk cache, Playwright `render()` fallback |
| `clean.py` | HTML → markdown and links (no selectors) |
| `extract.py` | Page → `Program[]`; country normalisation; aggregator → organiser canonical URL |
| `validate.py` | Issues and confidence per record; detects when a source looks broken |
| `dedupe.py` | Same program from different pages → one record (organiser's copy wins) |
| `store.py` | SQLite: `programs`, `sources`, `candidates` |
| `pipeline.py` | Ingest and crawl orchestration, change detection, follow-through from aggregators |
| `discover.py` | Candidate links by keyword, then a yes/no check by the small model |
| `match.py` | Eligibility filter, then score, with reasons and warnings |
| `gapmap.py` | Country × stage counts; the four pitch numbers |
| `deck.py` | PDF → `Profile`, with the slide number for each field |
| `api.py` | FastAPI for the UI |
| `cli.py` | `python -m gateway …` |

## Conventions

**Python**
- Python 3.11+, type hints, pydantic v2.
- Each module opens with a short docstring saying *why* it exists. Comment only what isn't obvious.
- Match the style of the code around you. Keep functions small and plain; no frameworks beyond what's already in use.
- New dependencies go in `pyproject.toml`, in the right extra (`api`, `vision`, `render`, `dev`), and their pinned version goes in `constraints.txt`. Keep the core light.
- Windows-friendly: use `pathlib`; the CLI forces UTF-8 output (Thai, Khmer and Vietnamese text).
- A behaviour change comes with a test.

**Web (`web/`)**
- Any stack the owner likes. Read the API base URL from an environment variable; default to `http://localhost:8000`.
- Every program card shows its source link and "verified on" date. Trust is the product.
- Show match **reasons** and **warnings** as returned. Don't recompute eligibility in the UI.
- Label the gap map "coverage so far". An empty cell means we haven't found anything yet, not that nothing exists.
- `/deck` and `/ingest` can take 30 seconds to several minutes on a laptop CPU. Show progress and handle timeouts.
- Mark sample data as sample anywhere it could be mistaken for real data.

## Git workflow

- Never commit straight to `main`. Branch, open a PR, squash-merge.
- Branch names: `pipeline/<topic>`, `web/<topic>`, `docs/<topic>`, `contract/<topic>`.
- Small PRs that merge within about an hour. Pull `main` often; this is a one-day hackathon.
- CI (`.github/workflows/ci.yml`) must pass: tests, plus the check that `docs/openapi.json` is current.
- Agents: don't push to `main`, force-push, merge PRs, or change repo settings unless the human asks.
- When a product or technical decision is made, add it to [docs/DECISIONS.md](docs/DECISIONS.md).

## Definition of done

- It works in the demo flow ([docs/DEMO.md](docs/DEMO.md)) or is covered by a test.
- `pytest -q` passes and the OpenAPI check passes.
- Docs are updated if commands, the contract or a decision changed.

## Gotchas

- **Inference on a laptop CPU is slow.** Pre-crawl and use `crawl --cached` and the stored DB for the demo. Only the paste-a-URL moment runs live.
- Use 4B for discovery's yes/no checks. Use 12B (or larger, if hardware allows) for extraction quality.
- Startup SG, Vietnam NIC, MDEC, NIA and Antler need the headless browser. It's automatic if Playwright is installed.
- Seeds that are homepages give poor extraction. Point them at the actual programs page.
- `data/` is local only. Share a crawl by `export`ing JSON, never by committing the DB.
