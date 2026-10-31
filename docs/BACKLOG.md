# Backlog

P0 = the demo fails without it. P1 = makes the demo much stronger. P2 = only if there's time.
Owners follow the areas in [AGENTS.md](../AGENTS.md). Tick items off here, or mirror them as GitHub issues.

## Pipeline and data · @adhibskr (Claude Code)

- [x] **P0** Install Ollama, pull `gemma3:4b` (and `gemma3:12b` if it runs acceptably), run the first real `ingest`, and record the time per page. Reused local Ollama on 31 Oct; real CIP Spark ingestion with 4B took 80.91 s on CPU. A 12B rerun using cached HTML took 207.74 s and corrected the country and equity-free claims, but stage errors remain. This is not a claim of audit readiness.
- [x] **P0** Replace homepage seeds in `sources.yaml` with actual programs or apply pages. Reviewed 31 Oct: programme URLs and JavaScript requirements documented; NIC's archived call and blocked Techo links deferred (see README).
- [ ] **P0** Crawl and cache 30–50 records; make sure `crawl --cached` works offline. Paused at the user's request on 31 Oct to open the pipeline PR: 26 public pages cached, 10 seed sources processed, 19 raw extraction rows stored. Non-programme rows and unsupported fields remain; this is not a verified 30–50-record dataset.
- [ ] **P0** Spot-check 10 records against their source pages (target ≥ 85% of key fields correct). Deferred with the remaining crawl. Initial 4B/12B spot-checks found eligibility, stage, equity-unit and programme-versus-benefit errors. The ten-record audit and ≥85% target are not complete; local exports and the explicit audit rubric are saved as session artifacts.
- [ ] **P1** If CPU inference takes over 60 s, make `/ingest` and `/deck` return a job id and add `GET /jobs/{id}` (a `[contract]` PR).
- [ ] **P1** Test `deck` on 2–3 real pitch decks; tune the prompt.
- [ ] **P1** Pick and test the non-English demo page.
- [ ] **P1** Run `stats` and put the numbers in the pitch.
- [ ] **P2** Run discovery from 3 seeds and approve any good candidates.

## Web UI · @reiva5 (Copilot)

- [ ] **P0** Scaffold `web/` against sample data (`seed-sample` + `serve`). Read the API URL from an environment variable.
- [ ] **P0** Deck upload → editable profile (show the slide number for each field) → match list.
- [ ] **P0** Match card: title, organiser, score, reasons, warnings, deadline countdown, source link, "verified on".
- [ ] **P0** Gap map: country × stage grid with empty cells highlighted, labelled "coverage so far".
- [ ] **P1** Paste-a-URL screen with progress for slow model calls (30 s to minutes) and a timeout message.
- [ ] **P1** Stats header showing the four pitch numbers from `/stats`.
- [ ] **P2** Plain profile form as a fallback when there's no deck.

## Shared

- [ ] **P0** Rehearse the demo end to end ([DEMO.md](DEMO.md)) and record a fallback video.
- [ ] **P1** Pitch slides: problem, numbers, live demo, gap map, next phase.
- [ ] **P1** Share the roadmap page (`gateway-roadmap.html`) with judges if useful.
