# Backlog

P0 = the demo fails without it. P1 = makes the demo much stronger. P2 = only if there's time.
Owners follow the areas in [AGENTS.md](../AGENTS.md) (split changed in [D15](DECISIONS.md)). Tick items off here, or mirror them as GitHub issues.

## Business, ops and web UI · @adhibskr (Claude Code)

Do these roughly in order. The first item unblocks the system work.

- [x] **P0** Gather the demo inputs and hand them to @reiva5:
  - [x] 30 checked seed URLs: [SOURCES_PROPOSED.md](SOURCES_PROPOSED.md)
  - [x] fictional sample pitch deck: [demo/sample_deck.pdf](../demo/sample_deck.pdf), answer key in [demo/README.md](../demo/README.md)
  - [x] non-English demo page (BRIN RISE 2026, Bahasa Indonesia), also in SOURCES_PROPOSED.md
- [x] **P0** Scaffold `web/` against sample data (`seed-sample` + `serve`). Read the API URL from an environment variable. Brief: [WEB_BRIEF.md](WEB_BRIEF.md). Implemented in #5.
- [x] **P1** Match the web UI to the pitch deck (palette, Manrope, logo). D20.
- [x] **P0** Match card: title, organiser, score, reasons, warnings, deadline countdown, source link, "verified on". Implemented in #5.
- [x] **P0** Gap map: country × stage grid with empty cells highlighted, labelled "coverage so far". Implemented in #5.
- [x] **P0** Deck upload → editable profile (show the slide number for each field) → match list. Implemented in #5; real-deck testing remains below.
- [ ] **P0** Spot-check 10 crawled records against their source pages (target ≥ 85% of key fields correct). Report misses to @reiva5. Deferred with the remaining crawl on 31 Oct; the ten-record audit and ≥85% target are not complete. The initial 4B/12B mismatch review and explicit audit rubric are saved as session artifacts.
- [ ] **P1** Pitch slides: problem, numbers, live demo, gap map, next phase. Draft done ([deck](https://claude.ai/artifact/5R7KsFVBwNFipqC7NsrDCf), private until shared); fill the `[__]` placeholders after the crawl and add a gap-map screenshot.
- [ ] **P1** Run `stats` and put the numbers in the pitch.
- [x] **P1** Stats header showing the four pitch numbers from `/stats`. Implemented in #5.
- [x] **P1** Paste-a-URL screen with progress for slow model calls (30 s to minutes) and a timeout message. Implemented in #5.
- [x] **P1** Update pitch prep (Q5, Q7), the demo script and UI progress text for hosted Gemma 4 on the Gemini API (D21). Team name recorded as Fundbound (D23).
- [ ] **P1** Check the judging criteria and make sure the pitch answers each one. Assumed criteria, mapping and 12 likely questions in [PITCH_PREP.md](PITCH_PREP.md); still need the official rubric from the organisers, plus an answer for "what did you build today" (business model decided: D19).
- [x] **P2** Plain profile form as a fallback when there's no deck. Implemented in #5.

## System (pipeline, data, API) · @reiva5 (Copilot)

- [ ] **P0** Close the talent-portal draft PR (D14). The UI now lives in `web/`, owned by @adhibskr.
- [x] **P0** Historical local setup before the Gemma-4-only policy: installed Ollama and ran the first real `ingest`. Real CIP Spark ingestion with `gemma3:4b` took 80.91 s on CPU; a `gemma3:12b` cached-HTML rerun took 207.74 s and corrected the country and equity-free claims, but stage errors remain. This is not current Gemma 4 validation or a claim of audit readiness.
- [x] **P0** Configure Gemma 4 via Gemini API or local Ollama (`gemma4:e4b`), run the first real ingestion, and record the time per page (D21). Hosted `gemma-4-31b-it` persisted MRANTI GAP in 86.8 s and MDEC's two grants in 43.5 s; several other seeds returned API HTTP 500. Spot-check these records before the demo; GAP describes an older cohort.
- [x] **P0** Add Gemini API integration restricted to Gemma 4, with external key-file loading, offline transport tests and updated agent rules (D21).
- [x] **P0** Replace homepage seeds in `sources.yaml` with actual programs or apply pages. Reviewed 31 Oct in #4: programme URLs and JavaScript requirements documented; NIC's archived call and blocked Techo links deferred (see README and D16).
- [ ] **P0** Crawl and cache 30–50 records; make sure `crawl --cached` works offline. Gemma 4 API runs stored 22 records from seven sources after retrying failed pages with the other allowed Gemma 4 model. Seven sources still report API HTTP 500 or invalid JSON after correction; Devpost returned no programs. HTML and records are local in ignored `data/`; replay of the first three successful cached pages was verified without network/model calls, but re-extraction still needs the model. The earlier local Gemma 3 run was paused at the user's request with 26 public pages cached, 10 seed sources processed and 19 raw rows; its processed subset replays offline and five seeds remain unprocessed. These are separate partial datasets, neither a verified 30–50-record dataset.
- [ ] **P0** Fix extraction issues found in the spot-check. Cache-only replay, authoritative merges and extraction instructions improved, but stage, equity-unit and programme-versus-benefit errors remain in the partial export.
- [ ] **P1** If CPU inference takes over 60 s, make `/ingest` and `/deck` return a job id and add `GET /jobs/{id}` (a `[contract]` PR).
- [ ] **P1** Test `deck` on the sample deck plus 1–2 real ones; tune the prompt.
- [ ] **P1** Test the non-English demo page end to end.
- [ ] **P2** Run discovery from 3 seeds and approve any good candidates.

## Shared

- [x] **P0** Merge the selected real crawl into the local sample preview without committing data. HTTP verification on 31 Oct found 27 records: eight preserved samples and 19 historical raw crawl rows. This did not import the separate newer 22-row Gemma 4 dataset or complete the extraction audit; procedure and caveats are in the README.
- [ ] **P0** Confirm the public preview reaches the merged API and replace sample-only banner wording with accurate mixed-data wording. Preserve individual sample labels; do not present raw crawl rows or combined statistics as verified real coverage.
- [ ] **P0** Test the sample deck and the BRIN RISE paste end to end on `gemma-4-31b-it`, and time both for [DEMO.md](DEMO.md) (issue #14).
- [ ] **P0** Rehearse the demo end to end ([DEMO.md](DEMO.md)) and record a fallback video. The live steps need the Gemini API, so check the venue Wi-Fi and have the video ready if the network drops.
- [ ] **P1** Share the roadmap page (`gateway-roadmap.html`) with judges if useful.
