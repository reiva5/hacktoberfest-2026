# Demo inputs

Owner: @adhibskr. Everything here is fictional and safe to show on stage.

| File | What it is |
|---|---|
| `sample_deck.pdf` | 10-slide pitch deck for **Sample PadiSense**, a fictional Malaysian agritech startup. Used for DEMO.md step 3. |
| `sample_deck.html` | Source for the deck. Edit it, then run `.venv/Scripts/python demo/build_deck.py`. |

Try it: `python -m gateway deck demo/sample_deck.pdf` (needs Gemma).

## Expected profile (answer key)

Target: at least 4 of the 5 core fields correct ([PRODUCT.md](../docs/PRODUCT.md)).

| Field | Expected | Slide(s) |
|---|---|---|
| country | `MY` | 8 (also 5, 7) |
| stage | `pre-seed` | 4, 8 |
| sectors | `agritech`, `ai`, `climate` (any two is fine) | 1, 8 |
| founder_nationalities | `MY`, `ID` | 7 |
| wants_equity_free | `true` | 9 |
| looking_for | `grant`, `accelerator`, `credits`, `gov_scheme` | 9 |
| company | `Sample PadiSense` | 1, 8 |

Programs it should plausibly match from the seed list: Cradle CIP Spark (MY, pre-seed, grant), Google for Startups Accelerator SEA (AI), AWS credits, ADB Ventures (climate/agri), Youth Co:Lab. Expect warnings on PH- or ID-only programs (country mismatch).
