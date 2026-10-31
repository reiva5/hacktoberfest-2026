"""Data contracts shared by the pipeline, the API and the UI.

`ExtractedProgram` is what Gemma fills from a page. `Program` adds what the pipeline knows
(where it was seen, when it was verified, validation issues). `Profile` is a founder's startup.
"""
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

ProgramType = Literal["accelerator", "grant", "competition", "gov_scheme", "credits", "investment", "other"]
Stage = Literal["idea", "pre-seed", "seed", "series-a+"]
STAGES: list[str] = ["idea", "pre-seed", "seed", "series-a+"]

ASEAN = {
    "BN": "Brunei", "KH": "Cambodia", "ID": "Indonesia", "LA": "Laos", "MY": "Malaysia",
    "MM": "Myanmar", "PH": "Philippines", "SG": "Singapore", "TH": "Thailand", "VN": "Vietnam",
}
GLOBAL = "*"  # open to applicants from anywhere


class Funding(BaseModel):
    amount: float | None = Field(None, description="Largest amount on offer, as a number. null if not stated.")
    currency: str | None = Field(None, description="ISO 4217 code, e.g. MYR, SGD, USD.")
    equity_free: bool | None = Field(None, description="true if no equity is taken. null if unclear.")
    equity_pct: float | None = Field(None, description="Equity taken in percent, if stated.")


class ExtractedProgram(BaseModel):
    title: str
    organiser: str
    organiser_url: str | None = Field(None, description="Homepage of the organising body, if linked.")
    program_url: str | None = Field(None, description="Link to this program's own page or application page, if present in the text.")
    type: ProgramType = "other"
    countries: list[str] = Field(default_factory=list, description="Where applicants must be based. Country names or ISO codes; 'ASEAN' for region-wide; 'GLOBAL' if open worldwide.")
    sectors: list[str] = Field(default_factory=list, description="Target sectors in lowercase English. Empty if sector-agnostic.")
    stages: list[Stage] = Field(default_factory=list, description="Eligible startup stages. Empty if not stated.")
    funding: Funding = Field(default_factory=Funding)
    eligibility: list[str] = Field(default_factory=list, description="Each eligibility rule as a short English sentence.")
    deadline: date | None = Field(None, description="Application deadline as YYYY-MM-DD. null if rolling or not stated.")
    rolling: bool = Field(False, description="true if applications are accepted on a rolling basis.")
    summary: str = Field("", description="One or two English sentences on what the program offers.")


class PageExtraction(BaseModel):
    is_program_page: bool = Field(description="true if the page describes or lists startup programs, grants, accelerators, competitions or funding calls.")
    language: str = Field("en", description="ISO 639-1 code of the page's main language.")
    programs: list[ExtractedProgram] = Field(default_factory=list)


class Program(ExtractedProgram):
    id: str = ""
    canonical_url: str = ""
    source_url: str = ""
    seen_on: list[str] = Field(default_factory=list)
    language: str = "en"
    last_verified: datetime | None = None
    issues: list[str] = Field(default_factory=list)
    confidence: float = 1.0

    @property
    def is_open(self) -> bool:
        return self.rolling or self.deadline is None or self.deadline >= date.today()


class Profile(BaseModel):
    company: str | None = None
    country: str = Field(description="ISO 3166-1 alpha-2 code of the country of incorporation.")
    stage: Stage
    sectors: list[str] = Field(default_factory=list, description="Lowercase English sector names.")
    founder_nationalities: list[str] = Field(default_factory=list, description="ISO codes.")
    wants_equity_free: bool = False
    looking_for: list[ProgramType] = Field(default_factory=list)
    evidence: dict[str, int] = Field(default_factory=dict, description="Field name -> slide number it was read from.")


class Match(BaseModel):
    program: Program
    score: int
    reasons: list[str]
    warnings: list[str]
    days_left: int | None
