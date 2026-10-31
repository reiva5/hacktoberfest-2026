"""Polite fetching: robots.txt, a per-host delay, and an on-disk cache so the demo runs offline."""
import hashlib
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx

from . import config

_robots: dict[str, RobotFileParser | None] = {}
_last_hit: dict[str, float] = {}


@dataclass
class Page:
    url: str
    final_url: str
    status: int
    html: str
    fetched_at: datetime
    from_cache: bool = False

    @property
    def content_hash(self) -> str:
        return hashlib.sha256(self.html.encode("utf-8", "ignore")).hexdigest()


class FetchError(RuntimeError):
    pass


def _cache_path(url: str):
    return config.CACHE_DIR / (hashlib.sha1(url.encode()).hexdigest() + ".html")


def allowed(url: str) -> bool:
    parts = urlparse(url)
    origin = f"{parts.scheme}://{parts.netloc}"
    if origin not in _robots:
        rp = RobotFileParser()
        try:
            r = httpx.get(origin + "/robots.txt", headers={"User-Agent": config.USER_AGENT}, timeout=10, follow_redirects=True)
            rp.parse(r.text.splitlines() if r.status_code == 200 else [])
            _robots[origin] = rp
        except httpx.HTTPError:
            _robots[origin] = None  # robots.txt unreachable: treat as allowed
    rp = _robots[origin]
    return rp is None or rp.can_fetch(config.USER_AGENT, url)


def _wait_for_host(host: str) -> None:
    gap = time.monotonic() - _last_hit.get(host, 0)
    if gap < config.CRAWL_DELAY:
        time.sleep(config.CRAWL_DELAY - gap)
    _last_hit[host] = time.monotonic()


def fetch(url: str, *, use_cache: bool = False) -> Page:
    cached = _cache_path(url)
    if use_cache and cached.exists():
        return Page(url, url, 200, cached.read_text(encoding="utf-8"),
                    datetime.fromtimestamp(cached.stat().st_mtime, timezone.utc), from_cache=True)

    if not allowed(url):
        raise FetchError(f"robots.txt disallows {url}")
    _wait_for_host(urlparse(url).netloc)
    try:
        r = httpx.get(url, headers={"User-Agent": config.USER_AGENT, "Accept-Language": "en;q=1, *;q=0.5"},
                      timeout=30, follow_redirects=True)
    except httpx.HTTPError as e:
        raise FetchError(f"{url}: {e}") from e
    if r.status_code >= 400:
        raise FetchError(f"{url}: HTTP {r.status_code}")

    config.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cached.write_text(r.text, encoding="utf-8")
    return Page(url, str(r.url), r.status_code, r.text, datetime.now(timezone.utc))


def can_render() -> bool:
    try:
        import playwright  # noqa: F401
        return True
    except ImportError:
        return False


def render(url: str) -> Page:
    """Load the page in headless Chromium for sites that build their content with JavaScript."""
    from playwright.sync_api import Error as PlaywrightError, sync_playwright

    if not allowed(url):
        raise FetchError(f"robots.txt disallows {url}")
    _wait_for_host(urlparse(url).netloc)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page(user_agent=config.USER_AGENT)
            resp = page.goto(url, wait_until="networkidle", timeout=45000)
            html, final_url = page.content(), page.url
            status = resp.status if resp else 200
            browser.close()
    except PlaywrightError as e:
        raise FetchError(f"{url}: render failed: {e}") from e
    if status >= 400:
        raise FetchError(f"{url}: HTTP {status}")
    config.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    _cache_path(url).write_text(html, encoding="utf-8")
    return Page(url, final_url, status, html, datetime.now(timezone.utc))
