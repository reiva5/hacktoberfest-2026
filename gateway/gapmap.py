"""Open programs counted by ASEAN country and stage, plus the numbers for the pitch.

An empty cell means "none found in the sources crawled so far", not "none exist". Say so in the pitch.
"""
from datetime import date, timedelta

from .extract import is_aggregator
from .schema import ASEAN, GLOBAL, STAGES, Program


def gap_map(programs: list[Program]) -> dict[str, dict[str, int]]:
    grid = {c: {s: 0 for s in STAGES} for c in ASEAN}
    for p in programs:
        if not p.is_open:
            continue
        countries = list(ASEAN) if (not p.countries or GLOBAL in p.countries) else [c for c in p.countries if c in ASEAN]
        stages = p.stages or STAGES  # stage not stated: counts as open to all stages
        for c in countries:
            for s in stages:
                grid[c][s] += 1
    return grid


def render(grid: dict[str, dict[str, int]]) -> str:
    lines = [f"{'Country':<13}" + "".join(f"{s:>11}" for s in STAGES)]
    for code, row in grid.items():
        lines.append(f"{ASEAN[code]:<13}" + "".join(f"{(str(n) if n else '-- 0'):>11}" for n in row.values()))
    return "\n".join(lines)


def pitch_numbers(programs: list[Program], *, today: date | None = None) -> dict[str, int]:
    today = today or date.today()
    open_ = [p for p in programs if p.is_open]
    covered = {c for p in open_ for c in (ASEAN if not p.countries or GLOBAL in p.countries else p.countries) if c in ASEAN}
    return {
        "open_programs": len(open_),
        "closing_in_30_days": sum(1 for p in open_ if p.deadline and p.deadline <= today + timedelta(days=30)),
        "asean_countries_covered": len(covered),
        # Found on the organiser's own site and never seen on an aggregator.
        "not_on_aggregators": sum(1 for p in open_ if not is_aggregator(p.canonical_url) and not any(is_aggregator(u) for u in p.seen_on)),
    }
