"""Normalization (build-spec §2, task 3).

Scrapers already emit canonical Permit objects; this is the last-mile cleanup
applied uniformly regardless of source: whitespace, obvious-null strings, and
address casing. Kept separate so source quirks don't leak scoring bias.
"""
from __future__ import annotations

import re

from .models import Permit

_NULLISH = {"", "n/a", "na", "none", "null", "-", "--"}


def _clean(s: str | None) -> str | None:
    if s is None:
        return None
    s = re.sub(r"\s+", " ", s).strip()
    return None if s.lower() in _NULLISH else s


def normalize(p: Permit) -> Permit:
    p.address = _clean(p.address) or ""
    p.jurisdiction = _clean(p.jurisdiction) or ""
    p.permit_type = _clean(p.permit_type) or ""
    p.description = _clean(p.description) or ""
    p.status = _clean(p.status) or ""
    p.contractor_name = _clean(p.contractor_name)
    p.owner_name = _clean(p.owner_name)
    return p
