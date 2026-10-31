"""Offline checks keep the seed list focused on programme pages."""
from urllib.parse import urlparse

from gateway.pipeline import load_sources
from gateway.schema import ASEAN


def test_seeds_have_unique_programme_urls_and_valid_metadata():
    sources = load_sources()
    assert sources
    urls = [source["url"] for source in sources]
    assert len(urls) == len(set(urls))
    for source in sources:
        url = urlparse(source["url"])
        assert url.scheme == "https" and url.netloc
        assert url.path.strip("/"), f"Generic homepage seed: {source['url']}"
        assert source["kind"] in {"portal", "program", "aggregator", "regional", "non-english"}
        assert source["country"] in set(ASEAN) | {"ASEAN", "GLOBAL"}


def test_seeds_preserve_demo_page_types_and_exclude_blocked_hosts():
    sources = load_sources()
    assert {source["kind"] for source in sources} == {
        "portal", "program", "aggregator", "regional", "non-english",
    }
    blocked = {"e27.co", "f6s.com", "dpa.techostartup.center", "ri.techostartup.center"}
    for source in sources:
        host = urlparse(source["url"]).hostname
        assert host
        assert not any(host == domain or host.endswith("." + domain) for domain in blocked)
