"""Tier A — alert the CONTRACTOR (our customer). Zero TCPA risk; they opted in.

Builds a per-contractor alert payload: how many new hot leads, the top one, and
a ready-to-send digest body. An email/SMS provider consumes this JSON; we don't
send here (no secrets in the pipeline). This is the workflow-stickiness wedge.
"""
from __future__ import annotations


def build_alerts(leads_by_contractor: dict, contractors_by_id: dict,
                 hot_score: int) -> list[dict]:
    alerts = []
    for cid, leads in leads_by_contractor.items():
        hot = [l for l in leads if l.get("score", 0) >= hot_score]
        if not hot:
            continue
        c = contractors_by_id.get(cid, {})
        top = hot[0]
        body_lines = [f"{len(hot)} new hot lead(s) for {c.get('name','you')}:", ""]
        for l in hot[:5]:
            body_lines.append(
                f"  [{l['score']}] {l.get('address','')}, {l.get('town','')} "
                f"— {l.get('match_reason', l.get('permit_type',''))}"
            )
        body_lines += ["", "Open your dashboard to mark won/lost and get outreach drafts."]
        alerts.append({
            "contractor_id": cid,
            "contractor": c.get("name", cid),
            "channel": "email",
            "hot_count": len(hot),
            "top_lead": {"score": top["score"], "address": top.get("address"),
                         "town": top.get("town")},
            "subject": f"{len(hot)} new permit lead(s) in your area",
            "body": "\n".join(body_lines),
        })
    return alerts
