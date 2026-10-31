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

## Timing plan: start slow model steps early

On a laptop CPU one model call takes minutes (one page: about 81 s with 4B, 208 s with 12B; a deck: [__] s, measure it at rehearsal). The model handles one request at a time, and while a deck is being read the whole API freezes (stats, matches and gap map included). So run the slow steps **in sequence and ahead of time**, never while the audience waits.

| When | Who | Do |
|---|---|---|
| Setup, ~5 min before the slot | [name] | **Tab 1, Find programs:** upload `demo/sample_deck.pdf`. Wait until the profile and match cards show. **Don't refresh this tab afterwards**: the profile isn't saved anywhere. |
| Setup | [name] | **Tab 2, Add a program:** paste the BRIN RISE URL. **Don't click Read page yet.** |
| Setup | [name] | **Tab 3, Gap map:** open it once so it's loaded. Then put the slides on screen. |
| **0:00**, before the first word | presenter | Click **Read page** in tab 2, then switch to the slides. It finishes by about 1:30 with 4B, ahead of row 8 at 2:15. |

- The API (`serve`) must use the **4B** model for the live paste (`LLM_MODEL` in `.env`). 12B takes about 3.5 minutes and won't be ready in time. The crawl can still use 12B beforehand. @reiva5 to confirm.
- Say plainly that the deck was read during setup. Honesty is part of the pitch.

## Script

Slides 1–5 must fit in about 65 seconds. Don't read the cards aloud; say the line and move on.

| # | Time | Show | Say |
|---|---|---|---|
| 1 | 0:00 | Slides 1–2: cover, problem | "Every ASEAN founder asks: which programs can I apply to? They're spread across government, corporate and VC sites, in five languages, with the rules buried. Directories list programs; none tell you which ones you qualify for." |
| 2 | 0:20 | Slide 3: scope | "Startup ASEAN asked for one gateway to programs, funding, talent and partners. We build it in order. Today: programs and funding calls." |
| 3 | 0:35 | Slide 4: why programs first | "They have deadlines and eligibility rules, which is where an open model adds value. They're what founders look for first. And they need no personal data." |
| 4 | 0:50 | Slide 5: numbers | "We found ___ open programs across ___ ASEAN countries. ___ close in the next 30 days. ___ aren't listed on any aggregator." |
| 5 | 1:05 | Slide 6: live demo, then the web UI | "Two moments: one for founders, one for Startup ASEAN." Switch to the UI. |
| 6 | 1:10 | Tab 1: deck result (read during setup) | "A founder drops in their pitch deck. Gemma, an open model, read it while we set up: about [__] on this laptop's CPU." Point out the profile fields and the slide each came from. |
| 7 | 1:45 | Match cards | "Here's what they can apply to, why they qualify, and when it closes. Every card links to the organiser's own page." |
| 8 | 2:15 | Tab 2: paste result (started at 0:00) | "We pasted a new program page in Bahasa Indonesia when we started talking. Here it is as a structured English record." Point at the "Translated from Bahasa Indonesia" tag and the eligibility list. |
| 9 | 2:50 | Gap map (UI; slide 7 is the backup) | "This is for Startup ASEAN: where in the region founders have nowhere to apply. Coverage so far, from ___ sources." |
| 10 | 3:15 | Restyled page (20 s, **cut first** if running long) | "We don't use selectors, so when a site is redesigned the crawler still works." |
| 11 | 3:35 | Slide 8: next phase | "Next: organisers claim their listings, then funders. Talent is opt-in, never scraped." |
| 12 | 3:50 | Slide 9: close | "Aggregate institutions now. Invite people later." Then the ask. |

Slides 10–11 (how it works, responsible by design) are backup for questions.

## If something breaks

- **Model too slow on stage:** switch to the recording at that step. Don't wait in silence.
- **Paste not finished by 2:15:** "It's still reading. Let's look at the gap map and come back." Do row 9, then return to tab 2.
- **Tab 1 refreshed by accident:** the profile is gone. Fill in the form with the PadiSense answers (MY, pre-seed, agritech/ai, prefers equity-free) and click Find programs, or play the recording.
- **Don't press Cancel** on the paste: the server keeps going anyway.
- **Deck misread:** "Every field is editable, and that's why we show the slide it came from." Fix it live.
- **Network down:** everything except paste-a-URL works from the local DB.
