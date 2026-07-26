#!/usr/bin/env python3
"""Shared polite-fetch machinery for the local ingest scripts.

These scripts exist because the cloud environment this study was built in cannot
reach any Hearthstone meta site — they block datacenter IP ranges. From a normal
home connection they work fine. Nothing here defeats a block; it just fetches
public pages from a network that is allowed to see them.

Behaviour that is deliberate, not incidental:
  * robots.txt is checked once per host and honoured. If a path is disallowed the
    fetch is skipped and logged, not retried through some other route.
  * one request at a time per host, with a real delay between them (default 2s).
  * every response is cached to disk, so re-running a normaliser costs zero
    requests. Delete .cache/ to force a refresh.
  * an honest User-Agent with a contact placeholder. Put your own contact in it.
"""
import hashlib
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import urllib.robotparser

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache")
# Put a real contact address here. Sites are far more tolerant of a scraper that
# identifies itself and is reachable than of an anonymous one.
UA = ("HearthstoneMetaStudy/1.0 (research; longitudinal ranked-meta dataset; "
      "contact: you@example.com)")
DELAY_S = 2.0

_robots = {}
_last_hit = {}


def _robot_ok(url):
    parts = urllib.parse.urlsplit(url)
    host = f"{parts.scheme}://{parts.netloc}"
    if host not in _robots:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(host + "/robots.txt")
        try:
            rp.read()
        except Exception:
            # No reachable robots.txt: proceed, but stay slow and identified.
            rp = None
        _robots[host] = rp
    rp = _robots[host]
    if rp is None:
        return True
    return rp.can_fetch(UA, url)


def _cache_path(url):
    h = hashlib.sha256(url.encode()).hexdigest()[:24]
    return os.path.join(CACHE, h + ".bin")


def fetch(url, delay=DELAY_S, force=False, timeout=45):
    """Fetch a URL politely, with on-disk caching. Returns bytes, or None."""
    os.makedirs(CACHE, exist_ok=True)
    cp = _cache_path(url)
    if os.path.exists(cp) and not force:
        with open(cp, "rb") as f:
            return f.read()

    if not _robot_ok(url):
        print(f"  [robots] disallowed, skipping: {url}", file=sys.stderr)
        return None

    host = urllib.parse.urlsplit(url).netloc
    wait = delay - (time.time() - _last_hit.get(host, 0))
    if wait > 0:
        time.sleep(wait)

    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/json,application/xhtml+xml,*/*",
        "Accept-Language": "en-US,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read()
    except Exception as e:
        print(f"  [fetch] {type(e).__name__} on {url}: {e}", file=sys.stderr)
        _last_hit[host] = time.time()
        return None
    _last_hit[host] = time.time()
    with open(cp, "wb") as f:
        f.write(data)
    return data


def fetch_json(url, **kw):
    b = fetch(url, **kw)
    if not b:
        return None
    try:
        return json.loads(b)
    except Exception as e:
        print(f"  [json] parse failed for {url}: {e}", file=sys.stderr)
        return None


def write_out(name, obj, outdir=None):
    outdir = outdir or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "data", "ingested")
    os.makedirs(outdir, exist_ok=True)
    p = os.path.abspath(os.path.join(outdir, name))
    with open(p, "w") as f:
        json.dump(obj, f, indent=1)
    print(f"[out] {p}", file=sys.stderr)
    return p


def decode_deckstring(code):
    """Deckstring -> card names, if python-hearthstone is installed."""
    try:
        from hearthstone.deckstrings import Deck
        import sqlite3
        d = Deck.from_deckstring(code)
        db = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "..", "data", "cards.sqlite")
        names = []
        if os.path.exists(db):
            con = sqlite3.connect(db)
            for dbf, count in d.cards:
                row = con.execute("SELECT name FROM cards WHERE dbf_id=? LIMIT 1",
                                  (dbf,)).fetchone()
                names.extend([row[0] if row else f"dbf:{dbf}"] * count)
            con.close()
        return {"format": d.format.name if d.format else None,
                "heroes": d.heroes, "cards": names}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}
