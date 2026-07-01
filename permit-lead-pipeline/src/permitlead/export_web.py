"""Export the contractor portal's data as static JSON (feeds permitleads-app).

Now models the real PRODUCT, not the experiment: leads are assigned EXCLUSIVELY
(hybrid model in config/product.yaml) — one contractor per trade per lead, with
capacity caps per region — and each lead carries a contractor-sent outreach
draft (Tier B). Also emits per-contractor alerts (Tier A) and the waitlist.

Deploys statically on Vercel; regenerate after each run_daily.

Usage:  python -m permitlead.export_web --db data/permits.db --out ../permitleads-data.json
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import yaml

from . import db
from .alerts import build_alerts
from .assign import assign_exclusive, region_of, waitlist as compute_waitlist, active_pools
from .outreach import draft

ROOT = Path(__file__).resolve().parents[2]


def _load_leads(conn) -> list[dict]:
    leads = []
    for r in conn.execute(
        """
        SELECT p.id AS lead_id, p.address, p.jurisdiction AS town, p.permit_type,
               p.owner_name, p.contractor_name, cl.primary_trade, cl.intent_score,
               cl.adjacencies, cl.freshness_days
        FROM permit p JOIN classification cl ON cl.permit_id = p.id
        """
    ):
        leads.append({
            "lead_id": r["lead_id"], "address": r["address"], "town": r["town"],
            "permit_type": r["permit_type"], "owner": r["owner_name"],
            "owner_pull": not (r["contractor_name"] or "").strip(),
            "primary_trade": r["primary_trade"], "score": r["intent_score"],
            "adjacencies": json.loads(r["adjacencies"] or "[]"),
            "freshness_days": r["freshness_days"],
        })
    return leads


def export(db_path: Path, product: dict) -> dict:
    regions = product["regions"]
    caps = product["exclusivity"]["caps"]
    adj_map = product["adjacency_to_trade"]
    hot = product["alerts"]["hot_score"]

    with db.session(db_path) as conn:
        contractors = [dict(r) for r in conn.execute("SELECT * FROM contractor")]
        leads = _load_leads(conn)

    assigned = assign_exclusive(leads, contractors, regions, caps, adj_map)
    by_id = {c["id"]: c for c in contractors}

    # Attach a contractor-sent outreach draft to each assigned lead.
    for cid, cleads in assigned.items():
        for l in cleads:
            l["drafts"] = draft(l, by_id[cid])

    alerts = build_alerts(assigned, by_id, hot)

    active = active_pools(contractors, regions, caps)
    wait = compute_waitlist(contractors, active, regions)

    out_contractors = []
    for c in contractors:
        out_contractors.append({
            "id": c["id"], "name": c["name"], "trade": c["trade"],
            "town": c["town"], "region": region_of(c.get("town", ""), regions),
            "active": c["id"] not in {w["id"] for w in wait},
            "leads": assigned.get(c["id"], []),
        })

    return {
        "generated": date.today().isoformat(),
        "model": product["exclusivity"]["mode"],
        "contractors": out_contractors,
        "alerts": alerts,
        "waitlist": [{"id": w["id"], "name": w["name"], "trade": w["trade"],
                      "region": region_of(w.get("town", ""), regions)} for w in wait],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(ROOT / "data" / "permits.db"))
    ap.add_argument("--out", default=str(ROOT.parent / "permitleads-data.json"))
    ap.add_argument("--date", default=None)
    args = ap.parse_args()

    product = yaml.safe_load((ROOT / "config" / "product.yaml").read_text())
    data = export(Path(args.db), product)
    if args.date:
        data["generated"] = args.date
    Path(args.out).write_text(json.dumps(data, indent=2))
    n = sum(len(c["leads"]) for c in data["contractors"])
    print(f"exported {len(data['contractors'])} contractors, {n} exclusive leads, "
          f"{len(data['alerts'])} alerts, {len(data['waitlist'])} waitlisted -> {args.out}")


if __name__ == "__main__":
    main()
