"""Page text -> structured program records, using Gemma."""
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
- If the page is a news article, blog post, or general homepage with no program details, set is_program_page to false and return no programs.
- countries: where applicants must be based. Use 'ASEAN' if open across Southeast Asia and 'GLOBAL' if open worldwide.
- deadline: the application closing date as YYYY-MM-DD. Resolve relative dates using today's date. If the year is missing, assume the next occurrence.
- program_url: copy the link to the program's own page or application form if it appears in the text."""

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


def domain(url: str | None) -> str:
    host = urlparse(url or "").netloc.lower()
    return host[4:] if host.startswith("www.") else host


def is_aggregator(url: str) -> bool:
    d = domain(url)
    return any(d == a or d.endswith("." + a) for a in config.AGGREGATOR_DOMAINS)


def extract(page: CleanPage, url: str, *, today: date | None = None) -> list[Program]:
    today = today or date.today()
    user = f"Today's date: {today.isoformat()}\nPage URL: {url}\nPage title: {page.title}\n\nPage content (markdown):\n{page.text}"
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
