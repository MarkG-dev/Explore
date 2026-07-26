#!/usr/bin/env python3
"""Pull r/CompetitiveHS meta threads — the best written record of top-legend deck choice.

Why this source matters more than a tier list: r/CompetitiveHS is where high-legend
players write up *why* they picked a deck, what they teched, and what the climb
actually felt like. Tier lists give you rankings; this gives you reasoning.

Reddit's public JSON needs no key — append .json to any listing or thread URL. It is
unreachable from the study's cloud environment but fine from a home connection.

Usage:
    python3 fetch_reddit_competitivehs.py                 # default sweep
    python3 fetch_reddit_competitivehs.py --limit 200 --with-comments
"""
import argparse
import re
import sys
import time

from common import fetch_json, write_out

SUB = "CompetitiveHS"

# Flairs and title patterns that mark a meta/deck-choice writeup rather than a
# question thread. Tuned to what the sub actually uses.
TITLE_HINTS = re.compile(
    r"(state of the meta|meta ?snapshot|tier list|top ?\d+ legend|"
    r"#\d+\s*legend|to legend|climb|deck ?guide|vs data reaper|data reaper|"
    r"season recap|end of season|wild meta|standard meta|report)", re.I)


def listing(kind, t=None, limit=100, after=None):
    url = f"https://www.reddit.com/r/{SUB}/{kind}.json?limit={min(limit,100)}"
    if t:
        url += f"&t={t}"
    if after:
        url += f"&after={after}"
    return fetch_json(url)


def harvest(kind, t, want):
    out, after, seen = [], None, 0
    while seen < want:
        j = listing(kind, t=t, limit=100, after=after)
        if not j or "data" not in j:
            break
        kids = j["data"].get("children") or []
        if not kids:
            break
        for c in kids:
            d = c.get("data") or {}
            out.append({
                "id": d.get("id"),
                "title": d.get("title"),
                "flair": d.get("link_flair_text"),
                "score": d.get("score"),
                "num_comments": d.get("num_comments"),
                "created_utc": d.get("created_utc"),
                "author": d.get("author"),
                "permalink": "https://www.reddit.com" + (d.get("permalink") or ""),
                "selftext": d.get("selftext") or "",
                "sort_bucket": f"{kind}/{t or 'all'}",
            })
        seen += len(kids)
        after = j["data"].get("after")
        if not after:
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=100,
                    help="posts to pull per sort bucket")
    ap.add_argument("--with-comments", action="store_true",
                    help="also pull top comments for matching threads (slow)")
    ap.add_argument("--comment-cap", type=int, default=60,
                    help="max threads to pull comments for")
    a = ap.parse_args()

    buckets = [("top", "all"), ("top", "year"), ("top", "month"),
               ("hot", None), ("new", None)]
    posts, byid = [], {}
    for kind, t in buckets:
        got = harvest(kind, t, a.limit)
        print(f"[reddit] {kind}/{t or 'all'}: {len(got)} posts", file=sys.stderr)
        for pst in got:
            if pst["id"] and pst["id"] not in byid:
                byid[pst["id"]] = pst
                posts.append(pst)

    for pst in posts:
        pst["meta_relevant"] = bool(
            TITLE_HINTS.search(pst["title"] or "") or
            TITLE_HINTS.search(pst["flair"] or ""))

    relevant = [p for p in posts if p["meta_relevant"]]
    relevant.sort(key=lambda p: -(p["score"] or 0))
    print(f"[reddit] {len(posts)} unique posts, {len(relevant)} look meta-relevant",
          file=sys.stderr)

    if a.with_comments:
        for i, pst in enumerate(relevant[:a.comment_cap]):
            j = fetch_json(pst["permalink"].rstrip("/") + ".json?limit=50&sort=top")
            if not j or len(j) < 2:
                continue
            cs = []
            for c in (j[1].get("data", {}).get("children") or []):
                d = c.get("data") or {}
                if d.get("body"):
                    cs.append({"author": d.get("author"), "score": d.get("score"),
                               "body": d["body"]})
            pst["top_comments"] = sorted(cs, key=lambda x: -(x["score"] or 0))[:25]
            if i % 10 == 0:
                print(f"  comments {i}/{min(len(relevant), a.comment_cap)}", file=sys.stderr)

    write_out("reddit_competitivehs.json", {
        "source": f"https://www.reddit.com/r/{SUB}/ public JSON",
        "fetched_utc": time.time(),
        "n_posts": len(posts),
        "n_meta_relevant": len(relevant),
        "note": "selftext is the author's own writeup. These are high-legend players "
                "explaining deck choice and tech, which is qualitative evidence, not "
                "sampled statistics. Score reflects reddit popularity, not deck strength.",
        "posts": posts,
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
