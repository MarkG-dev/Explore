"""Intent scoring (build-spec §3, task 6).

Pure, explainable, config-driven. Given a Permit + the LLM-shaped classification
fields, produce a full Classification with a 0-100 intent_score that is a
weighted blend of five signals. Explainability matters: a contractor must trust
the score, and the test analysis must be able to say WHY a lead scored high.

`today` is injected (not read from the clock) so scoring is deterministic and
history can be re-scored as-of any date.
"""
from __future__ import annotations

import math
from datetime import date
from typing import Optional

from .models import Adjacency, Classification, Permit


def _freshness(reference: Optional[str], today: date, full_days: int,
               zero_days: int) -> tuple[float, Optional[int]]:
    """1.0 at <= full_days old, linear down to 0.0 at >= zero_days."""
    if not reference:
        return 0.3, None  # unknown date -> mild penalty, not zero
    try:
        ref = date.fromisoformat(reference)
    except ValueError:
        return 0.3, None
    age = (today - ref).days
    if age < 0:
        age = 0
    if age <= full_days:
        return 1.0, age
    if age >= zero_days:
        return 0.0, age
    return 1.0 - (age - full_days) / (zero_days - full_days), age


def _valuation_norm(value: Optional[float], floor: float, ceil: float) -> float:
    if not value or value <= floor:
        return 0.0
    if value >= ceil:
        return 1.0
    # log scale between floor and ceil
    return (math.log(value) - math.log(floor)) / (math.log(ceil) - math.log(floor))


def _adjacency_norm(adjacencies: list[Adjacency], bands: dict) -> float:
    if not adjacencies:
        return 0.0
    return max(bands.get(a.est_value_band, bands.get("unknown", 0.3))
               for a in adjacencies)


def score_permit(permit: Permit, primary_trade: str, adjacencies: list[Adjacency],
                 confidence: float, cfg: dict, today: date,
                 model: str = "rules") -> Classification:
    w = cfg["weights"]
    fresh_cfg, val_cfg = cfg["freshness"], cfg["valuation"]
    test_trades = set(cfg.get("test_trades", []))

    # 1. trade match: full only if it's a trade we can actually route in the test.
    if primary_trade in test_trades:
        trade_match = min(1.0, 0.6 + confidence * 0.4)
    elif primary_trade != "other":
        trade_match = 0.4          # real trade, but not one we test -> lower
    else:
        trade_match = 0.1

    # 2. adjacency value  3. freshness  4. owner-pull  5. valuation
    adjacency = _adjacency_norm(adjacencies, cfg.get("value_bands", {}))
    fresh, fresh_days = _freshness(permit.reference_date, today,
                                   fresh_cfg["full_days"], fresh_cfg["zero_days"])
    owner_pull = 1.0 if permit.owner_pull else 0.0
    valuation = _valuation_norm(permit.valuation, val_cfg["floor"], val_cfg["ceil"])

    raw = (w["trade_match"] * trade_match
           + w["adjacency_value"] * adjacency
           + w["freshness"] * fresh
           + w["owner_pull"] * owner_pull
           + w["valuation"] * valuation)
    intent_score = int(round(max(0.0, min(100.0, raw))))

    return Classification(
        permit_id=permit.id,
        primary_trade=primary_trade,
        adjacencies=adjacencies,
        intent_score=intent_score,
        freshness_days=fresh_days,
        confidence=confidence,
        model=model,
    )
