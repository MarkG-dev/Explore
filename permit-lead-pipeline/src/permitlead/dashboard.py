"""Static HTML dashboard + one-click outcome capture (build-spec §4, tasks 11-12).

No server needed for the trial: generate a single self-contained HTML file per
contractor from SQLite. Each lead has won / lost / no-response buttons that
POST to a tiny endpoint (or, for the zero-infra trial, deep-link to a prefilled
form). The clicks are the Outcome table — the primary metric AND the won/lost
data loop (handoff §7.2), captured from day one.
"""
from __future__ import annotations

import html
import json

_TEMPLATE = """<!doctype html>
<meta charset="utf-8">
<title>Permit Leads — {contractor}</title>
<style>
 body{{font:15px/1.5 system-ui,sans-serif;max-width:820px;margin:2rem auto;padding:0 1rem}}
 .lead{{border:1px solid #ddd;border-radius:10px;padding:12px 16px;margin:12px 0}}
 .score{{display:inline-block;min-width:34px;text-align:center;font-weight:700;
        color:#fff;background:#2b6;border-radius:6px;padding:2px 6px;margin-right:8px}}
 .adj{{color:#555;font-size:13px}} .meta{{color:#777;font-size:13px}}
 button{{border:1px solid #ccc;border-radius:6px;padding:4px 10px;margin-right:6px;cursor:pointer}}
 .won{{background:#e7f7e7}} .lost{{background:#fde8e8}}
</style>
<h1>Your permit leads</h1>
<p class="meta">Contractor: {contractor} · arm: {arm} · {n} leads</p>
{leads}
<script>
 // Zero-infra capture: record clicks locally; export as JSON for the founder.
 // Swap outcomeUrl for a real endpoint when you host it.
 function mark(id, status){{
   const k='outcomes'; const o=JSON.parse(localStorage.getItem(k)||'{{}}');
   o[id]=status; localStorage.setItem(k, JSON.stringify(o));
   document.getElementById('row-'+id).className='lead '+status;
 }}
</script>
"""

_LEAD = """<div class="lead" id="row-{lead_id}">
  <div><span class="score">{score}</span><b>{address}</b>, {town}</div>
  <div class="meta">{permit_type} · owner: {owner}</div>
  <div class="adj">Adjacent: {adj}</div>
  <div style="margin-top:8px">
    <button onclick="mark('{lead_id}','won')">Won</button>
    <button onclick="mark('{lead_id}','lost')">Lost</button>
    <button onclick="mark('{lead_id}','no_response')">No response</button>
  </div>
</div>"""


def render_dashboard(conn, contractor: dict) -> str:
    arm = contractor.get("arm", "scored")
    rows = conn.execute(
        """
        SELECT l.id AS lead_id, p.address, p.jurisdiction, p.permit_type,
               p.owner_name, cl.intent_score, cl.adjacencies
        FROM lead l JOIN permit p ON p.id = l.permit_id
        JOIN classification cl ON cl.permit_id = p.id
        WHERE l.contractor_id = ?
        ORDER BY cl.intent_score DESC
        """,
        (contractor["id"],),
    ).fetchall()

    leads_html = []
    for r in rows:
        adj = json.loads(r["adjacencies"] or "[]")
        adj_str = ", ".join(a["trade"] for a in adj) or "—"
        # Raw arm hides the score/adjacency to stay a true control.
        show_score = r["intent_score"] if arm == "scored" else "•"
        show_adj = adj_str if arm == "scored" else "—"
        leads_html.append(_LEAD.format(
            lead_id=r["lead_id"], score=show_score,
            address=html.escape(r["address"] or ""),
            town=html.escape(r["jurisdiction"] or ""),
            permit_type=html.escape(r["permit_type"] or ""),
            owner=html.escape(r["owner_name"] or "n/a"),
            adj=html.escape(show_adj),
        ))
    return _TEMPLATE.format(
        contractor=html.escape(contractor.get("name", contractor["id"])),
        arm=arm, n=len(rows), leads="\n".join(leads_html),
    )
