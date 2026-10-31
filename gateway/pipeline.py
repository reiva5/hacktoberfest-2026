"""Seeds -> fetch -> clean -> extract -> validate -> dedupe -> store."""
import hashlib
import sqlite3
from dataclasses import dataclass, field

import yaml

from . import config, discover, store
from .clean import clean
from .extract import extract, is_aggregator
from .fetch import FetchError, can_render, fetch, render
from .llm import LLMError
from .validate import source_looks_broken, validate

MAX_FOLLOW_PER_PAGE = 10
MIN_TEXT_CHARS = 500  # below this, assume the page needs JavaScript to show its content


@dataclass
class IngestResult:
    url: str
    status: str  # ok | unchanged | not_program | needs_review | error
    new: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    followed: list["IngestResult"] = field(default_factory=list)
    note: str = ""


def load_sources(path=None) -> list[dict]:
    with open(path or config.SOURCES_FILE, encoding="utf-8") as f:
        return yaml.safe_load(f)["sources"]


def ingest_url(db: sqlite3.Connection, url: str, *, use_cache: bool = False, force: bool = False,
               follow: bool = True, kind: str | None = None, country: str | None = None) -> IngestResult:
    try:
        page = fetch(url, use_cache=use_cache)
    except FetchError as e:
        store.update_source(db, url, status="error", note=str(e), last_fetched=store.now())
        return IngestResult(url, "error", note=str(e))

    cleaned = clean(page.html, page.final_url)
    if len(cleaned.text) < MIN_TEXT_CHARS and not page.from_cache and can_render():
        # Probably built with JavaScript: load it in a headless browser and try again.
        try:
            page = render(url)
            cleaned = clean(page.html, page.final_url)
        except FetchError:
            pass
    # Hash the cleaned text, not the HTML: tracking scripts and nonces change on every load.
    text_hash = hashlib.sha256(cleaned.text.encode()).hexdigest()
    prev = store.get_source(db, url)
    if prev and prev["last_hash"] == text_hash and not force:
        store.update_source(db, url, status="unchanged", last_fetched=store.now())
        return IngestResult(url, "unchanged")

    try:
        programs = extract(cleaned, page.final_url)
    except LLMError as e:
        store.update_source(db, url, status="error", note=str(e), last_fetched=store.now())
        return IngestResult(url, "error", note=str(e))

    result = IngestResult(url, "ok" if programs else "not_program")
    for p in programs:
        stored, was_new = store.upsert_program(db, validate(p))
        (result.new if was_new else result.updated).append(stored.id)

    before = prev["last_count"] if prev and prev["last_count"] else 0
    if source_looks_broken(len(programs), before):
        result.status = "needs_review"
        result.note = f"found {len(programs)} programs, previously {before}"
    store.update_source(db, url, kind=kind or (prev["kind"] if prev else None), country=country or (prev["country"] if prev else None),
                        last_hash=text_hash, last_fetched=store.now(), last_count=len(programs), status=result.status, note=result.note)

    # Aggregator listing: go to each organiser's own page so the canonical record comes from the source.
    if follow and is_aggregator(page.final_url):
        targets = {p.canonical_url for p in programs if p.canonical_url and not is_aggregator(p.canonical_url)}
        for target in list(targets)[:MAX_FOLLOW_PER_PAGE]:
            result.followed.append(ingest_url(db, target, use_cache=use_cache, follow=False, kind="followed"))
    return result


def crawl(db: sqlite3.Connection, *, use_cache: bool = False, force: bool = False, only: str | None = None) -> list[IngestResult]:
    results = []
    for s in load_sources():
        if only and only not in s["url"] and only != s.get("kind"):
            continue
        results.append(ingest_url(db, s["url"], use_cache=use_cache, force=force, kind=s.get("kind"), country=s.get("country")))
    return results


def discover_from(db: sqlite3.Connection, url: str, *, check: int = 0, use_cache: bool = False) -> list[tuple[str, str, str]]:
    """Queue promising links from `url`. With check > 0, ask the small model about the first `check` of them."""
    page = fetch(url, use_cache=use_cache)
    cleaned = clean(page.html, page.final_url)
    found = []
    for link, anchor in discover.candidate_links(cleaned, page.final_url):
        if store.add_candidate(db, link, url, anchor):
            found.append((link, anchor, "pending"))
    for i, (link, anchor, _) in enumerate(found[:check]):
        try:
            cand = fetch(link)
            verdict = discover.looks_like_program(clean(cand.html, cand.final_url), link)
        except (FetchError, LLMError):
            continue
        status = "program" if verdict.is_program_page else "not_program"
        store.set_candidate(db, link, status)
        found[i] = (link, anchor, status)
    return found
