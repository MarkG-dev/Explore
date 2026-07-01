"""Render the two arms' outputs (build-spec §4, task 10).

Arm A (scored): ranked, scored, adjacency-annotated digest.
Arm B (raw):    same permits as a flat chronological list — no score, no rank,
                no adjacency. This is the PermitGrab-style control.

Both are generated from the identical permit pool so the only variable is
presentation. Markdown out (easy to email or paste); trivially HTML-able.
"""
from __future__ import annotations

import json
from datetime import date


def _permit_rows(conn, trade: str):
    return conn.execute(
        """
        SELECT p.address, p.jurisdiction, p.permit_type, p.owner_name,
               p.contractor_name, p.applied_date, p.issued_date, p.valuation,
               cl.intent_score, cl.adjacencies, cl.freshness_days
        FROM permit p JOIN classification cl ON cl.permit_id = p.id
        WHERE cl.primary_trade = ?
        ORDER BY cl.intent_score DESC, p.last_seen DESC
        """,
        (trade,),
    ).fetchall()


def scored_digest(conn, trade: str, today: date) -> str:
    """Arm A: the wedge — score, rank, adjacency, why-it-matters."""
    rows = _permit_rows(conn, trade)
    out = [f"# Scored {trade.title()} Leads — {today.isoformat()}",
           f"_{len(rows)} leads, ranked by intent score._\n"]
    for r in rows:
        adj = json.loads(r["adjacencies"] or "[]")
        adj_str = ", ".join(f"{a['trade']} ({a['est_value_band']})" for a in adj) or "—"
        fresh = f"{r['freshness_days']}d old" if r["freshness_days"] is not None else "age?"
        owner_pull = "  ⚑ owner-pull (no contractor listed)" if not r["contractor_name"] else ""
        out.append(
            f"## [{r['intent_score']}] {r['address']}, {r['jurisdiction']}\n"
            f"- **Permit:** {r['permit_type']}  ·  {fresh}{owner_pull}\n"
            f"- **Owner:** {r['owner_name'] or 'n/a'}\n"
            f"- **Adjacent opportunities:** {adj_str}\n"
        )
    return "\n".join(out)


def raw_digest(conn, trade: str, today: date) -> str:
    """Arm B: control — flat list, chronological, no score/rank/adjacency."""
    rows = sorted(_permit_rows(conn, trade),
                  key=lambda r: (r["applied_date"] or ""), reverse=True)
    out = [f"# {trade.title()} Permits — {today.isoformat()}",
           "| Date | Address | Town | Type | Owner |",
           "|---|---|---|---|---|"]
    for r in rows:
        out.append(
            f"| {r['applied_date'] or r['issued_date'] or '—'} | {r['address']} "
            f"| {r['jurisdiction']} | {r['permit_type']} | {r['owner_name'] or '—'} |"
        )
    return "\n".join(out)
