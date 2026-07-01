"""Socrata / open-data adapter (build robustness — see ma-permit-data-sources.md).

Big MA cities publish permits on Socrata as a free JSON API
(`https://<domain>/resource/<id>.json`) — fresher and far more reliable than
scraping a portal. Boston, Cambridge, and Somerville are all reachable this way.

Field names differ per dataset, so the source->Permit mapping is CONFIG, not
code (see `field_map` in sources.yaml). Add a new city by adding a config block;
no Python change. A Socrata app token (env SOCRATA_APP_TOKEN) lifts rate limits.
"""
from __future__ import annotations

import time
from datetime import datetime
from typing import Iterable, Optional

from ..models import Permit
from .base import Scraper


def _iso(text) -> Optional[str]:
    if not text:
        return None
    s = str(text).strip()
    # Socrata floating timestamps look like 2026-06-20T00:00:00.000
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d",
                "%m/%d/%Y"):
        try:
            return datetime.strptime(s[:26], fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _num(text) -> Optional[float]:
    try:
        return float(text) if text not in (None, "") else None
    except (TypeError, ValueError):
        return None


def row_to_permit(row: dict, source: str, fmap: dict, jurisdiction: str) -> Optional[Permit]:
    """Map a Socrata row -> Permit using a field-name map. Pure + unit-testable."""
    def g(key: str) -> str:
        col = fmap.get(key)
        return str(row.get(col, "")) if col else ""

    pid = g("permit_id")
    if not pid:
        return None
    return Permit(
        source=source,
        source_permit_id=pid,
        jurisdiction=g("jurisdiction") or jurisdiction,
        address=g("address"),
        permit_type=g("permit_type"),
        description=g("description") or g("permit_type"),
        status=g("status"),
        applied_date=_iso(row.get(fmap.get("applied_date"))),
        issued_date=_iso(row.get(fmap.get("issued_date"))),
        valuation=_num(row.get(fmap.get("valuation"))),
        contractor_name=g("contractor_name") or None,
        owner_name=g("owner_name") or None,
        raw=row,
    )


class SocrataScraper(Scraper):
    def fetch(self) -> Iterable[Permit]:
        import os

        from ..httpclient import get

        fmap = self.cfg.get("field_map", {})
        jurisdiction = self.cfg.get("jurisdiction", "")
        limit = self.cfg.get("page_limit", 1000)
        max_rows = self.cfg.get("max_rows", 5000)
        headers = {"User-Agent": self.http.get("user_agent", "PermitPilot/0.1")}
        token = os.environ.get("SOCRATA_APP_TOKEN")
        if token:
            headers["X-App-Token"] = token

        offset = 0
        while offset < max_rows:
            params = {"$limit": limit, "$offset": offset,
                      "$order": self.cfg.get("order_field", ":id")}
            if self.cfg.get("where"):
                params["$where"] = self.cfg["where"]
            resp = get(self.cfg["resource_url"], params=params, headers=headers,
                       timeout=self.http.get("timeout_seconds", 30))
            rows = resp.json()
            if not rows:
                break
            for row in rows:
                p = row_to_permit(row, self.name, fmap, jurisdiction)
                if p is not None:
                    yield p
            offset += limit
            time.sleep(self.cfg.get("rate_limit_seconds", 1))
