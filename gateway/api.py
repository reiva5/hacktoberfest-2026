"""HTTP API for the UI. Run with `python -m gateway serve`, then open http://localhost:8000/docs."""
import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import gapmap, pipeline, store
from .llm import LLMError
from .match import match
from .schema import Match, Profile, Program

app = FastAPI(title="Startup ASEAN Gateway")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class IngestRequest(BaseModel):
    url: str


@app.get("/programs", response_model=list[Program])
def programs(open_only: bool = True):
    ps = store.all_programs(store.connect())
    return [p for p in ps if p.is_open] if open_only else ps


@app.get("/programs/{pid}", response_model=Program)
def program(pid: str):
    p = store.get_program(store.connect(), pid)
    if not p:
        raise HTTPException(404, "No program with that id")
    return p


@app.post("/match", response_model=list[Match])
def match_profile(profile: Profile):
    return match(profile, store.all_programs(store.connect()))


@app.post("/deck")
async def deck(file: UploadFile):
    from .deck import read_deck
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "deck.pdf"
        path.write_bytes(await file.read())
        try:
            profile = read_deck(path)
        except LLMError as e:
            raise HTTPException(502, f"Could not read the deck: {e}")
    return {"profile": profile, "matches": match(profile, store.all_programs(store.connect()))}


@app.post("/ingest")
def ingest(req: IngestRequest):
    db = store.connect()
    r = pipeline.ingest_url(db, req.url, force=True)
    ids = r.new + r.updated + [i for f in r.followed for i in f.new + f.updated]
    return {"status": r.status, "note": r.note, "programs": [store.get_program(db, i) for i in ids]}


@app.get("/gapmap")
def gap():
    return gapmap.gap_map(store.all_programs(store.connect()))


@app.get("/stats")
def stats():
    return gapmap.pitch_numbers(store.all_programs(store.connect()))
