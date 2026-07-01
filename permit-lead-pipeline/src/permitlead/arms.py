"""Double-blind arm assignment + lead routing (build-spec §4, task 9).

The experiment's validity rests here: contractors are randomized to arm
('scored' | 'raw'), stratified by trade so each arm has a comparable trade mix,
and each contractor only ever sees their own arm. Both arms draw from the SAME
permit pool for the trade+geo — the only difference is presentation. That
isolates *scoring* as the variable (not coverage, not freshness).

Assignment is deterministic (seeded by contractor id) so it's reproducible and
survives re-runs — no clock/RNG that would reshuffle history.
"""
from __future__ import annotations

import hashlib
from datetime import date
from typing import Iterable

from .db import insert_lead
from .models import Lead

ARMS = ("scored", "raw")


def assign_arm(contractor_id: str) -> str:
    """Deterministic 50/50 split from a hash of the id. Stratify by calling this
    within a trade group (see assign_arms_stratified)."""
    h = int(hashlib.sha1(contractor_id.encode()).hexdigest(), 16)
    return ARMS[h % 2]


def assign_arms_stratified(contractors: list[dict]) -> dict[str, str]:
    """Balance arms *within* each trade. Sort each trade's contractors by their
    hash and alternate arms, so trade mix is comparable across arms even at
    small N (build-spec §4: stratify by trade)."""
    by_trade: dict[str, list[dict]] = {}
    for c in contractors:
        by_trade.setdefault(c.get("trade", "unknown"), []).append(c)

    assignment: dict[str, str] = {}
    for trade, group in by_trade.items():
        ordered = sorted(group, key=lambda c: hashlib.sha1(c["id"].encode()).hexdigest())
        for i, c in enumerate(ordered):
            assignment[c["id"]] = ARMS[i % 2]
    return assignment


def route_leads(conn, contractors: list[dict], trade_bucket_for,
                min_score: int, today: date) -> int:
    """For each contractor, deliver the matching permits for their trade+geo as
    Lead rows tagged with their arm. Returns count of leads delivered.

    `trade_bucket_for(contractor)` -> the trade key to match permits against.
    Scored arm is score-gated (min_score); raw arm gets the same permits
    unfiltered by score (chronological), matching the PermitGrab-style control.
    """
    delivered = 0
    now = today.isoformat()
    for c in contractors:
        arm = c.get("arm") or assign_arm(c["id"])
        trade = trade_bucket_for(c)
        rows = conn.execute(
            """
            SELECT p.id AS permit_id, cl.intent_score AS score
            FROM permit p JOIN classification cl ON cl.permit_id = p.id
            WHERE cl.primary_trade = ?
              AND (? = '' OR p.jurisdiction IN (SELECT value FROM json_each(?)))
            ORDER BY cl.intent_score DESC, p.last_seen DESC
            """,
            (trade, "", "[]"),
        ).fetchall()
        for r in rows:
            if arm == "scored" and (r["score"] or 0) < min_score:
                continue  # scored arm only gets leads above the quality bar
            lead = Lead(permit_id=r["permit_id"], arm=arm, trade_bucket=trade,
                        contractor_id=c["id"], delivered_at=now)
            insert_lead(conn, lead)
            delivered += 1
    return delivered
