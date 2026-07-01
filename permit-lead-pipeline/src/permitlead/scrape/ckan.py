"""CKAN datastore adapter (Boston's Analyze Boston runs CKAN, not Socrata).

CKAN's datastore_search returns {"result": {"records": [...], "total": N}}.
We paginate with limit/offset and reuse the Socrata row->Permit mapper (both are
just lists of dicts). Field names differ per dataset -> config `field_map`.
"""
from __future__ import annotations

import time
from typing import Iterable

from ..httpclient import get
from ..models import Permit
from .base import Scraper
from .socrata import row_to_permit


class CkanScraper(Scraper):
    def fetch(self) -> Iterable[Permit]:
        fmap = self.cfg.get("field_map", {})
        jurisdiction = self.cfg.get("jurisdiction", "")
        limit = self.cfg.get("page_limit", 1000)
        max_rows = self.cfg.get("max_rows", 5000)
        headers = {"User-Agent": self.http.get("user_agent", "PermitPilot/0.1")}

        offset = 0
        while offset < max_rows:
            params = {"resource_id": self.cfg["resource_id"],
                      "limit": limit, "offset": offset}
            if self.cfg.get("q"):
                params["q"] = self.cfg["q"]
            resp = get(self.cfg["base_url"], params=params, headers=headers,
                       timeout=self.http.get("timeout_seconds", 30))
            result = resp.json().get("result", {})
            records = result.get("records", [])
            if not records:
                break
            for row in records:
                p = row_to_permit(row, self.name, fmap, jurisdiction)
                if p is not None:
                    yield p
            offset += limit
            if offset >= result.get("total", 0):
                break
            time.sleep(self.cfg.get("rate_limit_seconds", 1))
