"""Pitch deck PDF -> founder Profile. Slides go to Gemma as images when LLM_VISION=1, otherwise as text."""
from pathlib import Path

from pypdf import PdfReader

from . import config, llm
from .extract import normalise_countries
from .schema import Profile

SYSTEM = """You read a startup's pitch deck and fill in a profile used to match it with accelerators, grants and funding programs in Southeast Asia.
Rules:
- Only use what the deck states or clearly shows. If unsure, leave a list empty or pick the most conservative stage.
- country: ISO 3166-1 alpha-2 code of where the company is incorporated or headquartered.
- stage: 'idea' (no product), 'pre-seed' (prototype or pilots, little revenue), 'seed' (paying customers, raising seed), 'series-a+' (raising Series A or later).
- sectors: short lowercase English names such as fintech, healthtech, agritech, edtech, climate, logistics, ecommerce, saas.
- wants_equity_free: true only if the deck says they prefer grants or non-dilutive funding.
- evidence: for each field you filled, the 1-based slide number where you found it."""

MAX_SLIDES = 20


def _slide_text(path: Path) -> str:
    reader = PdfReader(str(path))
    parts = []
    for i, page in enumerate(reader.pages[:MAX_SLIDES], start=1):
        parts.append(f"--- Slide {i} ---\n{(page.extract_text() or '').strip()}")
    return "\n\n".join(parts)


def _slide_images(path: Path) -> list[bytes]:
    try:
        import pymupdf
    except ImportError:
        return []
    doc = pymupdf.open(str(path))
    # ~100 dpi keeps slides readable without blowing up the context.
    return [page.get_pixmap(dpi=100).tobytes("png") for page in list(doc)[:MAX_SLIDES]]


def read_deck(path: str | Path) -> Profile:
    path = Path(path)
    text = _slide_text(path)
    images = _slide_images(path) if config.LLM_VISION else []
    user = "Here is the pitch deck. The extracted slide text is below"
    user += "; the slide images are attached in order.\n\n" if images else ".\n\n"
    profile = llm.chat_json(SYSTEM, user + text, Profile, images=images or None)
    codes = normalise_countries([profile.country])
    profile.country = codes[0] if codes else profile.country.upper()
    return profile
