"""Exclusive lead assignment (answers "how do we offer exclusives").

Hybrid model: a lead is delivered to at most ONE contractor per trade (never
resold), and only a capped number of subscribers per (trade, region) are active
(the scarcity you sell). Extra sign-ups go on a waitlist.

One permit can still become leads for SEVERAL trades — a roof permit is a solar
lead for a solar sub AND (if owner-pulled) a roofing lead for a roofer. That
fan-out is the value; exclusivity just means each of those goes to one sub.

Pure functions over plain dicts so it's easy to test and reuse at export time.
"""
from __future__ import annotations

CONTRACTOR_TRADES = {"roofing", "solar", "hvac", "remodel"}


def region_of(town: str, regions: dict) -> str:
    for name, towns in regions.items():
        if town in towns:
            return name
    return "Other"


def eligible_trades(lead: dict, adjacency_to_trade: dict) -> set[str]:
    """Which subscriber-trades this permit is a lead for."""
    trades: set[str] = set()
    # owner-pulled (no contractor listed) -> the primary trade itself is a live lead
    if lead.get("owner_pull") and lead["primary_trade"] in CONTRACTOR_TRADES:
        trades.add(lead["primary_trade"])
    # adjacent-trade opportunities (the fan-out) -> map onto our subscriber trades
    for a in lead.get("adjacencies", []):
        mapped = adjacency_to_trade.get(a.get("trade"))
        if mapped in CONTRACTOR_TRADES:
            trades.add(mapped)
    return trades


def active_pools(contractors: list[dict], regions: dict, caps: dict) -> dict:
    """Capped subscriber pool per (trade, region). Deterministic (sorted by id)."""
    pools: dict[tuple, list[dict]] = {}
    for c in contractors:
        key = (c["trade"], region_of(c.get("town", ""), regions))
        pools.setdefault(key, []).append(c)
    active: dict[tuple, list[dict]] = {}
    for key, members in pools.items():
        cap = caps.get(key[0], caps.get("default", 3))
        active[key] = sorted(members, key=lambda c: c["id"])[:cap]
    return active


def waitlist(contractors: list[dict], active: dict, regions: dict) -> list[dict]:
    active_ids = {c["id"] for members in active.values() for c in members}
    return [c for c in contractors if c["id"] not in active_ids]


def assign_exclusive(leads: list[dict], contractors: list[dict], regions: dict,
                     caps: dict, adjacency_to_trade: dict) -> dict[str, list[dict]]:
    """Return {contractor_id: [lead-with-match, ...]}.

    Highest-score leads assigned first; within a (trade, region) pool the
    least-loaded active subscriber wins (round-robin exclusivity).
    """
    active = active_pools(contractors, regions, caps)
    load = {c["id"]: 0 for c in contractors}
    out: dict[str, list[dict]] = {c["id"]: [] for c in contractors}

    for lead in sorted(leads, key=lambda l: -l.get("score", 0)):
        region = region_of(lead.get("town", ""), regions)
        for trade in eligible_trades(lead, adjacency_to_trade):
            pool = active.get((trade, region), [])
            if not pool:
                continue
            winner = min(pool, key=lambda c: (load[c["id"]], c["id"]))
            enriched = dict(lead)
            enriched["matched_trade"] = trade
            enriched["exclusive"] = True
            enriched["match_reason"] = (
                f"owner-pulled {trade} permit" if trade == lead["primary_trade"]
                else f"{lead['primary_trade']} permit → {trade} opportunity"
            )
            out[winner["id"]].append(enriched)
            load[winner["id"]] += 1
    for cid in out:
        out[cid].sort(key=lambda l: -l.get("score", 0))
    return out
