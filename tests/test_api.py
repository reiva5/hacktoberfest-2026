"""API smoke test against a temporary database, no model needed."""
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from gateway import config, store, validate
from gateway.schema import Funding, Program


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "api.db")
    db = store.connect()
    store.upsert_program(db, validate.validate(Program(
        title="Pre-Seed Grant", organiser="Agency", type="grant", countries=["MY"], stages=["pre-seed"],
        funding=Funding(equity_free=True), eligibility=["Malaysian company"],
        deadline=date.today() + timedelta(days=20), canonical_url="https://agency.gov.my/grant",
    )))
    from gateway.api import app
    return TestClient(app)


def test_api_endpoints(client):
    assert len(client.get("/programs").json()) == 1
    matches = client.post("/match", json={"country": "MY", "stage": "pre-seed", "wants_equity_free": True}).json()
    assert matches[0]["program"]["title"] == "Pre-Seed Grant" and "Equity-free" in matches[0]["reasons"]
    assert client.post("/match", json={"country": "VN", "stage": "pre-seed"}).json() == []
    assert client.get("/gapmap").json()["MY"]["pre-seed"] == 1
    assert client.get("/stats").json()["open_programs"] == 1
