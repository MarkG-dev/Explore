"""Scraper registry — maps a source's `kind` to its implementation."""
from __future__ import annotations

from .base import FixtureScraper, Scraper
from .permiteyes import PermitEyesScraper
from .socrata import SocrataScraper

_REGISTRY = {
    "fixture": FixtureScraper,
    "permiteyes": PermitEyesScraper,
    "socrata": SocrataScraper,          # free open-data feeds (Boston/Cambridge/Somerville)
    # "generic_table": GenericTableScraper,  # add when Pittsfield/OpenGov is live
}


def build_scraper(name: str, cfg: dict, http: dict | None = None) -> Scraper:
    kind = cfg.get("kind")
    if kind not in _REGISTRY:
        raise ValueError(f"unknown source kind {kind!r} for source {name!r}")
    return _REGISTRY[kind](name, cfg, http)
