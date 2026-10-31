# Demo script (about 4 minutes)

Two moments carry the demo: the **founder moment** (deck in, matches out) and the **sponsor moment** (the gap map). Everything else supports them.

## Before going on stage

Slides: [pitch deck](https://claude.ai/artifact/5R7KsFVBwNFipqC7NsrDCf) (speaker notes follow this script). Judges' Q&A and extra pre-stage checks: [PITCH_PREP.md](PITCH_PREP.md).

- [ ] Crawl finished and cached: `python -m gateway crawl --cached` runs without errors.
- [ ] `python -m gateway stats` numbers copied into the pitch.
- [ ] Sample deck PDF on the desktop, already tested end to end.
- [ ] One program URL that isn't in the DB yet, tested once (Bahasa Indonesia, Vietnamese or Khmer).
- [ ] One source page saved locally with its CSS changed, for the redesign moment.
- [ ] API running (`python -m gateway serve`) and the web UI open.
- [ ] **Fallback:** a screen recording of the whole flow, in case the live model is slow.

## Script

| # | Time | Show | Say |
|---|---|---|---|
| 1 | 0:00 | Problem slide | "There are hundreds of programs for ASEAN founders, spread across government, corporate and VC sites. Founders can't tell which ones they qualify for." |
| 2 | 0:30 | Stats header | "We found ___ open programs across ___ ASEAN countries. ___ close in the next 30 days. ___ aren't listed on any aggregator." |
| 3 | 0:50 | Upload a deck | "A founder drops in their pitch deck. Gemma, an open model, reads the slides." Point out the profile fields and the slide each came from. |
| 4 | 1:30 | Match cards | "Here's what they can apply to, why they qualify, and when it closes. Every card links to the organiser's own page." |
| 5 | 2:10 | Paste a non-English URL | "A new program page in Bahasa Indonesia comes back as a structured English record." |
| 6 | 2:50 | Gap map | "This is for Startup ASEAN: where in the region founders have nowhere to apply. Coverage so far, from ___ sources." |
| 7 | 3:20 | Restyled page (20 s) | "We don't use selectors, so when a site is redesigned the crawler still works." |
| 8 | 3:40 | Next-phase slide | "Next: organisers claim their listings, then funders. Talent is opt-in, never scraped." |

## If something breaks

- **Model too slow on stage:** switch to the recording at that step. Don't wait in silence.
- **Deck misread:** "Every field is editable, and that's why we show the slide it came from." Fix it live.
- **Network down:** everything except paste-a-URL works from the local DB.
