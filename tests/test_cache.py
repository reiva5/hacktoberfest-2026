"""Cached demo runs must not fall back to the network or lose redirect identity."""
from datetime import datetime, timezone

import httpx
import pytest

from gateway import cli, config, fetch, llm, pipeline, store
from gateway.clean import clean


@pytest.fixture
def offline(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CACHE_DIR", tmp_path / "cache")
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "gateway.db")

    def forbidden(*args, **kwargs):
        pytest.fail("Offline replay attempted a network or model request")

    monkeypatch.setattr(httpx, "get", forbidden)
    monkeypatch.setattr(httpx, "post", forbidden)
    monkeypatch.setattr(llm, "chat_json", forbidden)
    return store.connect()


def test_cache_miss_is_an_explicit_error_without_network(offline):
    with pytest.raises(fetch.FetchError, match="cache miss"):
        fetch.fetch("https://example.org/missing", use_cache=True)


def test_cached_redirect_keeps_final_url_and_timestamp(offline):
    stamp = datetime(2026, 10, 31, tzinfo=timezone.utc)
    page = fetch.Page("https://example.org/old", "https://example.org/program", 200,
                      "<html><body>Sample programme</body></html>", stamp)
    fetch._save_page(page)
    cached = fetch.fetch(page.url, use_cache=True)
    assert cached.from_cache
    assert (cached.final_url, cached.status, cached.fetched_at) == (page.final_url, 200, stamp)
    assert cached.html == page.html


def test_legacy_html_cache_is_still_readable(offline):
    config.CACHE_DIR.mkdir()
    url = "https://example.org/program"
    fetch._cache_path(url).write_text("<p>Sample programme</p>", encoding="utf-8")
    cached = fetch.fetch(url, use_cache=True)
    assert cached.from_cache and cached.final_url == url


@pytest.mark.parametrize("metadata", ["{", "null", "[]", "{}",
                                    '{"final_url": "https://example.org/", "status": "200", "fetched_at": "invalid"}'])
def test_corrupt_metadata_is_reported_without_network(offline, metadata):
    url = "https://example.org/program"
    fetch._save_page(fetch.Page(url, url, 200, "<p>Sample</p>", datetime.now(timezone.utc)))
    fetch._cache_path(url).with_suffix(".json").write_text(metadata, encoding="utf-8")
    with pytest.raises(fetch.FetchError, match="cannot read cached page"):
        fetch.fetch(url, use_cache=True)


def test_crawl_replays_unchanged_cache_without_inference(offline, monkeypatch):
    import hashlib

    url = "https://example.org/old"
    final_url = "https://example.org/program"
    html = "<html><body><main><h1>Sample programme</h1><p>Sample support.</p></main></body></html>"
    fetch._save_page(fetch.Page(url, final_url, 200, html, datetime.now(timezone.utc)))
    digest = hashlib.sha256(clean(html, final_url).text.encode()).hexdigest()
    store.update_source(offline, url, last_hash=digest, last_count=1)
    monkeypatch.setattr(pipeline, "load_sources", lambda: [{"url": url, "kind": "program"}])
    assert cli.main(["crawl", "--cached"]) == 0
    assert store.get_source(offline, url)["status"] == "unchanged"


def test_cached_crawl_and_ingest_exit_nonzero_on_miss(offline, monkeypatch):
    url = "https://example.org/missing"
    monkeypatch.setattr(pipeline, "load_sources", lambda: [{"url": url}])
    assert cli.main(["crawl", "--cached"]) == 1
    assert cli.main(["ingest", url, "--cached"]) == 1
    assert store.get_source(offline, url)["status"] == "error"


def test_followed_error_is_not_reported_as_cli_success(offline, monkeypatch):
    result = pipeline.IngestResult("https://example.org/list", "ok", followed=[
        pipeline.IngestResult("https://example.org/program", "error", note="cache miss"),
    ])
    monkeypatch.setattr(pipeline, "crawl", lambda *args, **kwargs: [result])
    assert cli.main(["crawl", "--cached"]) == 1
