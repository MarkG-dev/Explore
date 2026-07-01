"""Load pilot contractors from config/contractors.csv into the DB (task #3).

These are public business listings (recruiting list). Arm assignment happens
automatically in run_daily; this just gets them into the `contractor` table.

Usage:  python -m permitlead.seed_contractors --db data/permits.db
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from . import db

ROOT = Path(__file__).resolve().parents[2]


def seed(db_path: Path, csv_path: Path) -> int:
    n = 0
    with db.session(db_path) as conn:
        for row in csv.DictReader(csv_path.open()):
            db.upsert_contractor(
                conn, row["id"], name=row["name"], trade=row["trade"],
                town=row.get("town", ""), phone=row.get("phone", ""),
                email=row.get("email", ""),
            )
            n += 1
    return n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(ROOT / "data" / "permits.db"))
    ap.add_argument("--csv", default=str(ROOT / "config" / "contractors.csv"))
    args = ap.parse_args()
    count = seed(Path(args.db), Path(args.csv))
    print(f"seeded {count} contractors into {args.db}")


if __name__ == "__main__":
    main()
