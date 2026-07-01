"""Canonical data model (build-spec §2).

Plain dataclasses + a hashing helper for stable IDs. The DB layer (db.py) owns
the SQLite DDL; these types are what the rest of the pipeline passes around.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from typing import Any, Optional


def stable_id(*parts: str) -> str:
    """Deterministic id from source + source permit id, so re-scrapes upsert."""
    joined = "|".join(p.strip().lower() for p in parts if p)
    return hashlib.sha1(joined.encode("utf-8")).hexdigest()[:16]


@dataclass
class Permit:
    source: str
    source_permit_id: str
    jurisdiction: str = ""
    address: str = ""
    parcel_id: Optional[str] = None
    permit_type: str = ""
    description: str = ""
    status: str = ""
    applied_date: Optional[str] = None   # ISO yyyy-mm-dd
    issued_date: Optional[str] = None
    valuation: Optional[float] = None
    contractor_name: Optional[str] = None
    owner_name: Optional[str] = None
    raw: dict[str, Any] = field(default_factory=dict)
    id: str = ""

    def __post_init__(self) -> None:
        if not self.id:
            self.id = stable_id(self.source, self.source_permit_id)

    @property
    def reference_date(self) -> Optional[str]:
        """Best available project date for freshness = issued, else applied."""
        return self.issued_date or self.applied_date

    @property
    def owner_pull(self) -> bool:
        """No contractor named -> possible owner/DIY pull = direct-lead signal."""
        return not (self.contractor_name or "").strip()


@dataclass
class Adjacency:
    trade: str
    rationale: str = ""
    est_value_band: str = "unknown"


@dataclass
class Classification:
    permit_id: str
    primary_trade: str
    adjacencies: list[Adjacency] = field(default_factory=list)
    intent_score: int = 0
    freshness_days: Optional[int] = None
    confidence: float = 0.0
    model: str = "rules"
    classified_at: str = ""

    def __post_init__(self) -> None:
        if not self.classified_at:
            self.classified_at = datetime.utcnow().isoformat(timespec="seconds")


@dataclass
class Lead:
    permit_id: str
    arm: str                       # 'scored' | 'raw'
    trade_bucket: str
    contractor_id: Optional[str] = None
    delivered_at: Optional[str] = None
    id: str = ""

    def __post_init__(self) -> None:
        if not self.id:
            self.id = stable_id(self.permit_id, self.arm, self.contractor_id or "")


def to_json(obj: Any) -> str:
    """Serialize dataclasses/dates for the `raw` and adjacency JSON columns."""
    def default(o: Any) -> Any:
        if isinstance(o, (date, datetime)):
            return o.isoformat()
        if hasattr(o, "__dataclass_fields__"):
            return asdict(o)
        raise TypeError(f"not serializable: {type(o)}")
    return json.dumps(obj, default=default, ensure_ascii=False)
