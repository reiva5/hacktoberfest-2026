"""One record per real program, however many aggregators list it."""
import hashlib
import re
from difflib import SequenceMatcher

from .extract import domain, is_aggregator
from .schema import Program

_NOISE = re.compile(r"\b(19|20)\d{2}\b|\b(cohort|batch|intake|call for applications?|programme|program|applications? open)\b", re.I)


def _slug(s: str) -> str:
    s = _NOISE.sub(" ", s.lower())
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s).split())


def key(p: Program) -> str:
    return f"{_slug(p.organiser)}|{_slug(p.title)}"


def program_id(p: Program) -> str:
    return hashlib.sha1(key(p).encode()).hexdigest()[:12]


def same_program(a: Program, b: Program) -> bool:
    if a.canonical_url and a.canonical_url == b.canonical_url and _slug(a.title) == _slug(b.title):
        return True
    if key(a) == key(b):
        return True
    same_org = SequenceMatcher(None, _slug(a.organiser), _slug(b.organiser)).ratio() > 0.8 or (
        a.organiser_url and domain(a.organiser_url) == domain(b.organiser_url))
    return bool(same_org) and SequenceMatcher(None, _slug(a.title), _slug(b.title)).ratio() > 0.85


def merge(a: Program, b: Program) -> Program:
    """Keep the copy from the organiser's own site as the base, and fold the other into it."""
    # Prefer the copy read from the organiser's own site; on a tie, the newer one (b).
    rank = lambda p: (not is_aggregator(p.source_url), not is_aggregator(p.canonical_url))
    base, other = (b, a) if rank(b) >= rank(a) else (a, b)
    merged = base.model_copy(deep=True)
    merged.seen_on = sorted({*base.seen_on, *other.seen_on, other.source_url} - {merged.canonical_url, ""})
    merged.countries = sorted({*base.countries, *other.countries}) if "*" not in base.countries else ["*"]
    merged.sectors = sorted({*base.sectors, *other.sectors})
    merged.stages = [s for s in ("idea", "pre-seed", "seed", "series-a+") if s in {*base.stages, *other.stages}]
    if len(other.eligibility) > len(merged.eligibility):
        merged.eligibility = other.eligibility
    merged.deadline = merged.deadline or other.deadline
    merged.funding = merged.funding if merged.funding.amount is not None else other.funding
    merged.organiser_url = merged.organiser_url or other.organiser_url
    stamps = [t for t in (base.last_verified, other.last_verified) if t]
    merged.last_verified = max(stamps) if stamps else None
    merged.id = base.id or other.id or program_id(merged)
    return merged
