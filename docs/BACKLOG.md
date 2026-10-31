# Backlog

P0 = the demo fails without it. P1 = makes the demo much stronger. P2 = only if there's time.
Owners follow the areas in [AGENTS.md](../AGENTS.md) (split changed in [D15](DECISIONS.md)). Tick items off here, or mirror them as GitHub issues.

## Business, ops and web UI · @adhibskr (Claude Code)

Do these roughly in order. The first item unblocks the system work.

- [ ] **P0** Gather the demo inputs and hand them to @reiva5:
  - [x] 30 checked seed URLs: [SOURCES_PROPOSED.md](SOURCES_PROPOSED.md)
  - [ ] one sample pitch deck PDF, clearly fictional ("Sample …")
  - [x] non-English demo page (BRIN RISE 2026, Bahasa Indonesia), also in SOURCES_PROPOSED.md
- [ ] **P0** Scaffold `web/` against sample data (`seed-sample` + `serve`). Read the API URL from an environment variable. Brief: [WEB_BRIEF.md](WEB_BRIEF.md).
- [ ] **P0** Match card: title, organiser, score, reasons, warnings, deadline countdown, source link, "verified on".
- [ ] **P0** Gap map: country × stage grid with empty cells highlighted, labelled "coverage so far".
- [ ] **P0** Deck upload → editable profile (show the slide number for each field) → match list.
- [ ] **P0** Spot-check 10 crawled records against their source pages (target ≥ 85% of key fields correct). Report misses to @reiva5.
- [ ] **P1** Pitch slides: problem, numbers, live demo, gap map, next phase.
- [ ] **P1** Run `stats` and put the numbers in the pitch.
- [ ] **P1** Stats header showing the four pitch numbers from `/stats`.
- [ ] **P1** Paste-a-URL screen with progress for slow model calls (30 s to minutes) and a timeout message.
- [ ] **P1** Check the judging criteria and make sure the pitch answers each one.
- [ ] **P2** Plain profile form as a fallback when there's no deck.

## System (pipeline, data, API) · @reiva5 (Copilot)

- [ ] **P0** Close the talent-portal draft PR (D14). The UI now lives in `web/`, owned by @adhibskr.
- [ ] **P0** Install Ollama, pull `gemma3:4b` (and `gemma3:12b` if it runs acceptably), run the first real `ingest`, and record the time per page.
- [ ] **P0** Put the program-page URLs from @adhibskr into `sources.yaml`, replacing homepage seeds.
- [ ] **P0** Crawl and cache 30–50 records; make sure `crawl --cached` works offline.
- [ ] **P0** Fix extraction issues found in the spot-check.
- [ ] **P1** If CPU inference takes over 60 s, make `/ingest` and `/deck` return a job id and add `GET /jobs/{id}` (a `[contract]` PR).
- [ ] **P1** Test `deck` on the sample deck plus 1–2 real ones; tune the prompt.
- [ ] **P1** Test the non-English demo page end to end.
- [ ] **P2** Run discovery from 3 seeds and approve any good candidates.

## Shared

- [ ] **P0** Rehearse the demo end to end ([DEMO.md](DEMO.md)) and record a fallback video.
- [ ] **P1** Share the roadmap page (`gateway-roadmap.html`) with judges if useful.
