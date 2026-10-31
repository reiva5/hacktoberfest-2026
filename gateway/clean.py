"""Turn raw HTML into compact markdown for the model, plus the page's links for discovery.

No CSS selectors anywhere: trafilatura finds the main content, so a redesign doesn't break us.
"""
from dataclasses import dataclass
from urllib.parse import urljoin, urldefrag

import trafilatura
from lxml import html as lxml_html

from . import config


@dataclass
class CleanPage:
    text: str
    title: str
    links: list[tuple[str, str]]  # (absolute url, anchor text)


def clean(html: str, base_url: str) -> CleanPage:
    text = trafilatura.extract(
        html, url=base_url, output_format="markdown", include_links=True,
        include_tables=True, favor_recall=True,
    ) or ""
    title = ""
    links: list[tuple[str, str]] = []
    try:
        tree = lxml_html.fromstring(html)
        title = (tree.findtext(".//title") or "").strip()
        seen = set()
        for a in tree.iter("a"):
            href = a.get("href")
            if not href or href.startswith(("mailto:", "tel:", "javascript:", "#")):
                continue
            absolute = urldefrag(urljoin(base_url, href)).url
            if absolute in seen:
                continue
            seen.add(absolute)
            links.append((absolute, " ".join(a.text_content().split())[:120]))
    except (ValueError, lxml_html.etree.ParserError):
        pass

    if not text:
        # Listing pages built from cards sometimes defeat main-content detection; fall back to all visible text.
        text = trafilatura.html2txt(html) or ""
    return CleanPage(text=text[: config.MAX_PAGE_CHARS], title=title, links=links)
