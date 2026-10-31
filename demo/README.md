# Demo inputs

Owner: @adhibskr. Everything here is fictional and safe to show on stage.

| File | What it is |
|---|---|
| `sample_deck.pdf` | 10-slide pitch deck for **Sample PadiSense**, a fictional Malaysian agritech startup. **The one used on stage** (DEMO.md step 3). |
| `sample_deck_ledgerlah.pdf` | Singapore seed-stage fintech raising equity. Tests `wants_equity_free = false`. |
| `sample_deck_belajarbareng.pdf` | Indonesian idea-stage edtech, written entirely in **Bahasa Indonesia**. Tests a non-English deck and the earliest stage. |
| `sample_deck_mekongcold.pdf` | Series A cold-chain company, **incorporated in Singapore, operating in Vietnam**. Design-heavy (big numbers, few words). Tests the country rule and slide images. |
| `sample_deck*.html` | Sources. Edit, then run `.venv/Scripts/python demo/build_deck.py` to rebuild every PDF. |

Try it: `python -m gateway deck demo/sample_deck.pdf` (needs Gemma). Run all four to tune the prompt in `gateway/deck.py`.

## Expected profiles (answer keys)

### Sample PadiSense (`sample_deck.pdf`)

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

### Sample LedgerLah (`sample_deck_ledgerlah.pdf`)

| Field | Expected | Slide(s) |
|---|---|---|
| country | `SG` (offices in VN too) | 6 |
| stage | `seed` | 4, 6 |
| sectors | `fintech`, `saas` | 1, 6 |
| founder_nationalities | `SG`, `VN` | 5 |
| wants_equity_free | **`false`** (raising equity) | 7 |
| looking_for | `investment`, `accelerator` | 7 |

### Sample BelajarBareng (`sample_deck_belajarbareng.pdf`, Bahasa Indonesia)

| Field | Expected | Slide(s) |
|---|---|---|
| country | `ID` (not yet incorporated; based in Semarang) | 6 |
| stage | **`idea`** ("belum ada produk") | 4, 6 |
| sectors | `edtech` | 1, 6 |
| founder_nationalities | `ID` | 5 |
| wants_equity_free | `true` ("tanpa ekuitas") | 7 |
| looking_for | `grant`, `competition`, `accelerator` (incubation) | 7 |

### Sample MekongCold (`sample_deck_mekongcold.pdf`)

| Field | Expected | Slide(s) |
|---|---|---|
| country | **`SG`** (holding company; operations in VN) | 5 |
| stage | `series-a+` | 6 |
| sectors | `logistics`, `climate` | 3 |
| founder_nationalities | `VN`, `TH` | 4 |
| wants_equity_free | `false` | 6 |
| looking_for | `investment` | 6 |

The hard cases are in bold. If the reader gets them wrong, fix the prompt, not the deck.
