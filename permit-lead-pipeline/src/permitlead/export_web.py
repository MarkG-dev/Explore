"""Export the contractor portal's data as static JSON (feeds permitleads-app).

Writes one JSON the front-end loads: each contractor + their delivered leads
(scored-arm view — the product experience). Deploys statically on Vercel; no
backend needed for the pilot. Regenerate after each run_daily.

Usage:  python -m permitlead.export_web --db data/permits.db --out ../permitleads-data.json
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from . import db

ROOT = Path(__file__).resolve().parents[2]


def export(db_path: Path) -> dict:
    with db.session(db_path) as conn:
        contractors = []
        for c in conn.execute("SELECT * FROM contractor ORDER BY trade, name"):
            leads = []
            for r in conn.execute(
                """
                SELECT l.id AS lead_id, p.address, p.jurisdiction, p.permit_type,
                       p.owner_name, p.contractor_name, cl.intent_score,
                       cl.adjacencies, cl.freshness_days
                FROM lead l JOIN permit p ON p.id = l.permit_id
                JOIN classification cl ON cl.permit_id = p.id
                WHERE l.contractor_id = ?
                ORDER BY cl.intent_score DESC
                """,
                (c["id"],),
            ):
                leads.append({
                    "lead_id": r["lead_id"],
                    "score": r["intent_score"],
                    "address": r["address"],
                    "town": r["jurisdiction"],
                    "permit_type": r["permit_type"],
                    "owner": r["owner_name"],
                    "owner_pull": not (r["contractor_name"] or "").strip(),
                    "freshness_days": r["freshness_days"],
                    "adjacencies": json.loads(r["adjacencies"] or "[]"),
                })
            contractors.append({
                "id": c["id"], "name": c["name"], "trade": c["trade"],
                "town": c["town"], "arm": c["arm"] or "scored", "leads": leads,
            })
    return {"generated": date.today().isoformat(), "contractors": contractors}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(ROOT / "data" / "permits.db"))
    ap.add_argument("--out", default=str(ROOT.parent / "permitleads-data.json"))
    ap.add_argument("--date", default=None, help="override generated date")
    args = ap.parse_args()
    data = export(Path(args.db))
    if args.date:
        data["generated"] = args.date
    Path(args.out).write_text(json.dumps(data, indent=2))
    n = sum(len(c["leads"]) for c in data["contractors"])
    print(f"exported {len(data['contractors'])} contractors, {n} leads -> {args.out}")


if __name__ == "__main__":
    main()
