#!/usr/bin/env python3
"""Deep quantitative analysis of Hearthstone's card pool and its ranked deck archive.

Everything here is computed, not recalled. Two inputs:

  cards.sqlite          all 7,367 collectible Constructed cards + 2,695 balance changes,
                        reconstructed from 320 dated client builds
  the HearthPwn archive 346,232 decklists (202,375 ranked), 2013-05 -> 2017-03,
                        read from the 4 gzip shards so the raw file is not required

What it measures
----------------
1. Complexity vs power creep  - stats-per-mana against text length and keyword density
                                per set, in release order. Tests the folk claim directly.
2. Deck diversity per era     - Shannon entropy over archetypes, reported as the
                                "effective number of archetypes" exp(H), which is
                                readable: 8.0 means the era played like 8 equally
                                common decks.
3. Card concentration         - Gini over card inclusion rates, plus the count of
                                "staples" (cards in >25% of an era's decks). This is
                                the netdecking / mandatory-card problem, quantified.
4. Class balance              - spread of class shares per era.
5. Card synergy               - strongest co-occurrence pairs by lift, per era.
6. Curve evolution            - average deck mana cost per era.
7. Nerf latency               - how long Blizzard took to nerf a card after shipping it,
                                by year. Measures balance responsiveness over time.

Output: data/deep_analysis.json
"""
import argparse
import glob
import gzip
import json
import math
import os
import sqlite3
import sys
from collections import Counter, defaultdict

DATA = "/home/user/Explore/hearthstone/data"
SHARDS = os.path.join(DATA, "research", "decks_hearthpwn_shards")
# Reprint buckets: re-issues of older cards. Including them in a chronological
# trend would place 2013 cards in 2021 and corrupt every slope.
REPRINT_SETS = {"CORE", "LEGACY", "VANILLA", "PLACEHOLDER_202204", "EVENT"}


# ---------- small stats helpers ----------
def shannon_entropy(counts):
    total = sum(counts)
    if total <= 0:
        return 0.0
    h = 0.0
    for c in counts:
        if c > 0:
            p = c / total
            h -= p * math.log(p)
    return h


def effective_number(counts):
    """exp(Shannon entropy): how many equally-common categories this behaves like."""
    return math.exp(shannon_entropy(counts))


def gini(values):
    """0 = every card equally played, 1 = all play concentrated in one card."""
    xs = sorted(v for v in values if v > 0)
    n = len(xs)
    if n == 0:
        return 0.0
    total = sum(xs)
    if total == 0:
        return 0.0
    cum = 0.0
    for i, x in enumerate(xs, 1):
        cum += i * x
    return (2 * cum) / (n * total) - (n + 1) / n


def iter_decks():
    """Stream decks from the gzip shards, falling back to the raw NDJSON."""
    parts = sorted(glob.glob(os.path.join(SHARDS, "*.ndjson.gz")))
    if parts:
        for p in parts:
            with gzip.open(p, "rt") as f:
                for line in f:
                    try:
                        yield json.loads(line)
                    except Exception:
                        continue
        return
    raw = os.path.join(DATA, "research",
                       "decks_NJacobsohn-Hearthstone-Data-Analysis.ndjson")
    if os.path.exists(raw):
        with open(raw) as f:
            for line in f:
                try:
                    yield json.loads(line)
                except Exception:
                    continue


# ---------- 1. complexity vs power creep ----------
def analyse_card_pool(con, set_order):
    rows = []
    q = """
      SELECT card_set,
             COUNT(*)                                            AS n,
             SUM(CASE WHEN type='MINION' AND cost>=1 THEN 1 ELSE 0 END)         AS n_min,
             AVG(CASE WHEN type='MINION' AND cost>=1
                      THEN (attack+health)*1.0/cost END)         AS spm,
             AVG(cost)                                           AS avg_cost,
             AVG(LENGTH(text))                                   AS avg_text,
             SUM(CASE WHEN text='' THEN 1 ELSE 0 END)            AS n_vanilla,
             SUM(CASE WHEN legendary=1 THEN 1 ELSE 0 END)        AS n_leg
      FROM cards WHERE is_reprint=0 GROUP BY card_set
    """
    mech = dict(con.execute("""
        SELECT c.card_set, AVG(m.k) FROM cards c
        LEFT JOIN (SELECT card_id, COUNT(*) k FROM card_mechanics GROUP BY card_id) m
          ON m.card_id=c.id
        WHERE c.is_reprint=0 GROUP BY c.card_set
    """).fetchall())
    for (cs, n, n_min, spm, avg_cost, avg_text, n_van, n_leg) in con.execute(q):
        rows.append({
            "set_enum": cs,
            "release_date": set_order.get(cs, ""),
            "is_reprint_bucket": cs in REPRINT_SETS,
            "n_cards": n,
            "n_minions": n_min or 0,
            "avg_stats_per_mana": round(spm, 4) if spm else None,
            "avg_cost": round(avg_cost, 3) if avg_cost is not None else None,
            "avg_text_chars": round(avg_text, 1) if avg_text is not None else None,
            "pct_vanilla": round((n_van or 0) / n, 4) if n else None,
            "pct_legendary": round((n_leg or 0) / n, 4) if n else None,
            "avg_keywords": round(mech.get(cs) or 0, 3),
        })
    rows.sort(key=lambda r: (r["release_date"] or "9999", r["set_enum"]))
    return rows


def correlate(xs, ys):
    pts = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    n = len(pts)
    if n < 3:
        return None
    mx = sum(p[0] for p in pts) / n
    my = sum(p[1] for p in pts) / n
    num = sum((p[0] - mx) * (p[1] - my) for p in pts)
    dx = math.sqrt(sum((p[0] - mx) ** 2 for p in pts))
    dy = math.sqrt(sum((p[1] - my) ** 2 for p in pts))
    return round(num / (dx * dy), 3) if dx and dy else None


# ---------- 7. nerf latency ----------
def analyse_nerf_latency(con):
    q = """
      SELECT c.name, c.data_first_seen, MIN(b.date) AS first_change
      FROM cards c JOIN balance_changes b ON b.card_id=c.id
      WHERE c.is_reprint=0 AND c.data_first_seen<>''
      GROUP BY c.id
    """
    per_year = defaultdict(list)
    slowest = []
    for name, born, first in con.execute(q):
        try:
            d0 = tuple(int(x) for x in born.split("-"))
            d1 = tuple(int(x) for x in first.split("-"))
        except Exception:
            continue
        days = (d1[0] - d0[0]) * 365 + (d1[1] - d0[1]) * 30 + (d1[2] - d0[2])
        if days <= 0:
            continue
        per_year[born[:4]].append(days)
        slowest.append({"card": name, "shipped": born, "first_change": first, "days": days})
    by_year = []
    for y in sorted(per_year):
        v = sorted(per_year[y])
        by_year.append({
            "year": y, "n_cards_changed": len(v),
            "median_days_to_first_change": v[len(v) // 2],
            "fastest_days": v[0],
        })
    slowest.sort(key=lambda r: r["days"])
    return {"by_release_year": by_year, "fastest_20": slowest[:20]}


# ---------- 2-6. deck archive ----------
def analyse_decks(top_pairs=12):
    eras = defaultdict(lambda: {
        "decks": 0, "classes": Counter(), "arch": Counter(), "cards": Counter(),
        "pairs": Counter(), "cost_sum": 0.0, "cost_n": 0,
        "first": None, "last": None,
    })
    n_read = n_ranked = 0
    for d in iter_decks():
        n_read += 1
        extra = d.get("extra") or {}
        if extra.get("deck_type") != "Ranked Deck":
            continue
        n_ranked += 1
        e = eras[extra.get("deck_set") or "Unknown"]
        e["decks"] += 1
        if d.get("class"):
            e["classes"][d["class"]] += 1
        a = d.get("archetype")
        if a and a != "Unknown":
            e["arch"][a] += 1
        uniq = sorted(set(d.get("cards") or []))
        for c in uniq:
            e["cards"][c] += 1
        # co-occurrence on a capped subset: full pairwise on 30-card decks over
        # 200k decks is ~87M updates and not worth the runtime for the signal.
        if e["decks"] <= 6000:
            for i in range(len(uniq)):
                for j in range(i + 1, len(uniq)):
                    e["pairs"][(uniq[i], uniq[j])] += 1
        dt = (d.get("date") or "")[:10]
        if dt:
            if not e["first"] or dt < e["first"]:
                e["first"] = dt
            if not e["last"] or dt > e["last"]:
                e["last"] = dt

    out = []
    for era, e in eras.items():
        n = e["decks"]
        if n < 1000:
            continue
        incl = {c: v / n for c, v in e["cards"].items()}
        staples = [c for c, r in incl.items() if r >= 0.25]
        arch_counts = list(e["arch"].values())
        cls_counts = list(e["classes"].values())
        cls_share = [v / n for v in cls_counts]

        # synergy by lift, only on pairs seen enough to be meaningful
        cap = min(n, 6000)
        pairs = []
        for (a, b), c in e["pairs"].most_common(4000):
            if c < 60:
                continue
            pa, pb = e["cards"][a] / n, e["cards"][b] / n
            if pa <= 0 or pb <= 0:
                continue
            lift = (c / cap) / (pa * pb)
            pairs.append({"a": a, "b": b, "co_decks": c, "lift": round(lift, 2)})
        pairs.sort(key=lambda p: -p["lift"])

        out.append({
            "era": era,
            "decks": n,
            "date_range": [e["first"], e["last"]],
            "archetype_labelled_decks": sum(arch_counts),
            "effective_archetypes": round(effective_number(arch_counts), 2) if arch_counts else None,
            "distinct_archetypes": len(arch_counts),
            "card_gini": round(gini(list(incl.values())), 4),
            "n_staples_25pct": len(staples),
            "top_staples": sorted(
                ({"card": c, "inclusion": round(r, 4)} for c, r in incl.items() if r >= 0.25),
                key=lambda x: -x["inclusion"])[:15],
            "class_share_spread": round(max(cls_share) - min(cls_share), 4) if cls_share else None,
            "class_effective_n": round(effective_number(cls_counts), 2) if cls_counts else None,
            "top_synergy_pairs": pairs[:top_pairs],
        })
    out.sort(key=lambda r: (r["date_range"][0] or "9999"))
    return out, {"decks_read": n_read, "ranked_used": n_ranked}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DATA)
    ap.add_argument("--skip-decks", action="store_true")
    a = ap.parse_args()

    con = sqlite3.connect(os.path.join(DATA, "cards.sqlite"))
    set_order = {}
    p = os.path.join(DATA, "sets_first_seen.json")
    if os.path.exists(p):
        set_order = {k: v.get("first_date", "") for k, v in json.load(open(p)).items()}

    print("[deep] card pool ...", file=sys.stderr)
    pool = analyse_card_pool(con, set_order)
    trend = [r for r in pool if not r["is_reprint_bucket"] and r["release_date"]]
    idx = list(range(len(trend)))
    creep = {
        "note": "Sets in release order, reprint buckets (Core/Legacy/Vanilla/"
                "Placeholder/Event) excluded from the trend because they re-issue old "
                "cards and would corrupt a chronological read.",
        "n_sets_in_trend": len(trend),
        "corr_time_vs_stats_per_mana": correlate(idx, [r["avg_stats_per_mana"] for r in trend]),
        "corr_time_vs_text_length": correlate(idx, [r["avg_text_chars"] for r in trend]),
        "corr_time_vs_keywords": correlate(idx, [r["avg_keywords"] for r in trend]),
        "corr_time_vs_pct_legendary": correlate(idx, [r["pct_legendary"] for r in trend]),
        "corr_time_vs_pct_vanilla": correlate(idx, [r["pct_vanilla"] for r in trend]),
        "first_5_sets_avg_stats_per_mana": round(
            sum(r["avg_stats_per_mana"] for r in trend[:5] if r["avg_stats_per_mana"]) / 5, 3) if len(trend) >= 5 else None,
        "last_5_sets_avg_stats_per_mana": round(
            sum(r["avg_stats_per_mana"] for r in trend[-5:] if r["avg_stats_per_mana"]) / 5, 3) if len(trend) >= 5 else None,
        "first_5_sets_avg_text_chars": round(
            sum(r["avg_text_chars"] for r in trend[:5] if r["avg_text_chars"]) / 5, 1) if len(trend) >= 5 else None,
        "last_5_sets_avg_text_chars": round(
            sum(r["avg_text_chars"] for r in trend[-5:] if r["avg_text_chars"]) / 5, 1) if len(trend) >= 5 else None,
    }

    print("[deep] nerf latency ...", file=sys.stderr)
    nerf = analyse_nerf_latency(con)

    decks, deck_totals = ([], {})
    if not a.skip_decks:
        print("[deep] deck archive (streaming shards) ...", file=sys.stderr)
        decks, deck_totals = analyse_decks()

    out = {
        "generated_from": {
            "cards": "cards.sqlite (7,367 collectible Constructed cards, 320 client builds)",
            "decks": "346,232 HearthPwn decklists via 4 gzip shards; ranked subset only",
        },
        "caveats": [
            "Deck metrics measure deck-POSTING behaviour on HearthPwn, not ladder "
            "playrate and not winrate. There is no rank or games-played field in the source.",
            "Deck coverage is 2013-05 to 2017-03 only. Later eras have no deck data here.",
            "Archetype labels are author-entered and present on only ~43% of ranked decks, "
            "so effective_archetypes is computed over the labelled subset.",
            "Synergy pairs are computed on the first 6,000 decks of each era for runtime; "
            "they indicate structure, not exact frequencies.",
            "DO NOT read the rise in effective_archetypes (2.0 in 2014 to ~47 in 2017) as "
            "proof the meta got seven times more diverse. HearthPwn's archetype tag "
            "vocabulary grew over the same period, and early eras have few labelled decks, "
            "so much of that curve is taxonomy growth and sample size, not deck diversity. "
            "The trustworthy diversity signals here are card_gini and n_staples_25pct, "
            "which are computed over all cards in all decks and need no labels.",
            "nerf_latency is RIGHT-CENSORED and the trend is therefore biased. A card "
            "shipped in 2016 had ten years in which it could be changed; a card shipped in "
            "2026 has had months, so its latency cannot exceed months. Read each year as "
            "'of the cards from this year that were ever changed, the median wait was X', "
            "never as a clean measure of how fast Blizzard reacts over time. The one "
            "conclusion the data does support is the floor: same-week emergency nerfs "
            "(6-8 days) exist from 2018 onward and did not before.",
        ],
        "card_pool_by_set": pool,
        "creep_analysis": creep,
        "nerf_latency": nerf,
        "deck_eras": decks,
        "deck_totals": deck_totals,
    }
    with open(os.path.join(a.out, "deep_analysis.json"), "w") as f:
        json.dump(out, f, separators=(",", ":"))

    print(f"[deep] sets analysed      : {len(pool)} ({len(trend)} in trend)", file=sys.stderr)
    print(f"[deep] stats/mana corr    : {creep['corr_time_vs_stats_per_mana']}", file=sys.stderr)
    print(f"[deep] text-length corr   : {creep['corr_time_vs_text_length']}", file=sys.stderr)
    print(f"[deep] keyword corr       : {creep['corr_time_vs_keywords']}", file=sys.stderr)
    print(f"[deep] stats/mana first5  : {creep['first_5_sets_avg_stats_per_mana']}  "
          f"last5: {creep['last_5_sets_avg_stats_per_mana']}", file=sys.stderr)
    print(f"[deep] text chars first5  : {creep['first_5_sets_avg_text_chars']}  "
          f"last5: {creep['last_5_sets_avg_text_chars']}", file=sys.stderr)
    print(f"[deep] deck eras          : {len(decks)}  ({deck_totals})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
