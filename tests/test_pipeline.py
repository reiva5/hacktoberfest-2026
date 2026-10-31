"""Offline tests: the model is replaced by a stub so these run without Gemma."""
from datetime import date, timedelta

import pytest

from gateway import config, extract, gapmap, llm, store, validate
from gateway.clean import clean
from gateway.match import match
from gateway.schema import ExtractedProgram, Funding, PageExtraction, Profile

TODAY = date.today()


@pytest.fixture
def db(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "test.db")
    return store.connect()


def _stub_llm(monkeypatch, result: PageExtraction):
    monkeypatch.setattr(llm, "chat_json", lambda *a, **k: result)


def _grant(**over) -> ExtractedProgram:
    base = dict(
        title="Pre-Seed Grant 2026", organiser="National Startup Agency", organiser_url="https://agency.gov.my/",
        program_url="https://agency.gov.my/grant", type="grant", countries=["Malaysia"], sectors=[],
        stages=["idea", "pre-seed"], funding=Funding(amount=150000, currency="MYR", equity_free=True),
        eligibility=["Company incorporated in Malaysia", "At least 51% Malaysian-owned"],
        deadline=TODAY + timedelta(days=12), summary="Equity-free grant for early-stage startups.",
    )
    return ExtractedProgram(**(base | over))


LAYOUT_A = """<html><head><title>Grants</title></head><body><nav>Home | About</nav>
<main><h1>Pre-Seed Grant 2026</h1><p>Equity-free funding of up to RM150,000 for Malaysian startups.</p>
<ul><li>Incorporated in Malaysia</li><li>Prototype stage</li></ul><p>Applications close 30 November 2026.</p></main>
<footer>© Agency</footer></body></html>"""

# Same content after a redesign: different tags, classes and nesting.
LAYOUT_B = """<html><head><title>Grants</title></head><body><div class="hdr-x9">Menu</div>
<section class="c-card__wrap"><div class="c-card__ttl"><h2>Pre-Seed Grant 2026</h2></div>
<div class="c-card__body"><span>Equity-free funding of up to RM150,000 for Malaysian startups.</span>
<table><tr><td>Incorporated in Malaysia</td></tr><tr><td>Prototype stage</td></tr></table>
<div>Applications close 30 November 2026.</div></div></section></body></html>"""


def test_cleaning_survives_a_redesign():
    for html in (LAYOUT_A, LAYOUT_B):
        text = clean(html, "https://agency.gov.my/grant").text
        for fact in ("Pre-Seed Grant 2026", "RM150,000", "Incorporated in Malaysia", "30 November 2026"):
            assert fact in text, f"{fact!r} lost from layout"


def test_countries_are_normalised():
    assert extract.normalise_countries(["Malaysia", "viet nam"]) == ["MY", "VN"]
    assert len(extract.normalise_countries(["ASEAN"])) == 10
    assert extract.normalise_countries(["Global", "Singapore"]) == ["*"]


def test_aggregator_listing_points_to_organiser(monkeypatch):
    _stub_llm(monkeypatch, PageExtraction(is_program_page=True, programs=[_grant(program_url=None)]))
    page = clean(LAYOUT_A, "https://e27.co/events/grant")
    [p] = extract.extract(page, "https://e27.co/events/grant")
    assert p.canonical_url == "https://agency.gov.my/"
    assert p.seen_on == ["https://e27.co/events/grant"]
    assert p.countries == ["MY"]


def test_tidy_removes_spilled_json():
    spilled = 'Equity-free accelerator for AI startups.  ”, “sector_details”: “artificial intelligence, ai”}, {'
    assert extract.tidy(spilled) == "Equity-free accelerator for AI startups."
    assert extract.tidy("A normal sentence, with a comma.") == "A normal sentence, with a comma."


def test_non_program_page_yields_nothing(monkeypatch):
    _stub_llm(monkeypatch, PageExtraction(is_program_page=False))
    assert extract.extract(clean(LAYOUT_A, "https://x.com/"), "https://news.example/") == []


def test_same_program_from_two_places_is_one_record(db, monkeypatch):
    _stub_llm(monkeypatch, PageExtraction(is_program_page=True, programs=[_grant()]))
    [own] = extract.extract(clean(LAYOUT_A, "https://agency.gov.my/grant"), "https://agency.gov.my/grant")
    _stub_llm(monkeypatch, PageExtraction(is_program_page=True, programs=[_grant(title="Pre-Seed Grant (2026 intake)", program_url="https://e27.co/x")]))
    [agg] = extract.extract(clean(LAYOUT_A, "https://e27.co/x"), "https://e27.co/x")

    store.upsert_program(db, validate.validate(agg))
    merged, was_new = store.upsert_program(db, validate.validate(own))
    assert not was_new
    assert len(store.all_programs(db)) == 1
    assert merged.canonical_url == "https://agency.gov.my/grant"
    assert "https://e27.co/x" in merged.seen_on


def test_authoritative_refresh_removes_stale_eligibility_and_terms(db):
    old = extract.Program(**_grant(countries=["ASEAN"], stages=["idea", "pre-seed", "seed"]).model_dump(),
                          canonical_url="https://agency.gov.my/grant", source_url="https://agency.gov.my/grant")
    old.sectors = ["fintech"]
    new = old.model_copy(deep=True)
    new.countries = ["MY"]
    new.stages = ["idea", "pre-seed"]
    new.sectors = []
    new.eligibility = ["Minimum one team member resides in Malaysia"]
    new.funding = Funding(amount=150000, currency="MYR")
    new.deadline = None
    store.upsert_program(db, old)
    merged, was_new = store.upsert_program(db, new)
    assert not was_new and len(store.all_programs(db)) == 1
    assert merged.countries == ["MY"] and merged.stages == ["idea", "pre-seed"]
    assert merged.sectors == []
    assert merged.eligibility == new.eligibility
    assert merged.funding.equity_free is None and merged.deadline is None


def test_aggregator_cannot_broaden_authoritative_eligibility(db):
    own = extract.Program(**_grant(countries=["MY"], stages=["pre-seed"]).model_dump(),
                          canonical_url="https://agency.gov.my/grant", source_url="https://agency.gov.my/grant")
    aggregator = own.model_copy(deep=True)
    aggregator.source_url = "https://e27.co/grant"
    aggregator.countries = ["*"]
    aggregator.stages = ["idea", "pre-seed", "seed", "series-a+"]
    aggregator.sectors = ["healthtech"]
    aggregator.eligibility = ["Open to everyone", "All stages", "No restrictions"]
    store.upsert_program(db, own)
    merged, was_new = store.upsert_program(db, aggregator)
    assert not was_new
    assert merged.countries == own.countries and merged.stages == own.stages
    assert merged.sectors == own.sectors
    assert merged.eligibility == own.eligibility and "https://e27.co/grant" in merged.seen_on


def test_validation_flags_past_deadlines():
    p = extract.Program(**_grant(deadline=TODAY - timedelta(days=3)).model_dump(), canonical_url="u")
    validate.validate(p)
    assert "deadline has passed" in p.issues and p.confidence < 1 and not p.is_open


def _programs():
    def mk(**o):
        data = {"canonical_url": "https://a/"} | _grant().model_dump() | o
        data["countries"] = extract.normalise_countries(data["countries"])
        return validate.validate(extract.Program(**data))

    return [
        mk(),  # MY grant, idea/pre-seed, equity-free
        mk(title="Seed Accelerator", organiser="VC Co", type="accelerator", countries=["SG", "MY"], stages=["seed"],
           funding=Funding(amount=100000, currency="USD", equity_free=False, equity_pct=7), canonical_url="https://vc/"),
        mk(title="Health Challenge", organiser="Hospital", type="competition", countries=["*"], sectors=["healthtech"], canonical_url="https://h/"),
        mk(title="Vietnam Fund", organiser="VN Agency", countries=["VN"], canonical_url="https://vn/"),
    ]


def test_match_filters_and_explains():
    profile = Profile(country="MY", stage="pre-seed", sectors=["fintech"], wants_equity_free=True)
    results = match(profile, _programs())
    titles = [m.program.title for m in results]
    assert titles[0] == "Pre-Seed Grant 2026"
    assert "Vietnam Fund" not in titles          # wrong country
    assert "Health Challenge" not in titles      # wrong sector
    top = results[0]
    assert "Equity-free" in top.reasons and any("12 days" in w for w in top.warnings)
    seed = next(m for m in results if m.program.title == "Seed Accelerator")
    assert any("7% equity" in w for w in seed.warnings)


def test_gap_map_and_pitch_numbers():
    ps = _programs()
    grid = gapmap.gap_map(ps)
    assert grid["MY"]["pre-seed"] >= 2
    assert grid["LA"]["idea"] == 1          # only the global health challenge reaches Laos
    assert grid["LA"]["series-a+"] == 0     # a real gap in this sample
    nums = gapmap.pitch_numbers(ps)
    assert nums["open_programs"] == 4 and nums["asean_countries_covered"] == 10
