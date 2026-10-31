# Product brief

Visual roadmap: [`gateway-roadmap.html`](../gateway-roadmap.html). Open it in a browser.

## The question

Startup ASEAN asked: how can it be the **single gateway** for discovering opportunities, programs, funding, talent and partners?

## Our wedge

All five categories at once is three startups' worth of work. We start with **programs and funding calls**: accelerators, grants, competitions, government schemes and credit programs. They:

- are spread across hundreds of small government, corporate and VC sites;
- have deadlines and eligibility rules, which is where structured extraction adds real value;
- are what founders actually go looking for.

Directories such as F6S and e27 already exist. Our difference is **eligibility**: "you're a pre-seed fintech in Malaysia; here are the programs you can apply to, why, and when they close."

## Users

| User | What they get |
|---|---|
| **Founder** (primary in the demo) | Upload a pitch deck and get programs they qualify for, with reasons, deadlines and sources |
| **Startup ASEAN** (the sponsor) | A gap map: where in the region founders have nowhere to apply. Something they can't easily see today |
| Program organisers (next phase) | Claim and verify their listing |

## Phases

| | MVP (today) | Next phase (3-month pilot) | Later |
|---|---|---|---|
| Categories | Programs and funding calls | + funders and investors | Talent (opt-in), partners |
| Sources | 15–20 seeds, 5 page types | 200+, discovery plus a curator review queue | Organisers post directly |
| Experience | Deck upload → profile → matches; no login | Accounts, saved programs, deadline alerts | Application drafting help, tracking |
| Ecosystem | Gap map, country × stage | Trends over time, export for policy teams | Open data and an API |
| Infra | Gemma on a laptop (Ollama), SQLite | Gemma on a hosted GPU, Postgres + pgvector | Gemma fine-tuned on corrected extractions |

## Deliberately out of scope for the MVP

- **LinkedIn or talent scraping.** Against LinkedIn's terms, a PDPA risk, and a bad look for a public body.
- **Logins.** They add nothing for judges watching a 4-minute demo.
- **Partners.** Too vague to demo well.
- **Funder database.** Good open data on funders is hard to find.
- **Large-scale discovery claims.** We show it works on the seeds.

## Success measures for today

| Measure | Target |
|---|---|
| Structured program records | 30–50 |
| Key fields correct (spot check of 10) | ≥ 85% |
| Source page types handled | 5 (portal, single program, aggregator, regional, non-English) |
| Profile fields correct from a sample deck | ≥ 4 of 5 |
| Programs found that aren't on e27 or F6S | ≥ 5 |
| Extraction survives an HTML restyle | yes |

## Risks

- **CPU inference is slow.** Pre-crawl and cache everything; only paste-a-URL runs live, and we have a recorded fallback.
- **Gemma 4B misreads eligibility.** Use 12B for extraction where possible; spot-check records.
- **Stale listings lose trust.** Show "verified on" and the source on every card.
- **The gap map overstates gaps.** Label it "coverage so far" and name the sources checked.
- **A design-heavy deck is misread.** Show the slide each field came from and keep every field editable.

## Open questions

- Is Startup ASEAN judging, and what outcome do they want?
- How long is the demo slot, and when is the deadline?
- Can we get any GPU time for Gemma 12B or 27B?
