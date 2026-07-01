"""PermitEyes Berkshire scraper (build-spec §5, task 1).

Two engines, config-selected:
  - playwright: drives a real browser (the portal 403s bare HTTP). Preferred.
  - httpx:      lightweight GET, works only if the portal serves static HTML.

Selectors live in config (sources.yaml) — confirm them against the live page
once; no Python edit needed to fix a moved column. This module intentionally
does the minimum: fetch rows -> Permit objects. Parsing quirks (date formats,
"see multiple towns" pagination) are isolated in _row_to_permit / _parse_date.

Politeness: honors rate_limit_seconds and a truthful User-Agent. Do not remove.
"""
from __future__ import annotations

import re
import time
from datetime import datetime
from typing import Iterable, Optional

from selectolax.parser import HTMLParser

from ..models import Permit
from .base import Scraper


def _parse_date(text: str) -> Optional[str]:
    text = (text or "").strip()
    if not text:
        return None
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m-%d-%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _money(text: str) -> Optional[float]:
    if not text:
        return None
    digits = re.sub(r"[^0-9.]", "", text)
    try:
        return float(digits) if digits else None
    except ValueError:
        return None


class PermitEyesScraper(Scraper):
    def fetch(self) -> Iterable[Permit]:
        engine = self.cfg.get("engine", "httpx")
        html_pages = (
            self._fetch_playwright() if engine == "playwright" else self._fetch_httpx()
        )
        sel = self.cfg.get("selectors", {})
        for html in html_pages:
            yield from self._parse(html, sel)

    # --- engines -----------------------------------------------------------
    def _fetch_httpx(self) -> list[str]:
        import httpx  # local import so the module loads without the dep

        headers = {"User-Agent": self.http.get("user_agent", "PermitPilot/0.1")}
        timeout = self.http.get("timeout_seconds", 30)
        with httpx.Client(headers=headers, timeout=timeout, follow_redirects=True) as c:
            resp = c.get(self.cfg["base_url"])
            resp.raise_for_status()
            time.sleep(self.cfg.get("rate_limit_seconds", 3))
            return [resp.text]

    def _fetch_playwright(self) -> list[str]:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            # Degrade rather than crash the daily run; log-and-skip.
            print("[permiteyes] playwright not installed; skipping live scrape")
            return []
        pages: list[str] = []
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page(
                user_agent=self.http.get("user_agent", "PermitPilot/0.1")
            )
            page.goto(self.cfg["base_url"], wait_until="networkidle")
            # If the portal filters by jurisdiction, iterate; otherwise one page.
            # (Confirm the filter control against the live page and wire it here.)
            pages.append(page.content())
            time.sleep(self.cfg.get("rate_limit_seconds", 3))
            browser.close()
        return pages

    # --- parsing -----------------------------------------------------------
    def _parse(self, html: str, sel: dict) -> Iterable[Permit]:
        tree = HTMLParser(html)
        table = tree.css_first(sel.get("results_table", "table"))
        if table is None:
            return
        for row in table.css(sel.get("row", "tr")):
            permit = self._row_to_permit(row, sel)
            if permit is not None:
                yield permit

    def _row_to_permit(self, row, sel: dict) -> Optional[Permit]:
        def cell(key: str) -> str:
            css = sel.get(key)
            if not css:
                return ""
            node = row.css_first(css)
            return node.text(strip=True) if node else ""

        permit_no = cell("cell_permit_no")
        if not permit_no:
            return None  # header row / empty
        return Permit(
            source=self.name,
            source_permit_id=permit_no,
            jurisdiction=cell("cell_jurisdiction"),
            address=cell("cell_address"),
            permit_type=cell("cell_type"),
            description=cell("cell_type"),
            status=cell("cell_status"),
            applied_date=_parse_date(cell("cell_applied_date")),
            issued_date=_parse_date(cell("cell_issued_date")),
            valuation=_money(cell("cell_valuation")),
            contractor_name=cell("cell_contractor") or None,
            owner_name=cell("cell_owner") or None,
            raw={"permit_no": permit_no},
        )
