"""Sanity checks on extracted records. Failures lower confidence and put the source in the review queue."""
from datetime import date

from .schema import Program


def validate(p: Program, *, today: date | None = None) -> Program:
    today = today or date.today()
    issues = []
    if len(p.title.strip()) < 4:
        issues.append("title missing or too short")
    if not p.organiser.strip():
        issues.append("organiser missing")
    if not p.countries:
        issues.append("no eligible countries found")
    if not p.stages:
        issues.append("no stages found")
    if p.deadline is None and not p.rolling:
        issues.append("no deadline and not marked rolling")
    if p.deadline and p.deadline < today:
        issues.append("deadline has passed")
    if p.deadline and (p.deadline - today).days > 730:
        issues.append("deadline more than two years away; check the year")
    if p.funding.equity_free and p.funding.equity_pct:
        issues.append("marked equity-free but lists an equity percentage")
    if not p.eligibility:
        issues.append("no eligibility rules extracted")

    p.issues = issues
    p.confidence = round(max(0.1, 1 - 0.15 * len(issues)), 2)
    return p


def source_looks_broken(programs_now: int, programs_before: int) -> bool:
    """A source that suddenly yields far fewer programs probably changed layout or blocked us."""
    return programs_before >= 3 and programs_now < programs_before / 2
