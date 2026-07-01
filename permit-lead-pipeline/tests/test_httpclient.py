"""Retry/backoff behavior — mocked, no network, fast (backoff monkeypatched)."""
import httpx
import pytest

from permitlead import httpclient
from permitlead.scrape import build_scraper
from permitlead.scrape.ckan import CkanScraper
from permitlead.scrape.socrata import SocrataScraper


class _Resp:
    def __init__(self, status): self.status_code = status; self.request = None
    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("e", request=None, response=self)
    def json(self): return []


def test_retries_then_succeeds(monkeypatch):
    calls = {"n": 0}
    def fake_get(url, **kw):
        calls["n"] += 1
        return _Resp(503 if calls["n"] < 3 else 200)
    monkeypatch.setattr(httpx, "get", fake_get)
    monkeypatch.setattr(httpclient.time, "sleep", lambda *_: None)  # no real waits
    resp = httpclient.get("http://x", retries=5)
    assert resp.status_code == 200 and calls["n"] == 3


def test_non_retryable_fails_fast(monkeypatch):
    calls = {"n": 0}
    def fake_get(url, **kw):
        calls["n"] += 1
        return _Resp(403)
    monkeypatch.setattr(httpx, "get", fake_get)
    monkeypatch.setattr(httpclient.time, "sleep", lambda *_: None)
    with pytest.raises(httpx.HTTPStatusError):
        httpclient.get("http://x", retries=5)
    assert calls["n"] == 1  # 403 not retried


def test_registry_knows_api_scrapers():
    assert isinstance(build_scraper("s", {"kind": "socrata"}), SocrataScraper)
    assert isinstance(build_scraper("c", {"kind": "ckan"}), CkanScraper)
