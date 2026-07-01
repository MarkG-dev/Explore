"""SQLite persistence (build-spec §2). Single file, zero infra.

Upserts are idempotent on stable IDs so daily re-scrapes don't duplicate.
The Outcome table is present from day one on purpose: it's the double-blind
test's primary metric AND the un-recreatable won/lost data loop (handoff §7.2).
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional

from .models import Classification, Lead, Permit, to_json

SCHEMA = """
CREATE TABLE IF NOT EXISTS permit (
    id               TEXT PRIMARY KEY,
    source           TEXT NOT NULL,
    source_permit_id TEXT NOT NULL,
    jurisdiction     TEXT,
    address          TEXT,
    parcel_id        TEXT,
    permit_type      TEXT,
    description      TEXT,
    status           TEXT,
    applied_date     TEXT,
    issued_date      TEXT,
    valuation        REAL,
    contractor_name  TEXT,
    owner_name       TEXT,
    raw              TEXT,
    first_seen       TEXT,
    last_seen        TEXT
);
CREATE TABLE IF NOT EXISTS classification (
    permit_id      TEXT PRIMARY KEY REFERENCES permit(id),
    primary_trade  TEXT,
    adjacencies    TEXT,
    intent_score   INTEGER,
    freshness_days INTEGER,
    confidence     REAL,
    model          TEXT,
    classified_at  TEXT
);
CREATE TABLE IF NOT EXISTS contractor (
    id       TEXT PRIMARY KEY,
    name     TEXT,
    trade    TEXT,
    town     TEXT,
    email    TEXT,
    phone    TEXT,
    arm      TEXT              -- assigned test arm: 'scored' | 'raw'
);
CREATE TABLE IF NOT EXISTS lead (
    id            TEXT PRIMARY KEY,
    permit_id     TEXT REFERENCES permit(id),
    arm           TEXT,
    trade_bucket  TEXT,
    contractor_id TEXT REFERENCES contractor(id),
    delivered_at  TEXT
);
CREATE TABLE IF NOT EXISTS contact (
    permit_id    TEXT REFERENCES permit(id),
    email        TEXT,
    phone        TEXT,
    contact_type TEXT,
    source       TEXT,
    confidence   REAL
);
CREATE TABLE IF NOT EXISTS outcome (
    lead_id       TEXT REFERENCES lead(id),
    contractor_id TEXT REFERENCES contractor(id),
    status        TEXT,          -- contacted/quoted/won/lost/no_response
    job_value     REAL,
    noted_at      TEXT
);
CREATE TABLE IF NOT EXISTS run_log (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    source        TEXT,
    started_at    TEXT,
    finished_at   TEXT,
    rows_scraped  INTEGER,
    rows_new      INTEGER,
    status        TEXT,          -- success | error
    error         TEXT
);
CREATE INDEX IF NOT EXISTS idx_class_score ON classification(intent_score);
CREATE INDEX IF NOT EXISTS idx_lead_arm ON lead(arm);
CREATE INDEX IF NOT EXISTS idx_runlog_source ON run_log(source, finished_at);
"""


def connect(db_path: str | Path) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn


@contextmanager
def session(db_path: str | Path) -> Iterator[sqlite3.Connection]:
    conn = connect(db_path)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


def upsert_permit(conn: sqlite3.Connection, p: Permit) -> None:
    """Insert or refresh. Preserves first_seen; always bumps last_seen."""
    now = _now()
    conn.execute(
        """
        INSERT INTO permit (id, source, source_permit_id, jurisdiction, address,
            parcel_id, permit_type, description, status, applied_date, issued_date,
            valuation, contractor_name, owner_name, raw, first_seen, last_seen)
        VALUES (:id,:source,:source_permit_id,:jurisdiction,:address,:parcel_id,
            :permit_type,:description,:status,:applied_date,:issued_date,:valuation,
            :contractor_name,:owner_name,:raw,:now,:now)
        ON CONFLICT(id) DO UPDATE SET
            jurisdiction=excluded.jurisdiction, address=excluded.address,
            parcel_id=excluded.parcel_id, permit_type=excluded.permit_type,
            description=excluded.description, status=excluded.status,
            applied_date=excluded.applied_date, issued_date=excluded.issued_date,
            valuation=excluded.valuation, contractor_name=excluded.contractor_name,
            owner_name=excluded.owner_name, raw=excluded.raw, last_seen=:now
        """,
        {**p.__dict__, "raw": to_json(p.raw), "now": now},
    )


def upsert_classification(conn: sqlite3.Connection, c: Classification) -> None:
    conn.execute(
        """
        INSERT INTO classification (permit_id, primary_trade, adjacencies,
            intent_score, freshness_days, confidence, model, classified_at)
        VALUES (:permit_id,:primary_trade,:adjacencies,:intent_score,
            :freshness_days,:confidence,:model,:classified_at)
        ON CONFLICT(permit_id) DO UPDATE SET
            primary_trade=excluded.primary_trade, adjacencies=excluded.adjacencies,
            intent_score=excluded.intent_score, freshness_days=excluded.freshness_days,
            confidence=excluded.confidence, model=excluded.model,
            classified_at=excluded.classified_at
        """,
        {
            "permit_id": c.permit_id,
            "primary_trade": c.primary_trade,
            "adjacencies": to_json(c.adjacencies),
            "intent_score": c.intent_score,
            "freshness_days": c.freshness_days,
            "confidence": c.confidence,
            "model": c.model,
            "classified_at": c.classified_at,
        },
    )


def upsert_contractor(conn: sqlite3.Connection, cid: str, **fields: object) -> None:
    cols = ["id"] + list(fields)
    placeholders = ",".join(f":{c}" for c in cols)
    updates = ",".join(f"{c}=excluded.{c}" for c in fields)
    conn.execute(
        f"INSERT INTO contractor ({','.join(cols)}) VALUES ({placeholders}) "
        f"ON CONFLICT(id) DO UPDATE SET {updates}",
        {"id": cid, **fields},
    )


def insert_lead(conn: sqlite3.Connection, lead: Lead) -> None:
    conn.execute(
        """INSERT OR IGNORE INTO lead (id, permit_id, arm, trade_bucket,
               contractor_id, delivered_at)
           VALUES (:id,:permit_id,:arm,:trade_bucket,:contractor_id,:delivered_at)""",
        lead.__dict__,
    )


def count_permits(conn: sqlite3.Connection, source: str) -> int:
    return conn.execute("SELECT COUNT(*) n FROM permit WHERE source=?",
                        (source,)).fetchone()["n"]


def record_run(conn: sqlite3.Connection, source: str, started_at: str,
               rows_scraped: int, rows_new: int, status: str,
               error: Optional[str] = None) -> None:
    conn.execute(
        """INSERT INTO run_log (source, started_at, finished_at, rows_scraped,
               rows_new, status, error) VALUES (?,?,?,?,?,?,?)""",
        (source, started_at, _now(), rows_scraped, rows_new, status, error),
    )


def record_outcome(conn: sqlite3.Connection, lead_id: str, contractor_id: str,
                   status: str, job_value: Optional[float] = None) -> None:
    conn.execute(
        """INSERT INTO outcome (lead_id, contractor_id, status, job_value, noted_at)
           VALUES (?,?,?,?,?)""",
        (lead_id, contractor_id, status, job_value, _now()),
    )
