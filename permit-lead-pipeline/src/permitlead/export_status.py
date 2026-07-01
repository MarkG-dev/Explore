"""Export scraper-source health as static JSON (feeds the ops dashboard).

Reads config/sources.yaml + the run_log and computes, per source: enabled state,
endpoint, coverage (jurisdictions), field_map coverage, last-run metrics, and a
health verdict (ok / stale / dead / never / disabled) — the dead-source and
row-count monitoring the research calls for. No network; safe to run anywhere.

Usage:  python -m permitlead.export_status --db data/permits.db --out ../sources-status.json
"""
from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timezone
from pathlib import Path

import yaml

from . import db

ROOT = Path(__file__).resolve().parents[2]
STALE_DAYS = 2   # a source with no successful run in this many days is "stale"

CONFIRMABLE = {"permiteyes", "socrata", "ckan"}   # need live confirm before trusting


def _last_run(conn, source: str):
    row = conn.execute(
        """SELECT started_at, finished_at, rows_scraped, rows_new, status, error
           FROM run_log WHERE source=? ORDER BY id DESC LIMIT 1""", (source,)
    ).fetchone()
    return dict(row) if row else None


def _age_days(iso: str, now: datetime) -> float:
    try:
        return (now - datetime.fromisoformat(iso)).total_seconds() / 86400
    except (ValueError, TypeError):
        return 1e9


def _health(enabled: bool, last, now: datetime) -> str:
    if not enabled:
        return "disabled"
    if not last:
        return "never"
    if last["status"] == "error":
        return "dead"
    if (last["rows_scraped"] or 0) == 0:
        return "dead"                       # ran but returned nothing
    if _age_days(last["finished_at"], now) > STALE_DAYS:
        return "stale"
    return "ok"


def export(db_path: Path, sources_cfg: dict, now: datetime) -> dict:
    out_sources = []
    with db.session(db_path) as conn:
        db_permits = conn.execute("SELECT COUNT(*) n FROM permit").fetchone()["n"]
        for sid, cfg in sources_cfg["sources"].items():
            kind = cfg.get("kind")
            enabled = bool(cfg.get("enabled"))
            last = _last_run(conn, sid)
            health = _health(enabled, last, now)
            confirmed = bool(last and last["status"] == "success"
                             and (last["rows_scraped"] or 0) > 0)
            out_sources.append({
                "id": sid,
                "kind": kind,
                "enabled": enabled,
                "endpoint": cfg.get("base_url") or cfg.get("resource_url")
                            or cfg.get("path") or "",
                "jurisdictions": cfg.get("jurisdictions")
                                 or ([cfg["jurisdiction"]] if cfg.get("jurisdiction") else []),
                "field_map_fields": sorted((cfg.get("field_map") or {}).keys()),
                "last_run": last,
                "health": health,
                "needs_confirm": kind in CONFIRMABLE and not confirmed,
            })
    healthy = sum(1 for s in out_sources if s["health"] == "ok")
    return {
        "generated": now.date().isoformat(),
        "db_permits": db_permits,
        "totals": {
            "sources": len(out_sources),
            "enabled": sum(1 for s in out_sources if s["enabled"]),
            "healthy": healthy,
            "needs_confirm": sum(1 for s in out_sources if s["needs_confirm"]),
        },
        "sources": out_sources,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(ROOT / "data" / "permits.db"))
    ap.add_argument("--out", default=str(ROOT.parent / "sources-status.json"))
    ap.add_argument("--now", default=None, help="ISO timestamp override (tests)")
    args = ap.parse_args()
    now = datetime.fromisoformat(args.now) if args.now else datetime.now(timezone.utc).replace(tzinfo=None)
    sources_cfg = yaml.safe_load((ROOT / "config" / "sources.yaml").read_text())
    data = export(Path(args.db), sources_cfg, now)
    Path(args.out).write_text(json.dumps(data, indent=2))
    t = data["totals"]
    print(f"status: {t['sources']} sources, {t['enabled']} enabled, "
          f"{t['healthy']} healthy, {t['needs_confirm']} need confirm -> {args.out}")


if __name__ == "__main__":
    main()
