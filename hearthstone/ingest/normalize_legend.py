#!/usr/bin/env python3
"""Fold ingested top-legend sources into one file the website reads.

Inputs (whatever exists in ../data/ingested/):
    legend_decks_raw.json        from fetch_legend_decks.py
    reddit_competitivehs.json    from fetch_reddit_competitivehs.py

Output:
    ../data/ingested/legend_decks.json

The site loads that file if present and renders a Top-Legend section; if it is
absent the site simply does not show the section, so this is safe to run partially.

Archetype naming is the messy part. Deck sites label the same deck a dozen ways, so
rather than trust the scraped title we infer a class from the decoded card list
(authoritative) and keep the scraped title only as a display label.
"""
import json
import os
import re
import sqlite3
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ING = os.path.join(HERE, "..", "data", "ingested")
CARDS_DB = os.path.join(HERE, "..", "data", "cards.sqlite")

NOISE = re.compile(r"(copy|deck code|import|share|guide|update[d]?|\bby\b|\d{4}-\d{2}-\d{2})", re.I)


def load(name):
    p = os.path.join(ING, name)
    if not os.path.exists(p):
        print(f"[skip] {name} not present", file=sys.stderr)
        return None
    with open(p) as f:
        return json.load(f)


def class_of(cards, con):
    """Infer the deck's class from its cards: the non-neutral class that dominates."""
    if not cards or not con:
        return None
    counts = Counter()
    for nm in set(cards):
        row = con.execute(
            "SELECT card_class FROM cards WHERE name=? AND card_class<>'NEUTRAL' LIMIT 1",
            (nm,)).fetchone()
        if row:
            counts[row[0]] += 1
    return counts.most_common(1)[0][0] if counts else "NEUTRAL"


def clean_title(ctx):
    """Best-effort archetype label from the text preceding a deckstring."""
    if not ctx:
        return None
    parts = [p.strip() for p in re.split(r"[|•–—\-–—]{1,2}|\s{3,}", ctx) if p.strip()]
    cands = [p for p in reversed(parts)
             if 3 <= len(p) <= 46 and not NOISE.search(p) and not p.isdigit()]
    return cands[0] if cands else None


def main():
    con = sqlite3.connect(CARDS_DB) if os.path.exists(CARDS_DB) else None
    if not con:
        print("[warn] cards.sqlite missing; class inference disabled", file=sys.stderr)

    raw = load("legend_decks_raw.json")
    reddit = load("reddit_competitivehs.json")
    if not raw and not reddit:
        print("[!] nothing to normalise. Run the fetchers first.", file=sys.stderr)
        return 1

    decks, by_class, by_source, dedupe = [], Counter(), Counter(), {}
    for d in ((raw or {}).get("decks") or []):
        cards = d.get("cards") or []
        if not cards:
            continue
        key = d.get("deckstring")
        if key in dedupe:          # same list republished across pages
            continue
        dedupe[key] = True
        cls = class_of(cards, con)
        rec = {
            "deckstring": key,
            "label": clean_title(d.get("context_text")),
            "class": cls,
            "format": d.get("format"),
            "legend_rank": d.get("legend_rank"),
            "n_cards": len(cards),
            "cards": cards,
            "source": d.get("source"),
            "source_url": d.get("source_url"),
        }
        decks.append(rec)
        by_class[cls] += 1
        by_source[d.get("source")] += 1

    ranked = [d for d in decks if d.get("legend_rank")]
    ranked.sort(key=lambda d: d["legend_rank"])

    writeups = []
    for p in ((reddit or {}).get("posts") or []):
        if not p.get("meta_relevant"):
            continue
        writeups.append({
            "title": p.get("title"), "flair": p.get("flair"), "score": p.get("score"),
            "author": p.get("author"), "permalink": p.get("permalink"),
            "created_utc": p.get("created_utc"),
            "excerpt": (p.get("selftext") or "")[:1500],
            "n_comments": p.get("num_comments"),
        })
    writeups.sort(key=lambda w: -(w["score"] or 0))

    out = {
        "note": "Top-legend deck choice, ingested locally. Card lists are exact "
                "(decoded from Blizzard deckstrings); class is inferred from the cards. "
                "legend_rank is scraped page text and is best-effort.",
        "limits": [
            "Deck sites publish what their editors feature -- a curated sample, not a "
            "random sample of the ladder.",
            "A '#12 Legend' tag means one player reached that rank with that list. It "
            "is not a winrate and does not generalise.",
            "Reddit writeups are strong evidence of reasoning and weak evidence of "
            "frequency. Treat them as expert testimony, not measurement.",
        ],
        "n_decks": len(decks),
        "n_with_legend_rank": len(ranked),
        "by_class": dict(by_class.most_common()),
        "by_source": dict(by_source.most_common()),
        "decks": decks,
        "top_ranked_decks": ranked[:120],
        "writeups": writeups[:200],
    }
    p = os.path.join(ING, "legend_decks.json")
    os.makedirs(ING, exist_ok=True)
    with open(p, "w") as f:
        json.dump(out, f, indent=1)

    print(f"[ok] {len(decks)} decks ({len(ranked)} rank-tagged), "
          f"{len(writeups)} writeups -> {os.path.abspath(p)}", file=sys.stderr)
    if by_class:
        print("     classes: " + ", ".join(f"{k} {v}" for k, v in by_class.most_common()),
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
