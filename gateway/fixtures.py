"""Fictional sample programs, so the web UI can be built and demoed before Gemma is running.

Deadlines are stored as days from today so the sample never goes stale.
"""
import json
import sqlite3
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from . import store
from .schema import Program
from .validate import validate


def load_sample(db: sqlite3.Connection, path: Path) -> int:
    rows = json.loads(path.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc)
    for row in rows:
        days = row.pop("deadline_in_days", None)
        row["deadline"] = (date.today() + timedelta(days=days)).isoformat() if days is not None else None
        p = Program(**row, source_url=row["canonical_url"], last_verified=now)
        store.upsert_program(db, validate(p))
    return len(rows)
