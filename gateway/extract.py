"""Page text -> structured program records, using Gemma."""
import re
from datetime import date, datetime, timezone
from urllib.parse import urljoin, urlparse

from . import config, llm
from .clean import CleanPage
from .schema import ASEAN, GLOBAL, PageExtraction, Program

SYSTEM = """You extract startup support programs from web pages for a directory used by founders in Southeast Asia (ASEAN).
A program is anything a startup can apply to: accelerators, incubators, grants, government schemes, competitions, pitch events with prizes, cloud credit programs, or investment calls.
Rules:
- Only use facts stated on the page. Never guess amounts, dates or eligibility.
- Write every text field in English, translating if the page is in another language.
- If the page lists several programs, return each one separately (at most 25).
- Perks inside a program (cloud credits, mentorship, demo day) are part of that program, not separate programs.
- Do not turn navigation links, conferences, surveys, training for students, or benefits of a program into separate startup funding opportunities.
- If the page is a news article, blog post, or general homepage with no program details, set is_program_page to false and return no programs.
- countries: where applicants must be based. Use 'ASEAN' if open across Southeast Asia and 'GLOBAL' if open worldwide.
- Never infer eligible countries from this directory's ASEAN focus, the organiser's location, or the page URL. A Malaysian residence requirement means Malaysia, not all ASEAN countries. Leave countries empty if no applicant location is stated.
- stages: use only stages stated or clearly described: ideation = idea, pre-seed = pre-seed, seed = seed, Series A/B and later = series-a+. Do not add seed just because a program supports early-stage entrepreneurs.
- funding: distinguish the grant or investment cap from project cost, revenue limits, paid-up capital, perks and later follow-on investment. Never infer equity-free from the word 'grant', 'free participation', or revenue sharing. A conditional share-subscription right is not a fixed equity percentage.
- deadline: only the application closing date as YYYY-MM-DD, never event, bootcamp or graduation dates. Resolve relative dates using today's date and an explicit cohort year where supplied. If the exact date or year cannot be established, leave deadline null and describe the published period in eligibility. Never invent a day for a month-only closing period or move a past cohort into the future.
- rolling: true only if ongoing or rolling applications are explicitly stated, not merely because no deadline is listed.
- program_url: copy an observed link to this specific program's own detail page; prefer it over a shared application portal. If no detail link is supplied, use the Page URL. Never construct a URL from the title.
- Keep conditional funding, residency, incorporation and published application-period restrictions in eligibility even when a structured field cannot express them."""

_COUNTRY_ALIASES = {name.lower(): code for code, name in ASEAN.items()} | {
    "viet nam": "VN", "lao pdr": "LA", "burma": "MM", "brunei darussalam": "BN",
    "global": GLOBAL, "worldwide": GLOBAL, "international": GLOBAL, "any": GLOBAL,
}
_REGION = {"asean", "southeast asia", "south east asia", "sea"}


def normalise_countries(raw: list[str]) -> list[str]:
    out: set[str] = set()
    for c in raw:
        key = c.strip().lower()
        if key in _REGION:
            out.update(ASEAN)
        elif key.upper() in ASEAN:
            out.add(key.upper())
        elif key in _COUNTRY_ALIASES:
            out.add(_COUNTRY_ALIASES[key])
        elif len(key) == 2:
            out.add(key.upper())  # non-ASEAN ISO code, keep as-is
    if GLOBAL in out:
        return [GLOBAL]
    return sorted(out)


# Small models sometimes run on past the end of a string and spill JSON into it: `text", "key": ...`
_JSON_SPILL = re.compile(r"""\s*["”]\s*,\s*["“][\w ]+["”]\s*:.*$|\s*["”]?\s*[}\]]\s*,?\s*[{\[].*$""", re.S)


def tidy(text: str) -> str:
    return _JSON_SPILL.sub("", text).strip().rstrip(",;")


def domain(url: str | None) -> str:
    host = urlparse(url or "").netloc.lower()
    return host[4:] if host.startswith("www.") else host


def is_aggregator(url: str) -> bool:
    d = domain(url)
    return any(d == a or d.endswith("." + a) for a in config.AGGREGATOR_DOMAINS)


def extract(page: CleanPage, url: str, *, today: date | None = None) -> list[Program]:
    today = today or date.today()
    links = "\n".join(f"{anchor}: {link}" for link, anchor in page.links)
    user = f"Today's date: {today.isoformat()}\nPage URL: {url}\nPage title: {page.title}\n\nPage content (markdown):\n{page.text}\n\nObserved page links (navigation is not evidence of a program):\n{links}"
    result = llm.chat_json(SYSTEM, user, PageExtraction)
    if not result.is_program_page:
        return []

    now = datetime.now(timezone.utc)
    programs = []
    for p in result.programs:
        program_url = urljoin(url, p.program_url) if p.program_url else None
        organiser_url = urljoin(url, p.organiser_url) if p.organiser_url else None
        # Canonical = the organiser's own page when we can find it, never the aggregator's copy.
        canonical = program_url or url
        if is_aggregator(canonical) and organiser_url and not is_aggregator(organiser_url):
            canonical = organiser_url
        p.summary = tidy(p.summary)
        p.eligibility = [tidy(e) for e in p.eligibility if tidy(e)]
        p.sectors = sorted({s.strip().lower() for s in p.sectors if s.strip()})
        programs.append(Program(
            **p.model_dump(exclude={"program_url", "organiser_url", "countries"}),
            program_url=program_url,
            organiser_url=organiser_url,
            countries=normalise_countries(p.countries),
            canonical_url=canonical,
            source_url=url,
            seen_on=[url] if url != canonical else [],
            language=result.language,
            last_verified=now,
        ))
    return programs
