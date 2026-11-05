# Demo script (about 4 minutes)

Two moments carry the demo: the **founder moment** (deck in, matches out) and the **sponsor moment** (the gap map). Everything else supports them.

## Before going on stage

Slides: [pitch deck](https://claude.ai/artifact/5R7KsFVBwNFipqC7NsrDCf) (speaker notes follow this script). Judges' Q&A and extra pre-stage checks: [PITCH_PREP.md](PITCH_PREP.md).

- [ ] Crawl finished and cached: `python -m gateway crawl --cached` runs without errors.
- [ ] `python -m gateway stats` numbers copied into the pitch.
- [ ] Sample deck PDF on the desktop, already tested end to end.
- [ ] One program URL that isn't in the DB yet, tested once (Bahasa Indonesia, Vietnamese or Khmer).
- [ ] One source page saved locally with its CSS changed, for the redesign moment.
- [ ] Gemini API key file set (`LLM_PROVIDER=gemini`, `LLM_API_KEY_FILE`) and quota checked; venue Wi-Fi tested.
- [ ] API running (`python -m gateway serve`) and the web UI open.
- [ ] **Fallback:** a screen recording of the whole flow, in case the live model is slow or the network drops.

## Timing plan: start slow model steps early

Gemma 4 runs through the Gemini API, and it is still slow: one program page took 44–87 s in the hosted crawl, and reading the sample deck takes **about 3–5 minutes**. The API handles one request at a time, and while a deck is being read the whole API freezes (stats, matches and gap map included). So run the slow steps **in sequence and ahead of time**, never while the audience waits.

| When | Who | Do |
|---|---|---|
| Setup, **at least 6 min before the slot** | [name] | **Tab 1, Find programs:** upload `demo/sample_deck.pdf`. Wait until the profile and match cards show (3–5 min). **Don't refresh this tab afterwards**: the profile isn't saved anywhere. |
| Setup | [name] | **Tab 2, Add a program:** paste the BRIN RISE URL. **Don't click Read page yet.** |
| Setup | [name] | **Tab 3, Gap map:** open it once so it's loaded. Then put the slides on screen. |
| **0:00**, before the first word | presenter | Click **Read page** in tab 2, then switch to the slides. At 44–87 s per page it should finish by about 1:30, ahead of row 9 at 2:20. |

- The API (`serve`) uses hosted Gemma 4 (`gemma-4-31b-it`, see the README). The hosted API sometimes returns HTTP 500; if the paste fails, use the recording for that step.
- The demo needs network for the deck upload and the paste. Check the venue Wi-Fi during setup.
- Say plainly that the deck was read during setup. Honesty is part of the pitch.

## Script

Slides 1–6 must fit in about 70 seconds. Don't read the cards aloud; say the line and move on.

| # | Time | Show | Say |
|---|---|---|---|
| 1 | 0:00 | Slides 1–2: cover, problem | "Every ASEAN founder asks: which programs can I apply to? They're spread across government, corporate and VC sites, in five languages, with the rules buried. Directories list programs; none tell you which ones you qualify for." |
| 2 | 0:20 | Slide 3: scope | "Startup ASEAN asked for one gateway to programs, funding, talent and partners. We build it in order. Today: programs and funding calls." |
| 3 | 0:30 | Slide 4: why programs first | "They have deadlines and eligibility rules, which is where an open model adds value. They're what founders look for first. And they need no personal data." |
| 4 | 0:45 | Slide 5: Gemma 4 | "Gemma 4 does all the reading: pitch decks as images, program pages in any language, and new links. You'll see two of those live." |
| 5 | 1:00 | Slide 6: numbers | "One day, 15 public sources. Gemma 4 read 22 programs from 7 of them. We have national sources in only four countries so far, which is what the gap map shows." |
| 6 | 1:10 | Slide 7: live demo, then the web UI | "Two moments: one for founders, one for Startup ASEAN." Switch to the UI. |
| 7 | 1:15 | Tab 1: deck result (read during setup) | "A founder drops in their pitch deck. Gemma 4 read it while we set up: about 3 to 5 minutes, through the Gemini API." Point out the profile fields and the slide each came from. |
| 8 | 1:50 | Match cards | "Here's what they can apply to, why they qualify, and when it closes. Every card links to the organiser's own page." |
| 9 | 2:20 | Tab 2: paste result (started at 0:00) | "We pasted a new program page in Bahasa Indonesia when we started talking. Here it is as a structured English record." Point at the "Translated from Bahasa Indonesia" tag and the eligibility list. |
| 10 | 2:55 | Gap map (UI; slide 8 is the backup) | "This is for Startup ASEAN: where in the region founders have nowhere to apply. Coverage so far, from 15 sources." |
| 11 | 3:20 | Restyled page (20 s, **cut first**; skip it unless you're ahead of time) | "We don't use selectors, so when a site is redesigned the crawler still works." |
| 12 | 3:40 | Slide 9: next phase | "Next: organisers claim their listings, then funders. Talent is opt-in, never scraped." |
| 13 | 3:55 | Slide 10: close | "Aggregate institutions now. Invite people later." Then the ask. |

Without row 11 the pitch ends at about 3:50; with it, about 4:10.

Slides 11–12 (how it works, responsible by design) are backup for questions.

## If something breaks

- **Model too slow on stage:** switch to the recording at that step. Don't wait in silence.
- **Paste not finished by 2:20:** "It's still reading. Let's look at the gap map and come back." Do row 10, then return to tab 2.
- **Tab 1 refreshed by accident:** the profile is gone. Fill in the form with the PadiSense answers (MY, pre-seed, agritech/ai, prefers equity-free) and click Find programs, or play the recording.
- **Don't press Cancel** on the paste: the server keeps going anyway.
- **Deck misread:** "Every field is editable, and that's why we show the slide it came from." Fix it live.
- **Network down:** matches and the gap map still work from the local DB (and the deck already read in tab 1). Paste-a-URL and new deck uploads need the Gemini API, so play the recording for those.
