"""Scraper contract + a fixture source so the whole pipeline runs offline."""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable

from ..models import Permit


class Scraper(ABC):
    """A source knows how to yield canonical Permit objects. Nothing else."""

    def __init__(self, name: str, cfg: dict, http: dict | None = None) -> None:
        self.name = name
        self.cfg = cfg
        self.http = http or {}

    @abstractmethod
    def fetch(self) -> Iterable[Permit]:
        ...


class FixtureScraper(Scraper):
    """Reads a JSON array of permit dicts from disk. No network. Used by tests,
    CI, and `run_daily --source fixture` so the pipeline is always runnable."""

    def fetch(self) -> Iterable[Permit]:
        path = Path(self.cfg["path"])
        if not path.is_absolute():
            # resolve relative to the project root (two levels up from src/permitlead)
            path = Path(__file__).resolve().parents[3] / path
        rows = json.loads(path.read_text())
        for row in rows:
            yield Permit(
                source=self.name,
                source_permit_id=str(row["source_permit_id"]),
                jurisdiction=row.get("jurisdiction", ""),
                address=row.get("address", ""),
                parcel_id=row.get("parcel_id"),
                permit_type=row.get("permit_type", ""),
                description=row.get("description", ""),
                status=row.get("status", ""),
                applied_date=row.get("applied_date"),
                issued_date=row.get("issued_date"),
                valuation=row.get("valuation"),
                contractor_name=row.get("contractor_name"),
                owner_name=row.get("owner_name"),
                raw=row,
            )
