# Web UI brief (for @reiva5 and Copilot)

Paste this into Copilot as the task. It replaces the talent-portal draft (see [D14](DECISIONS.md)).

## Goal

Build the four screens the 4-minute demo needs ([DEMO.md](DEMO.md)). Nothing else today.

## Rules

- All code lives in `web/`. Any stack is fine.
- Read data **only** from the HTTP API. The base URL comes from an environment variable and defaults to `http://localhost:8000`. No browser-local storage of listings, no SQLite, no Python imports.
- Programs only. No talent, projects or other listing types (D1, D7).
- Show match reasons and warnings exactly as the API returns them. Don't recompute eligibility.
- Mark sample data as sample.

## Running it locally (no Gemma needed)

```bash
python -m gateway seed-sample
python -m gateway serve        # http://localhost:8000/docs
```

## Screens, in priority order

| # | Screen | Endpoint | Must show |
|---|---|---|---|
| 1 | Match cards | `POST /match` | title, organiser, score, reasons, warnings, deadline countdown, source link, "verified on" date |
| 2 | Deck upload → editable profile → matches | `POST /deck`, then `POST /match` | the slide number next to each profile field; progress while waiting (can take minutes); timeout message |
| 3 | Gap map | `GET /gapmap` | country × stage grid, empty cells highlighted, labelled "coverage so far" |
| 4 | Stats header | `GET /stats` | the four pitch numbers |
| P1 | Paste a URL | `POST /ingest` | progress and timeout handling, same as the deck |

Exact request and response shapes: `docs/openapi.json` or `http://localhost:8000/docs`.

## Reusable from the draft PR

Card layout, styles and filter UI can be moved into `web/`. Drop the type registry, relationships, the Node server and browser persistence.

## Done when

All four screens work against `seed-sample` data, and one end-to-end run through DEMO.md steps 3, 4 and 6 works.
