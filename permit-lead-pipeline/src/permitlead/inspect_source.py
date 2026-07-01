"""Confirm a source's live structure + validate its config (network required).

This is how you "confirm the PermitEyes selectors" / "confirm the open-data
columns" without editing Python:

  python -m permitlead.inspect_source permiteyes_berkshire   # dumps tables+forms
  python -m permitlead.inspect_source cambridge              # dumps columns, checks field_map
  python -m permitlead.inspect_source cambridge --sample 3   # + a few parsed permits

For API sources it fetches a few rows, prints the real column names, and flags
any field_map entries that don't exist in the data. For PermitEyes it prints
each table's selector guess + header + sample row so you can paste the right
selectors into config/sources.yaml. Run it where the network is open (your
machine or the GitHub Action) — this sandbox's egress policy blocks these hosts.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from .scrape import build_scraper

ROOT = Path(__file__).resolve().parents[2]


def _api_columns(src_cfg: dict, http: dict) -> dict:
    """Fetch a tiny sample from a socrata/ckan source and report columns."""
    import copy
    cfg = copy.deepcopy(src_cfg)
    cfg["max_rows"] = cfg["page_limit"] = 5
    scraper = build_scraper("_inspect", cfg, http)
    permits = list(scraper.fetch())
    cols = sorted({k for p in permits for k in (p.raw or {}).keys()})
    fmap = src_cfg.get("field_map", {})
    missing = {k: v for k, v in fmap.items() if v and v not in cols}
    return {"sample_count": len(permits), "columns": cols,
            "field_map": fmap, "field_map_missing_columns": missing,
            "ok": not missing and bool(permits)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--sample", type=int, default=0,
                    help="also print N parsed permits")
    args = ap.parse_args()

    sources = yaml.safe_load((ROOT / "config" / "sources.yaml").read_text())
    http = sources.get("http", {})
    src_cfg = sources["sources"].get(args.source)
    if not src_cfg:
        raise SystemExit(f"unknown source {args.source!r}")
    kind = src_cfg.get("kind")

    if kind == "permiteyes":
        scraper = build_scraper(args.source, src_cfg, http)
        print(json.dumps(scraper.discover(), indent=2))
    elif kind in ("socrata", "ckan"):
        report = _api_columns(src_cfg, http)
        print(json.dumps(report, indent=2))
        if report["field_map_missing_columns"]:
            print("\n⚠️  field_map references columns not in the data — fix "
                  "config/sources.yaml before enabling this source.")
    else:
        raise SystemExit(f"inspect not supported for kind {kind!r}")

    if args.sample:
        scraper = build_scraper(args.source, src_cfg, http)
        for p in list(scraper.fetch())[: args.sample]:
            print(json.dumps({"id": p.id, "address": p.address,
                              "type": p.permit_type, "town": p.jurisdiction,
                              "issued": p.issued_date}, indent=2))


if __name__ == "__main__":
    main()
