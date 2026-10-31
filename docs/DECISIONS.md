# Decisions

Newest last. Each entry records what we decided, why, and when to revisit it. Agents: add an entry whenever a product or technical decision is made.

### D1 · Start with programs and funding calls · 31 Oct
**Why:** Five categories is too much for two people and one day. Programs have deadlines and eligibility rules, which suits structured extraction, and they are what founders search for.
**Revisit:** After the hackathon. Funders are next.

### D2 · Aggregate first, direct listings later · 31 Oct
**Why:** Aggregating solves the cold start; the gateway is useful from day one without organisers doing anything. Organisers claiming their listings is the next phase.

### D3 · Model extraction, no CSS selectors · 31 Oct
**Why:** Selectors break whenever a site is redesigned. trafilatura plus Gemma filling a fixed schema survives layout changes (see `test_cleaning_survives_a_redesign`). Validation rules catch bad output instead of trusting it.

### D4 · Gemma behind an OpenAI-compatible client · 31 Oct
**Why:** The hackathon requires an open-source model. The same code runs on Ollama (laptop), vLLM, llama.cpp or a hosted endpoint by changing `.env`.
**Revisit:** If extraction quality is poor on 4B and no GPU is available.

### D5 · SQLite, with programs stored as JSON · 31 Oct
**Why:** No setup, and a single file. Querying needs are small.
**Revisit:** Next phase: Postgres + pgvector for embedding-based duplicate detection.

### D6 · The organiser's own page is the canonical record · 31 Oct
**Why:** The same program appears on several aggregators. We follow listings back to the organiser and keep aggregator URLs in `seen_on`. This is also how we prove "found X programs not on any aggregator".

### D7 · No LinkedIn or personal-data scraping · 31 Oct
**Why:** Against LinkedIn's terms, a risk under Malaysia's PDPA, and wrong for a public-sector sponsor. Talent will come as opt-in profiles.

### D8 · Respect crawler blocks · 31 Oct
**Why:** e27 returns 403 to our honest user agent. We skip it rather than spoofing a browser. Being responsible matters to a public body.

### D9 · Headless browser only as a fallback · 31 Oct
**Why:** Startup SG, Vietnam NIC and others build their pages with JavaScript. Playwright runs only when the fetched text is under 500 characters, which keeps crawling fast and light.

### D10 · Pitch deck upload as the main input · 31 Oct
**Why:** "It understood my startup" is a stronger demo moment than filling in a form. Gemma 3 reads slides as images. A plain form is the fallback.

### D11 · Gap map for the sponsor · 31 Oct
**Why:** It shows Startup ASEAN something it can't easily see today and justifies aggregating. It is always labelled "coverage so far", because an empty cell may only mean we haven't crawled there.

### D12 · Split by area, joined by the API contract · 31 Oct
**Why:** Two people with separate coding agents. The pipeline (@adhibskr, Claude) and the web UI (@reiva5, Copilot) meet only at `schema.py`, `api.py` and `docs/openapi.json`. CI checks that the contract file is current, and fictional sample data lets the UI be built before the model works.

### D13 · Gemma runs on the laptop CPU with Ollama · 31 Oct
**Why:** No GPU is available: the laptop has a 16 GB i7-1185G7 with integrated graphics. Everything is pre-crawled and cached; only the paste-a-URL step runs live.
**Revisit:** If someone offers GPU credits.

### D14 · Programme pages, not organisation homepages, are crawl seeds · 31 Oct
**Why:** Programme directories and detail pages give extraction funding and eligibility context instead of generic organisation descriptions. The reviewed URLs, JavaScript requirements, older cohorts and access limits are recorded in `sources.yaml` and the README. NIC's archived 2024 call is deferred until a current call is found; Techo's linked accelerator sites and F6S return 403 and are not enabled. No crawler or contract changes are needed.
**Revisit:** Before the real crawl, confirm cohort dates and Devpost listing content, and find accessible current Vietnam and Cambodia programme pages without bypassing blocks.
