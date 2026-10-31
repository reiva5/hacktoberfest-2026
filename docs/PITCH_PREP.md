# Pitch prep

Owner: @adhibskr. Goes with the [pitch deck](https://claude.ai/artifact/5R7KsFVBwNFipqC7NsrDCf) and [DEMO.md](DEMO.md).

## Judging criteria

**No official criteria found online (31 Oct).** Ask the organisers' desk for the rubric and replace this table. Until then we assume the usual hackathon criteria, plus fit with what Startup ASEAN asked.

| Assumed criterion | Where the pitch answers it | Proof on stage |
|---|---|---|
| **Fit with the challenge**: "single gateway for opportunities, programs, funding, talent and partners" | Cover, next-phase slide | Phased plan: programs now → funders → opt-in talent and partners |
| **Problem and impact**: real founder pain, real value for the sponsor | Problem slide, gap-map slide | Gap map: where founders have nowhere to apply |
| **Innovation**: what's new vs. F6S, e27 and other directories | Problem slide (last line) | Match cards with *reasons* and *warnings*, not just a list |
| **Technical execution**: does it actually work? | Live demo | Deck → profile → matches; non-English page → English record; restyled page still extracts |
| **Feasibility and scale**: can it grow past a hackathon? | Next-phase slide, backup "How it works" | No per-site scrapers; same pipeline on a laptop or a GPU server |
| **Responsibility**: important to a public-sector sponsor | Backup "Responsible by design" | robots.txt respected, no personal data, open model, every card sourced |
| **Presentation**: clear, on time | Whole pitch | 4 minutes, rehearsed, fallback video ready |

## Likely questions, with answers

Keep answers to ~20 seconds. Numbers in `[__]` come from the crawl and the spot-check.

**1. How is this different from F6S or e27?**
Directories list programs. We tell a founder which ones they can apply to and why, with warnings when they don't quite fit. We also follow listings back to the organiser's own page, and [__] programs we found aren't on any aggregator.

**2. How accurate is the extraction?**
We spot-checked [__] records against their source pages: [__]% of key fields were correct. Every card links to the organiser's page and shows when we verified it, so a founder can always check. Validation rules flag doubtful records instead of hiding them.

**3. What happens when a website changes?**
Nothing breaks. We never use CSS selectors; we read the page text and the model fills a fixed schema. We showed a restyled page still extracting.

**4. How do you keep listings fresh?**
Each source is re-crawled and we detect changes. Cards show a "verified on" date and a deadline countdown, and closed programs drop out. In the pilot, organisers claim and update their own listings.

**5. Why an open model? Isn't it slow?**
The challenge asked for open source, and it matters for a public body: no data leaves your servers and there's no per-call fee. Today it runs on a laptop CPU, which is why we pre-crawl. In a pilot it runs on a hosted GPU, and only one setting changes.

**6. Is crawling these sites allowed?**
We only read public program pages, identify ourselves honestly, and follow robots.txt. Four sites said no (e27, F6S, Thailand's NIA, SGInnovate), and we skip them. We never touch LinkedIn or personal profiles.

**7. What happens to an uploaded pitch deck?**
It's read in a temporary folder and deleted straight away. We keep the profile only in the founder's browser session; nothing is stored on our side.

**8. Why only programs? The brief says talent and partners too.**
Programs have deadlines and eligibility rules, which is where structured extraction adds the most, and they're what founders search for first. Aggregating institutions solves the cold start. People come later, and only opt-in.

**9. Doesn't the gap map just show where you didn't crawl?**
Partly, and we say so: it's labelled "coverage so far", with the sources named. That's still useful: it tells Startup ASEAN where to look next, and organisers in empty cells are the first people to invite.

**10. How would this scale to the whole region?**
Discovery already finds candidate pages from seeds; a curator approves them. The next step is 200+ sources, a review queue, and Postgres with embeddings for duplicate detection.

**11. What's the business model?**
[Decide before the pitch. Options: a public good funded by Startup ASEAN; featured listings for organisers; an API for policy teams.]

**12. What did you build today?**
[Be honest: what existed before the event and what was built today.]

## Before going on stage (additions to DEMO.md)

- [ ] **Remove sample data.** The database must hold only crawled programs, or the UI shows the "sample data" banner. Ask @reiva5 to reset it before the final crawl.
- [ ] **Remove the BRIN RISE record** (`ukmindonesia.id/…brin-rise-2026…`) so paste-a-URL shows a fresh result. It was ingested during UI testing.
- [ ] **Don't press Cancel during the paste-a-URL demo.** Cancel only stops the browser waiting; the server keeps going and saves the record anyway.
- [ ] **Share the deck** with @reiva5 from its Share menu (it's private).
- [ ] Browser zoom at 125% so the back row can read the cards; close other tabs.
- [ ] Open the UI at `http://localhost:5173` with the "Find programs" tab showing.
