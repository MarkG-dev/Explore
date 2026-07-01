"""Outcome capture + the double-blind readout (build-spec §4, task 12 + §4 gates).

record() writes a won/lost/no_response outcome. analyze() computes the metric
that decides everything: conversion (booked job / leads delivered) per arm, and
the scored-vs-raw ratio against the pre-registered gates:
  >= 2.0x  -> real wedge, proceed        (handoff §9)
  ~1.3x    -> lifestyle business at best
  ~1.0x    -> kill
N is small (~20 contractors), so this is a DIRECTIONAL signal, not a p-value —
analyze() says so in its verdict rather than over-claiming significance.
"""
from __future__ import annotations

from .db import record_outcome

WON = "won"


def record(conn, lead_id: str, contractor_id: str, status: str,
           job_value: float | None = None) -> None:
    record_outcome(conn, lead_id, contractor_id, status, job_value)


def _conversion(conn, arm: str) -> tuple[int, int, float]:
    delivered = conn.execute(
        "SELECT COUNT(*) n FROM lead WHERE arm = ?", (arm,)
    ).fetchone()["n"]
    won = conn.execute(
        """SELECT COUNT(DISTINCT o.lead_id) n
           FROM outcome o JOIN lead l ON l.id = o.lead_id
           WHERE l.arm = ? AND o.status = ?""",
        (arm, WON),
    ).fetchone()["n"]
    rate = (won / delivered) if delivered else 0.0
    return delivered, won, rate


def analyze(conn) -> dict:
    d_s, w_s, r_s = _conversion(conn, "scored")
    d_r, w_r, r_r = _conversion(conn, "raw")

    # Both arms must actually have delivered leads or there's nothing to compare.
    # (A degenerate run where one arm got zero leads is NOT a result.)
    if d_s == 0 or d_r == 0:
        ratio = None
        verdict = "INSUFFICIENT DATA — both arms need delivered leads to compare"
    else:
        ratio = (r_s / r_r) if r_r else (float("inf") if r_s else 0.0)
        if ratio == float("inf") or ratio >= 2.0:
            verdict = "PROCEED — scored ≥2x raw (real wedge)"
        elif ratio >= 1.3:
            verdict = "LIFESTYLE — ~1.3x, marginal edge at best"
        else:
            verdict = "KILL — ~1x, scoring adds no conversion lift"
        ratio = round(ratio, 2) if ratio != float("inf") else None

    return {
        "scored": {"delivered": d_s, "won": w_s, "conversion": round(r_s, 4)},
        "raw": {"delivered": d_r, "won": w_r, "conversion": round(r_r, 4)},
        "ratio": ratio,
        "verdict": verdict,
        "caveat": "N is small; treat as a directional signal, not a significance test.",
    }
