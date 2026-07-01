"""Shared HTTP with polite retry/backoff (robustness — ma-permit-data-sources.md).

Government/open-data endpoints rate-limit and occasionally 5xx. One helper so
every scraper retries with exponential backoff, honors a truthful User-Agent,
and never hammers a source. 4xx (except 429) fail fast — retrying a 403/404 is
pointless (and, per our egress policy, forbidden for policy denials).
"""
from __future__ import annotations

import time
from typing import Optional

RETRYABLE = {429, 500, 502, 503, 504}


def get(url: str, *, params: Optional[dict] = None, headers: Optional[dict] = None,
        timeout: float = 30, retries: int = 4, backoff: float = 1.5):
    """GET with retry/backoff. Raises on non-retryable errors after exhausting."""
    import httpx

    last_exc = None
    for attempt in range(retries):
        try:
            resp = httpx.get(url, params=params, headers=headers,
                             timeout=timeout, follow_redirects=True)
            if resp.status_code in RETRYABLE:
                raise httpx.HTTPStatusError("retryable", request=resp.request,
                                            response=resp)
            resp.raise_for_status()
            return resp
        except Exception as exc:  # noqa: BLE001 - retry then re-raise
            last_exc = exc
            status = getattr(getattr(exc, "response", None), "status_code", None)
            if status is not None and status not in RETRYABLE:
                raise  # 403/404/etc. — fail fast, don't pound the source
            if attempt < retries - 1:
                time.sleep(backoff ** (attempt + 1))
    raise last_exc
