"""Find new program pages by following links out of pages we already crawl.

Cheap keyword filter first, then the small Gemma model decides. Approved candidates become sources.
"""
from pydantic import BaseModel

from . import config, llm
from .clean import CleanPage
from .extract import domain

KEYWORDS = (
    # English
    "accelerator", "incubator", "grant", "fund", "programme", "program", "cohort", "apply", "application",
    "competition", "challenge", "pitch", "startup", "founder", "credits", "call for",
    # Malay / Indonesian
    "geran", "dana", "hibah", "inkubator", "pendanaan", "permohonan", "pertandingan",
    # Vietnamese / Thai (common words in URLs and anchors)
    "chuong-trinh", "khoi-nghiep", "tai-tro", "สตาร์ทอัพ", "ทุน",
)
SKIP = ("login", "signin", "sign-in", "privacy", "terms", "cookie", "careers", "/jobs", "facebook.com",
        "twitter.com", "x.com/", "linkedin.com", "instagram.com", "youtube.com", "tiktok.com", ".pdf", ".jpg", ".png")


class PageCheck(BaseModel):
    is_program_page: bool
    reason: str


def candidate_links(page: CleanPage, base_url: str, limit: int = 40) -> list[tuple[str, str]]:
    base = domain(base_url)
    scored = []
    for url, anchor in page.links:
        low = (url + " " + anchor).lower()
        if not url.startswith("http") or any(s in low for s in SKIP):
            continue
        hits = sum(k in low for k in KEYWORDS)
        if hits:
            # Outbound links score higher: that's where new organisers live.
            scored.append((hits + (2 if domain(url) != base else 0), url, anchor))
    scored.sort(reverse=True)
    return [(u, a) for _, u, a in scored[:limit]]


def looks_like_program(page: CleanPage, url: str) -> PageCheck:
    user = f"URL: {url}\nTitle: {page.title}\n\n{page.text[:4000]}"
    return llm.chat_json(
        "Decide if this web page describes or lists startup programs a founder can apply to "
        "(accelerators, grants, competitions, government startup schemes, funding calls). "
        "News articles about programs do not count. Give a one-sentence reason.",
        user, PageCheck, model=config.LLM_SMALL_MODEL,
    )
