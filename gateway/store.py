"""SQLite storage. Programs are stored as JSON with a few columns pulled out for querying."""
import json
import sqlite3
from datetime import datetime, timezone

from . import config, dedupe
from .schema import Program

SCHEMA = """
CREATE TABLE IF NOT EXISTS programs (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    organiser TEXT NOT NULL,
    canonical_url TEXT,
    deadline TEXT,
    data TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sources (
    url TEXT PRIMARY KEY,
    kind TEXT,
    country TEXT,
    last_hash TEXT,
    last_fetched TEXT,
    last_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'new',   -- new | ok | unchanged | needs_review | error
    note TEXT
);
CREATE TABLE IF NOT EXISTS candidates (
    url TEXT PRIMARY KEY,
    found_on TEXT,
    anchor TEXT,
    status TEXT DEFAULT 'pending',  -- pending | program | not_program | approved | rejected
    created_at TEXT
);
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect() -> sqlite3.Connection:
    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(config.DB_PATH)
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    return db


def all_programs(db: sqlite3.Connection) -> list[Program]:
    return [Program.model_validate_json(r["data"]) for r in db.execute("SELECT data FROM programs ORDER BY deadline IS NULL, deadline")]


def get_program(db: sqlite3.Connection, pid: str) -> Program | None:
    row = db.execute("SELECT data FROM programs WHERE id = ?", (pid,)).fetchone()
    return Program.model_validate_json(row["data"]) if row else None


def _write(db: sqlite3.Connection, p: Program) -> None:
    db.execute(
        "INSERT OR REPLACE INTO programs (id, title, organiser, canonical_url, deadline, data, updated_at) VALUES (?,?,?,?,?,?,?)",
        (p.id, p.title, p.organiser, p.canonical_url, p.deadline.isoformat() if p.deadline else None, p.model_dump_json(), now()),
    )


def upsert_program(db: sqlite3.Connection, p: Program) -> tuple[Program, bool]:
    """Insert, or merge into an existing record for the same program. Returns (stored record, was_new)."""
    for existing in all_programs(db):
        if dedupe.same_program(existing, p):
            merged = dedupe.merge(existing, p)
            merged.id = existing.id
            _write(db, merged)
            db.commit()
            return merged, False
    p.id = dedupe.program_id(p)
    _write(db, p)
    db.commit()
    return p, True


def update_source(db: sqlite3.Connection, url: str, **fields) -> None:
    db.execute("INSERT OR IGNORE INTO sources (url) VALUES (?)", (url,))
    if fields:
        cols = ", ".join(f"{k} = ?" for k in fields)
        db.execute(f"UPDATE sources SET {cols} WHERE url = ?", (*fields.values(), url))
    db.commit()


def get_source(db: sqlite3.Connection, url: str) -> sqlite3.Row | None:
    return db.execute("SELECT * FROM sources WHERE url = ?", (url,)).fetchone()


def add_candidate(db: sqlite3.Connection, url: str, found_on: str, anchor: str) -> bool:
    cur = db.execute("INSERT OR IGNORE INTO candidates (url, found_on, anchor, created_at) VALUES (?,?,?,?)", (url, found_on, anchor, now()))
    db.commit()
    return cur.rowcount > 0


def set_candidate(db: sqlite3.Connection, url: str, status: str) -> None:
    db.execute("UPDATE candidates SET status = ? WHERE url = ?", (status, url))
    db.commit()


def export_json(db: sqlite3.Connection) -> str:
    return json.dumps([json.loads(p.model_dump_json()) for p in all_programs(db)], indent=2, ensure_ascii=False)
