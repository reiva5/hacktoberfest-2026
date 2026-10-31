"""Founder profile -> programs they can actually apply to, ranked, each with reasons."""
from datetime import date

from .schema import ASEAN, GLOBAL, STAGES, Match, Profile, Program


def _country_ok(p: Program, country: str) -> bool:
    return not p.countries or GLOBAL in p.countries or country in p.countries


def _stage_fit(p: Program, stage: str) -> str:
    """'exact', 'any' (not stated), 'near' (one step off), or 'no'."""
    if not p.stages:
        return "any"
    if stage in p.stages:
        return "exact"
    i = STAGES.index(stage)
    return "near" if any(abs(STAGES.index(s) - i) == 1 for s in p.stages) else "no"


def _sector_fit(p: Program, sectors: list[str]) -> str:
    if not p.sectors:
        return "any"
    wanted = {s.lower() for s in sectors}
    have = {s.lower() for s in p.sectors}
    if wanted & have or any(w in h or h in w for w in wanted for h in have):
        return "exact"
    return "no"


def match(profile: Profile, programs: list[Program], *, today: date | None = None, include_near: bool = True) -> list[Match]:
    today = today or date.today()
    results = []
    for p in programs:
        if not p.is_open or not _country_ok(p, profile.country):
            continue
        stage = _stage_fit(p, profile.stage)
        sector = _sector_fit(p, profile.sectors)
        if stage == "no" or sector == "no" or (stage == "near" and not include_near):
            continue
        if profile.looking_for and p.type not in profile.looking_for:
            continue

        score, reasons, warnings = 50, [], []
        country_name = ASEAN.get(profile.country, profile.country)
        if p.countries and GLOBAL not in p.countries and len(p.countries) < len(ASEAN):
            score += 10
            reasons.append(f"Open to startups in {country_name}")
        else:
            reasons.append("Open across the region" if p.countries else "No country restriction stated")

        if stage == "exact":
            score += 15
            reasons.append(f"Accepts {profile.stage} startups")
        elif stage == "near":
            score -= 10
            warnings.append(f"Prefers {', '.join(p.stages)} stage")
        else:
            warnings.append("Stage not stated; check the page")

        if sector == "exact":
            score += 10
            reasons.append(f"Targets {', '.join(p.sectors[:3])}")
        else:
            score += 4
            reasons.append("Open to any sector")

        if p.funding.equity_free:
            score += 10 if profile.wants_equity_free else 3
            reasons.append("Equity-free")
        elif profile.wants_equity_free and p.funding.equity_pct:
            score -= 15
            warnings.append(f"Takes {p.funding.equity_pct:g}% equity")

        days_left = (p.deadline - today).days if p.deadline else None
        if days_left is not None:
            score += 5 if days_left <= 30 else 0
            if days_left <= 14:
                warnings.append(f"Closes in {days_left} days")
        if p.confidence < 0.7:
            warnings.append("Some details could not be read; check the source")

        results.append(Match(program=p, score=max(0, min(100, score)), reasons=reasons, warnings=warnings, days_left=days_left))

    return sorted(results, key=lambda m: (-m.score, m.days_left if m.days_left is not None else 9999))
