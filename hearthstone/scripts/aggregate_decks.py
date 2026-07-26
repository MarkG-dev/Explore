#!/usr/bin/env python3
"""Aggregate the 346k-deck HearthPwn archive into a compact, committable dataset.

The raw NDJSON is ~307 MB, which is too large to commit (GitHub rejects >100 MB)
and is reproducible from its public source anyway. What is actually useful for a
longitudinal study is the aggregate: for each patch era, which cards and classes
were actually being put in decks, and how that shifted.

Scope: only `extra.deck_type == "Ranked Deck"` rows, since Arena / Tavern Brawl /
PvE / Theorycraft decks are not ranked-ladder evidence.

Honest limits, restated here because they travel with the data:
  * This measures DECK POSTING BEHAVIOUR on HearthPwn, not ladder representation
    and not winrate. There is no games-played or rank field anywhere in the source.
  * Popular archetypes with few published variants are undercounted; brewers and
    meme decks are overcounted.
  * Coverage stops at 2017-03-19.

Outputs (into --out):
  deck_aggregate.json  per-era deck counts, class shares, top cards, top archetypes
"""
import argparse
import json
import os
import sys
from collections import Counter, defaultdict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="/home/user/Explore/hearthstone/data/research/"
                                    "decks_NJacobsohn-Hearthstone-Data-Analysis.ndjson")
    ap.add_argument("--out", default="/home/user/Explore/hearthstone/data")
    ap.add_argument("--top-cards", type=int, default=40)
    args = ap.parse_args()

    if not os.path.exists(args.src):
        print(f"[decks] source missing: {args.src}", file=sys.stderr)
        return 1

    eras = defaultdict(lambda: {
        "decks": 0,
        "classes": Counter(),
        "archetypes": Counter(),
        "cards": Counter(),
        "first_date": None,
        "last_date": None,
    })
    totals = {"read": 0, "ranked": 0, "skipped_no_era": 0}

    with open(args.src) as f:
        for line in f:
            totals["read"] += 1
            try:
                d = json.loads(line)
            except Exception:
                continue
            extra = d.get("extra") or {}
            if extra.get("deck_type") != "Ranked Deck":
                continue
            totals["ranked"] += 1
            era = extra.get("deck_set") or "Unknown"
            if era == "Unknown":
                totals["skipped_no_era"] += 1
            e = eras[era]
            e["decks"] += 1
            if d.get("class"):
                e["classes"][d["class"]] += 1
            arch = d.get("archetype")
            if arch and arch != "Unknown":
                e["archetypes"][arch] += 1
            # count each distinct card once per deck: "what fraction of decks ran this"
            for c in set(d.get("cards") or []):
                e["cards"][c] += 1
            dt = (d.get("date") or "")[:10]
            if dt:
                if not e["first_date"] or dt < e["first_date"]:
                    e["first_date"] = dt
                if not e["last_date"] or dt > e["last_date"]:
                    e["last_date"] = dt

    out = {
        "source": "HearthPwn user-submitted decks via github.com/NJacobsohn/"
                  "Hearthstone-Data-Analysis, normalised to NDJSON then aggregated",
        "scope": 'Only extra.deck_type == "Ranked Deck" rows.',
        "measures": "inclusion_rate = share of that era's ranked decks that ran the "
                    "card at least once. This is deck-posting behaviour, NOT ladder "
                    "playrate and NOT winrate -- the source has no games-played, no "
                    "rank and no winrate field.",
        "limits": [
            "Measures what players published on HearthPwn, not what was queued on ladder.",
            "Archetype labels are author-entered and only ~43% of ranked rows carry one.",
            "Coverage ends 2017-03-19; nothing from Un'Goro onward.",
            "Deleted HearthPwn pages are simply absent (survivorship bias).",
        ],
        "totals": totals,
        "eras": [],
    }
    for era, e in sorted(eras.items(), key=lambda kv: (kv[1]["first_date"] or "9999")):
        n = e["decks"] or 1
        out["eras"].append({
            "era": era,
            "decks": e["decks"],
            "date_range": [e["first_date"], e["last_date"]],
            "class_share": {k: round(v / n, 4) for k, v in e["classes"].most_common()},
            "top_archetypes": [{"archetype": k, "decks": v, "share": round(v / n, 4)}
                               for k, v in e["archetypes"].most_common(15)],
            "top_cards": [{"card": k, "decks": v, "inclusion_rate": round(v / n, 4)}
                          for k, v in e["cards"].most_common(args.top_cards)],
        })

    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, "deck_aggregate.json")
    with open(path, "w") as f:
        json.dump(out, f, separators=(",", ":"))

    print(f"[decks] read {totals['read']:,} rows, {totals['ranked']:,} ranked", file=sys.stderr)
    print(f"[decks] {len(out['eras'])} eras -> {path}", file=sys.stderr)
    for e in out["eras"][:8]:
        top = e["top_cards"][0] if e["top_cards"] else {}
        print(f"    {str(e['era'])[:26]:26s} {e['decks']:>6,} decks  "
              f"{e['date_range'][0]}..{e['date_range'][1]}  "
              f"top: {top.get('card','—')} ({top.get('inclusion_rate',0):.0%})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
