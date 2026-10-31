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

**Run the real pipeline:** install [Ollama](https://ollama.com), then:

```bash
ollama pull gemma3:4b             # gemma3:12b gives better extraction if your machine can run it
python -m playwright install chromium
python -m gateway crawl
python -m gateway stats
```

All commands are listed in [AGENTS.md](AGENTS.md#commands).

## Gemma options

Any OpenAI-compatible server works; set `LLM_BASE_URL` and `LLM_MODEL` in `.env`.

| Where | Notes |
|---|---|
| Ollama on a laptop | 4B runs on CPU. 12B needs about 10 GB of RAM and is slow on CPU; fine for pre-crawling |
| vLLM or a hosted endpoint | Much faster. Point `LLM_BASE_URL` at it and set `LLM_API_KEY` |

## Team

- @adhibskr: product and pipeline (Claude Code)
- @reiva5: engineering and web UI (GitHub Copilot)
