@AGENTS.md

## Claude Code specifics

- Windows machine. Use the venv directly: `.venv/Scripts/python -m pytest -q`, `.venv/Scripts/python -m gateway …`.
- The human driving Claude (@adhibskr) is the product lead and owns business, ops, the pitch and the web UI (`web/`). Think like a product person: challenge scope, propose cuts, and keep the 4-minute demo in mind.
- @reiva5 owns the system (`gateway/`, `sources.yaml`, `tests/`) with Copilot. Don't edit their area; open an issue instead. Before touching contract files (`gateway/schema.py`, `gateway/api.py`), check their open PRs with `gh pr list --author reiva5` to avoid conflicts.
- When a decision is made in conversation, add it to `docs/DECISIONS.md` in the same PR.
- Keep `docs/BACKLOG.md` in sync when a task is finished or a new one appears.
