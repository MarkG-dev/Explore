#!/usr/bin/env python3
"""Harvest top-legend decklists from the public deck sites.

Design note, because it matters for whether this still works in six months:
this scraper does NOT parse each site's DOM. Every Hearthstone deck site publishes
Blizzard **deckstrings** (the `AAEBA...` base64 blobs players paste into the game),
and a deckstring is self-describing — it decodes to an exact card list, hero class
and format with no HTML involved. So the strategy is:

    1. pull the page
    2. regex out every deckstring on it
    3. decode each one against the local card database
    4. scrape only the *soft* metadata (archetype title, legend rank) from nearby
       text, and treat it as optional

A site redesign breaks the titles; it does not break the decks. That is a
deliberate trade — the decklist is the valuable part.

I could not test these fetchers while building them: every one of these hosts
blocks the cloud environment the study was written in. They are written
defensively and log what they find, but expect to adjust the SOURCES list and the
title heuristics on first run. `--dump` prints what was matched so you can see
immediately whether a source is yielding.

Usage:
    python3 fetch_legend_decks.py --list-sources
    python3 fetch_legend_decks.py --source hearthstone-decks --pages 5 --dump
    python3 fetch_legend_decks.py --all
"""
import argparse
import re
import sys
import time

from common import fetch, write_out, decode_deckstring

# Deckstrings are base64 starting with AAEB (Standard/Wild constructed).
DECKSTRING_RE = re.compile(rb"AAEB[A-Za-z0-9+/=]{20,}")
TAG_RE = re.compile(rb"<[^>]+>")
LEGEND_RANK_RE = re.compile(r"#\s?(\d{1,4})\s*legend", re.I)

SOURCES = {
    "hearthstone-decks": {
        "name": "hearthstone-decks.net (Top 500 Legend builds)",
        "pages": ["https://hearthstone-decks.net/standard-decks/page/{n}/"],
        "start": 1,
        "note": "Publishes Top Legend builds, refreshed several times a week.",
    },
    "metastats": {
        "name": "metastats.net (best decks by rank)",
        "pages": ["https://metastats.net/decksbyrank/", "https://metastats.net/decks/"],
        "start": None,
        "note": "Deck lists broken out by ladder bracket, including Legend.",
    },
    "hearthstonetopdecks": {
        "name": "hearthstonetopdecks.com",
        "pages": ["https://www.hearthstonetopdecks.com/deck-category/type/standard/page/{n}/"],
        "start": 1,
        "note": "Long-running deck archive with dated posts.",
    },
    "icyveins": {
        "name": "icy-veins.com Hearthstone deck guides",
        "pages": ["https://www.icy-veins.com/hearthstone/decks"],
        "start": None,
        "note": "Curated guides; fewer decks, much more written reasoning.",
    },
}


def text_around(blob, pos, span=420):
    """Readable text near a match, for pulling a title / legend rank."""
    chunk = blob[max(0, pos - span): pos]
    chunk = TAG_RE.sub(b" ", chunk)
    s = chunk.decode("utf-8", "replace")
    return " ".join(s.split())[-260:]


def harvest_page(url, dump=False):
    blob = fetch(url)
    if not blob:
        return []
    found, seen = [], set()
    for m in DECKSTRING_RE.finditer(blob):
        code = m.group(0).decode()
        if code in seen:
            continue
        seen.add(code)
        ctx = text_around(blob, m.start())
        rank = None
        rm = LEGEND_RANK_RE.search(ctx)
        if rm:
            try:
                rank = int(rm.group(1))
            except ValueError:
                pass
        dec = decode_deckstring(code)
        rec = {
            "deckstring": code,
            "source_url": url,
            "context_text": ctx,
            "legend_rank": rank,
            "format": dec.get("format"),
            "cards": dec.get("cards") or [],
            "decode_error": dec.get("error"),
        }
        found.append(rec)
        if dump:
            print(f"    + {len(rec['cards']):>2} cards"
                  f"{'  #'+str(rank)+' legend' if rank else ''}  … {ctx[-90:]}",
                  file=sys.stderr)
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=sorted(SOURCES))
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--pages", type=int, default=3, help="paginated depth per source")
    ap.add_argument("--dump", action="store_true", help="print each decoded deck")
    ap.add_argument("--list-sources", action="store_true")
    a = ap.parse_args()

    if a.list_sources:
        for k, v in SOURCES.items():
            print(f"  {k:22s} {v['name']}\n  {'':22s} {v['note']}")
        return 0

    keys = sorted(SOURCES) if a.all else ([a.source] if a.source else [])
    if not keys:
        ap.error("pass --source NAME, --all, or --list-sources")

    all_decks, per_source = [], {}
    for k in keys:
        src = SOURCES[k]
        print(f"[{k}] {src['name']}", file=sys.stderr)
        urls = []
        for tpl in src["pages"]:
            if "{n}" in tpl and src["start"] is not None:
                urls += [tpl.format(n=i) for i in range(src["start"], src["start"] + a.pages)]
            else:
                urls.append(tpl)
        got = []
        for u in urls:
            d = harvest_page(u, dump=a.dump)
            print(f"  {u} -> {len(d)} decks", file=sys.stderr)
            for rec in d:
                rec["source"] = k
            got += d
        per_source[k] = len(got)
        all_decks += got

    ok = [d for d in all_decks if d["cards"]]
    ranked = [d for d in all_decks if d.get("legend_rank")]
    print(f"[total] {len(all_decks)} deckstrings, {len(ok)} decoded, "
          f"{len(ranked)} with a legend rank", file=sys.stderr)
    if not all_decks:
        print("[!] nothing found. Either the URLs 404'd, robots.txt disallowed them, "
              "or the sites no longer inline deckstrings. Re-run with --dump and "
              "check ingest/.cache/ for what actually came back.", file=sys.stderr)

    write_out("legend_decks_raw.json", {
        "fetched_utc": time.time(),
        "per_source_counts": per_source,
        "n_total": len(all_decks),
        "n_decoded": len(ok),
        "n_with_legend_rank": len(ranked),
        "note": "Decks are decoded from Blizzard deckstrings, so card lists are exact. "
                "legend_rank is scraped from surrounding page text and is best-effort. "
                "These sites curate what they publish, so this is a sample of decks "
                "editors chose to feature, not a random sample of the ladder.",
        "decks": all_decks,
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
