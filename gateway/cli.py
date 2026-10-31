"""Command line for the pipeline. Run `python -m gateway --help`."""
import argparse
import json
import sys

from . import gapmap, pipeline, store
from .match import match
from .schema import Profile


def _print_result(r: pipeline.IngestResult, indent: str = "") -> None:
    extra = f" ({r.note})" if r.note else ""
    print(f"{indent}[{r.status}] {r.url}: {len(r.new)} new, {len(r.updated)} merged{extra}")
    for f in r.followed:
        _print_result(f, indent + "  -> ")


def _print_matches(profile: Profile, programs) -> None:
    results = match(profile, programs)
    print(f"\n{len(results)} programs for {profile.model_dump(exclude={'evidence'}, exclude_defaults=True)}\n")
    for m in results[:15]:
        p = m.program
        when = f"closes in {m.days_left} days" if m.days_left is not None else ("rolling" if p.rolling else "no deadline listed")
        print(f"  {m.score:>3}  {p.title}  ·  {p.organiser}  ·  {when}")
        print(f"       why: {'; '.join(m.reasons)}")
        if m.warnings:
            print(f"       note: {'; '.join(m.warnings)}")
        print(f"       source: {p.canonical_url}" + (f" (also on {len(p.seen_on)} other pages)" if p.seen_on else ""))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="gateway", description="Startup ASEAN gateway pipeline")
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("crawl", help="Crawl every source in sources.yaml")
    c.add_argument("--cached", action="store_true", help="Use cached HTML (offline demo)")
    c.add_argument("--force", action="store_true", help="Re-extract even if a page has not changed")
    c.add_argument("--only", help="Only sources whose URL contains this text, or of this kind")

    i = sub.add_parser("ingest", help="Fetch one URL and extract its programs (the paste-a-URL demo)")
    i.add_argument("url")
    i.add_argument("--cached", action="store_true")
    i.add_argument("--no-follow", action="store_true", help="Don't follow aggregator listings to organiser pages")

    d = sub.add_parser("discover", help="Queue candidate program links found on a page")
    d.add_argument("url")
    d.add_argument("--check", type=int, default=0, help="Ask the small model about the first N candidates")

    sub.add_parser("candidates", help="List the discovery queue")
    a = sub.add_parser("approve", help="Ingest a discovered candidate")
    a.add_argument("url")

    dk = sub.add_parser("deck", help="Read a pitch deck PDF into a profile, then show matches")
    dk.add_argument("pdf")

    m = sub.add_parser("match", help="Show matches for a profile given on the command line")
    m.add_argument("--country", required=True, help="ISO code, e.g. MY")
    m.add_argument("--stage", required=True, choices=["idea", "pre-seed", "seed", "series-a+"])
    m.add_argument("--sector", action="append", default=[])
    m.add_argument("--equity-free", action="store_true")

    g = sub.add_parser("gapmap", help="Open programs by country and stage")
    g.add_argument("--json", action="store_true")
    sub.add_parser("stats", help="The four numbers for the pitch")
    sub.add_parser("list", help="List stored programs")
    sub.add_parser("sources", help="Show source health")
    e = sub.add_parser("export", help="Write all programs as JSON for the UI")
    e.add_argument("--out", default="data/programs.json")
    s = sub.add_parser("serve", help="Run the HTTP API for the UI")
    s.add_argument("--port", type=int, default=8000)

    args = ap.parse_args(argv)
    # Windows consoles default to cp1252, which can't print Thai, Khmer or Vietnamese.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    db = store.connect()

    if args.cmd == "crawl":
        for r in pipeline.crawl(db, use_cache=args.cached, force=args.force, only=args.only):
            _print_result(r)
    elif args.cmd == "ingest":
        r = pipeline.ingest_url(db, args.url, use_cache=args.cached, force=True, follow=not args.no_follow)
        _print_result(r)
        for pid in r.new + r.updated:
            p = store.get_program(db, pid)
            print(json.dumps(json.loads(p.model_dump_json()), indent=2, ensure_ascii=False))
    elif args.cmd == "discover":
        for link, anchor, status in pipeline.discover_from(db, args.url, check=args.check):
            print(f"  [{status}] {link}  ({anchor})")
    elif args.cmd == "candidates":
        for r in db.execute("SELECT * FROM candidates ORDER BY status, created_at"):
            print(f"  [{r['status']}] {r['url']}  from {r['found_on']}")
    elif args.cmd == "approve":
        store.set_candidate(db, args.url, "approved")
        _print_result(pipeline.ingest_url(db, args.url, kind="discovered"))
    elif args.cmd == "deck":
        from .deck import read_deck
        profile = read_deck(args.pdf)
        print(json.dumps(profile.model_dump(), indent=2))
        _print_matches(profile, store.all_programs(db))
    elif args.cmd == "match":
        profile = Profile(country=args.country.upper(), stage=args.stage, sectors=args.sector, wants_equity_free=args.equity_free)
        _print_matches(profile, store.all_programs(db))
    elif args.cmd == "gapmap":
        grid = gapmap.gap_map(store.all_programs(db))
        print(json.dumps(grid, indent=2) if args.json else gapmap.render(grid))
        if not args.json:
            print("\nEmpty cells mean none found in the sources crawled so far.")
    elif args.cmd == "stats":
        for k, v in gapmap.pitch_numbers(store.all_programs(db)).items():
            print(f"  {k.replace('_', ' '):<26} {v}")
    elif args.cmd == "list":
        for p in store.all_programs(db):
            flag = "" if not p.issues else f"  [check: {'; '.join(p.issues)}]"
            print(f"  {p.id}  {p.deadline or '-':<10}  {p.title}  ·  {p.organiser}  ·  {','.join(p.countries)}{flag}")
    elif args.cmd == "sources":
        for r in db.execute("SELECT * FROM sources ORDER BY status"):
            print(f"  [{r['status']}] {r['url']}  programs={r['last_count']}  {r['note'] or ''}")
    elif args.cmd == "export":
        from pathlib import Path
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(store.export_json(db), encoding="utf-8")
        print(f"Wrote {args.out}")
    elif args.cmd == "serve":
        import uvicorn
        uvicorn.run("gateway.api:app", port=args.port, reload=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
