# Web UI

Owner: @adhibskr (Claude Code). Plain HTML, CSS and JavaScript with no build step. It talks to the pipeline only through the HTTP API.

## Run it

```bash
python -m gateway seed-sample     # fictional programs, no model needed
python -m gateway serve           # API on http://localhost:8000
python web/serve.py               # UI on http://localhost:5173
```

The API address comes from the `API_BASE` environment variable (default `http://localhost:8000`). `WEB_PORT` changes the UI port.

## Screens

| Screen | Endpoint | Notes |
|---|---|---|
| Stats header | `GET /stats` | The four pitch numbers. A banner appears when sample data is loaded. |
| Deck upload → profile | `POST /deck` | Progress timer, cancel button, 10-minute timeout. Each field shows the slide it came from. Falls back to the form on any error. |
| Profile form → matches | `POST /match` | Reasons and warnings are shown exactly as the API returns them. |
| Match card | — | Type, countries, score, summary, deadline countdown, amount, equity, reasons, warnings, organiser link and "verified on" date. |
| Gap map | `GET /gapmap` | Country × stage, labelled "coverage so far"; empty cells highlighted. |

Not built yet: the paste-a-URL screen (P1).

All page text comes from crawled sites, so `app.js` escapes it and only allows http(s) links.
