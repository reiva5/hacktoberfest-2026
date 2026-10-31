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

## Cached demo and extraction checks

`python -m gateway crawl --cached` reads only saved HTML; a missing or corrupt cache
entry is an explicit error, not a live-fetch fallback. Crawl and ingest exit nonzero
when a source or followed page fails. New cache entries preserve the final redirected
URL and fetch timestamp alongside the HTML; existing HTML-only entries remain readable.

For a fully offline replay with **no model calls**, use the same database and cache as
the successful extraction, and do not pass `--force`. Unchanged cleaned text skips
extraction. Changed or previously unprocessed cached pages still need Gemma;
`ingest --cached` deliberately re-extracts. Keep the DB/cache in ignored `data/`, and
export real records to a local or session-artifact path, never to committed fixtures.

Check eligibility, funding terms and application dates against the source before the
demo. Unknown countries/stages are not evidence of eligibility; a missing deadline is
not proof that applications are open. The current API's `is_open` treats a missing
deadline as open, so distinguish this computed count from manually confirmed open
calls when reporting crawl results. A newer organiser copy replaces older eligibility
and funding claims instead of unioning them into broader eligibility.

Before the Gemma-4-only policy, the 31 Oct P0 run reused Ollama and measured the first real CIP Spark ingest at
80.91 seconds with `gemma3:4b` on CPU. A `gemma3:12b` rerun using cached HTML took
207.74 seconds. The remaining crawl and ten-record audit were paused at the
user's request before their targets were met: 26 public page snapshots were
cached, but only 10 seed sources were processed, producing 19 **raw, unreviewed**
rows. Every stored row lacks an exact deadline; the API therefore computes all
19 as open, which is **not** a verified open-call count. Local exports and source
snapshots are session artifacts, not committed data. Do not use this partial
dataset to claim demo coverage or extraction accuracy.

The subsequent hosted Gemma 4 run stored 22 schema-validated records from seven
sources, with seven sources still failing and Devpost returning no programs.
This is a separate, local dataset and still requires factual spot-checking.
The historical Gemma 3 results do not validate the current Gemma 4 integration.

### Combining a real export with sample programs

A database merge is local, not a Git change. Keep real JSON exports, SQLite
databases and backups outside tracked files; a PR can document the operation
but must not contain the crawl itself. The UI continues to read only the HTTP API.

1. Identify the database used by the running API, including its working directory
   and `gateway.config.DB_PATH`. Different worktrees can serve different databases.
2. Select the intended export explicitly. Validate the complete JSON array with
   `Program.model_validate` from `gateway.schema` before writing any rows.
   Preserve each record's `source_url`, `last_verified`, issues and confidence;
   importing an export is not a fresh crawl or factual verification.
3. Back up the target with SQLite's `Connection.backup` into a separate local
   database. Use `gateway.store.upsert_program` for every validated record so the
   existing duplicate detection and authoritative merge rules apply. Do not clear
   the target or reload sample fixtures: that would remove or refresh existing data.
   Upserts commit individually; if an import fails, stop and restore the backup
   with the API stopped before retrying.
4. Verify `GET /programs?open_only=false`: compare all original sample records,
   check the imported source URLs, and record total/sample/real counts. Keep samples
   visibly labelled and describe raw crawl rows as unreviewed. Mixed totals from
   `/stats` and `/gapmap` are not real-only coverage or verified open-call counts.
5. Check the public preview as well as localhost. A public UI must reach the
   intended API; a visitor's `localhost:8000` is not the demo machine's API.

The 31 Oct local preview merge combined the historical 19-row export with eight
existing samples: HTTP verification found **27 records, eight sample and 19 real**,
with the samples preserved. The real rows remain unreviewed and have no exact
deadlines. This merge did **not** import the separate newer 22-row hosted Gemma 4
dataset described above, and it does not establish that the latest crawl is served.
The mixed-data banner and public-preview routing need to be checked separately.

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
