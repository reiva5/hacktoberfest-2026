# Demo script (about 4 minutes)

Two moments carry the demo: the **founder moment** (deck in, matches out) and the **sponsor moment** (the gap map). Everything else supports them.

## Before going on stage

Slides: [pitch deck](https://claude.ai/artifact/5R7KsFVBwNFipqC7NsrDCf) (speaker notes follow this script).

- [ ] Crawl finished and cached: `python -m gateway crawl --cached` runs without errors.
- [ ] `python -m gateway stats` numbers copied into the pitch.
- [ ] Sample deck PDF on the desktop, already tested end to end.
- [ ] One program URL that isn't in the DB yet, tested once (Bahasa Indonesia, Vietnamese or Khmer).
- [ ] One source page saved locally with its CSS changed, for the redesign moment.
- [ ] API running (`python -m gateway serve`) and the web UI open.
- [ ] **Fallback:** a screen recording of the whole flow, in case the live model is slow.

## Script

Slides 1–5 must fit in about 65 seconds. Don't read the cards aloud; say the line and move on.

| # | Time | Show | Say |
|---|---|---|---|
| 1 | 0:00 | Slides 1–2: cover, problem | "Every ASEAN founder asks: which programs can I apply to? They're spread across government, corporate and VC sites, in five languages, with the rules buried. Directories list programs; none tell you which ones you qualify for." |
| 2 | 0:20 | Slide 3: scope | "Startup ASEAN asked for one gateway to programs, funding, talent and partners. We build it in order. Today: programs and funding calls." |
| 3 | 0:35 | Slide 4: why programs first | "They have deadlines and eligibility rules, which is where an open model adds value. They're what founders look for first. And they need no personal data." |
| 4 | 0:50 | Slide 5: numbers | "We found ___ open programs across ___ ASEAN countries. ___ close in the next 30 days. ___ aren't listed on any aggregator." |
| 5 | 1:05 | Slide 6: live demo, then the web UI | "Two moments: one for founders, one for Startup ASEAN." Switch to the UI. |
| 6 | 1:10 | Upload a deck | "A founder drops in their pitch deck. Gemma, an open model, reads the slides." Point out the profile fields and the slide each came from. |
| 7 | 1:45 | Match cards | "Here's what they can apply to, why they qualify, and when it closes. Every card links to the organiser's own page." |
| 8 | 2:15 | Paste a non-English URL | "A new program page in Bahasa Indonesia comes back as a structured English record." |
| 9 | 2:50 | Gap map (UI; slide 7 is the backup) | "This is for Startup ASEAN: where in the region founders have nowhere to apply. Coverage so far, from ___ sources." |
| 10 | 3:15 | Restyled page (20 s) | "We don't use selectors, so when a site is redesigned the crawler still works." |
| 11 | 3:35 | Slide 8: next phase | "Next: organisers claim their listings, then funders. Talent is opt-in, never scraped." |
| 12 | 3:50 | Slide 9: close | "Aggregate institutions now. Invite people later." Then the ask. |

Slides 10–11 (how it works, responsible by design) are backup for questions.

## If something breaks

- **Model too slow on stage:** switch to the recording at that step. Don't wait in silence.
- **Deck misread:** "Every field is editable, and that's why we show the slide it came from." Fix it live.
- **Network down:** everything except paste-a-URL works from the local DB.
