"""Daily orchestrator (build-spec §5, task 13).

scrape -> normalize -> classify -> score -> store -> route arms -> emit digests
+ dashboards. One entry point; wire to cron / GitHub Action.

Runs fully offline against the `fixture` source (no key, no network), which is
what CI and `--source fixture` use. Point it at `permiteyes_berkshire` once the
selectors are confirmed and (optionally) ANTHROPIC_API_KEY is set.

Usage:
  python -m permitlead.run_daily --source fixture --out out/
  python -m permitlead.run_daily --source permiteyes_berkshire
  python -m permitlead.run_daily --analyze          # print the double-blind readout
"""
from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from pathlib import Path

import yaml

from . import db
from .arms import assign_arms_stratified, route_leads
from .classify import get_classifier
from .dashboard import render_dashboard
from .digest import raw_digest, scored_digest
from .normalize import normalize
from .outcomes import analyze
from .scrape import build_scraper
from .score import score_permit

ROOT = Path(__file__).resolve().parents[2]


def load_yaml(rel: str) -> dict:
    return yaml.safe_load((ROOT / rel).read_text())


def run(source: str, out_dir: Path, db_path: Path, today: date) -> dict:
    sources = load_yaml("config/sources.yaml")
    scoring = load_yaml("config/scoring.yaml")
    src_cfg = sources["sources"][source]
    classifier = get_classifier(scoring)

    scraped = classified = 0
    started_at = datetime.utcnow().isoformat(timespec="seconds")
    with db.session(db_path) as conn:
        before = db.count_permits(conn, source)
        # 1-2. scrape + normalize + store — log the run either way (health tracking)
        try:
            scraper = build_scraper(source, src_cfg, sources.get("http"))
            for permit in scraper.fetch():
                permit = normalize(permit)
                db.upsert_permit(conn, permit)
                scraped += 1

                # 3-4. classify + score
                trade, adj, conf = classifier.classify(permit)
                classification = score_permit(permit, trade, adj, conf, scoring,
                                              today, model=classifier.model)
                db.upsert_classification(conn, classification)
                classified += 1
            rows_new = db.count_permits(conn, source) - before
            db.record_run(conn, source, started_at, scraped, rows_new, "success")
        except Exception as exc:  # noqa: BLE001 - log dead source, then re-raise
            db.record_run(conn, source, started_at, scraped,
                          db.count_permits(conn, source) - before, "error", str(exc))
            raise

        # 5. route leads to test participants (if any are loaded)
        contractors = [dict(r) for r in conn.execute("SELECT * FROM contractor")]
        if contractors:
            assignment = assign_arms_stratified(contractors)
            for c in contractors:
                c["arm"] = assignment[c["id"]]
                db.upsert_contractor(conn, c["id"], arm=c["arm"])
            delivered = route_leads(
                conn, contractors,
                trade_bucket_for=lambda c: c.get("trade", ""),
                min_score=scoring.get("min_scored_arm_score", 40), today=today,
            )
        else:
            delivered = 0

        # 6. emit digests per test trade + a dashboard per contractor
        out_dir.mkdir(parents=True, exist_ok=True)
        for trade in scoring.get("test_trades", []):
            (out_dir / f"scored_{trade}.md").write_text(scored_digest(conn, trade, today))
            (out_dir / f"raw_{trade}.md").write_text(raw_digest(conn, trade, today))
        for c in contractors:
            (out_dir / f"dashboard_{c['id']}.html").write_text(render_dashboard(conn, c))

    summary = {"source": source, "scraped": scraped, "classified": classified,
               "leads_delivered": delivered, "out": str(out_dir)}
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="fixture")
    ap.add_argument("--out", default=str(ROOT / "out"))
    ap.add_argument("--db", default=str(ROOT / "data" / "permits.db"))
    ap.add_argument("--date", default=date.today().isoformat(),
                    help="scoring 'today' (yyyy-mm-dd) for deterministic runs")
    ap.add_argument("--analyze", action="store_true",
                    help="print the double-blind conversion readout and exit")
    args = ap.parse_args()

    if args.analyze:
        with db.session(Path(args.db)) as conn:
            print(json.dumps(analyze(conn), indent=2))
        return

    summary = run(args.source, Path(args.out), Path(args.db),
                  date.fromisoformat(args.date))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
