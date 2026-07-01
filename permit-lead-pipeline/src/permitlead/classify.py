"""Trade + adjacency classification (build-spec §3, task 5).

Returns the LLM-shaped fields only: primary_trade, adjacencies, confidence.
The final intent_score is computed by score.py from these fields PLUS structured
permit fields — the LLM never sets the score directly (keeps it auditable/cheap
to re-tune, per build-spec §3).

Two backends:
  - AnthropicClassifier: real classification (default model claude-haiku-4-5).
  - RulesClassifier:      keyword + adjacency-map fallback. Deterministic, no
                          network, no key. Lets the whole pipeline run in CI.

get_classifier() auto-selects: Anthropic if ANTHROPIC_API_KEY and the sdk are
present, else rules. This is why tests are deterministic and offline.
"""
from __future__ import annotations

import json
import os
from typing import Optional

from .models import Adjacency, Permit

CLASSIFY_MODEL = os.environ.get("PERMITLEAD_MODEL", "claude-haiku-4-5")

_PROMPT = """You classify a US building permit for a contractor lead-gen pilot.
Return STRICT JSON only, no prose:
{{"primary_trade": "<one of: roofing|solar|hvac|remodel|pool|electrical|plumbing|new_construction|other>",
  "adjacencies": [{{"trade": "<trade>", "rationale": "<short>", "est_value_band": "<0-5k|5-10k|10-20k|20k+|unknown>"}}],
  "confidence": <0..1>}}

Permit:
  type: {permit_type}
  description: {description}
  jurisdiction: {jurisdiction}
  valuation: {valuation}
  contractor_listed: {contractor}
"""


class RulesClassifier:
    """Keyword match against scoring.yaml trade_keywords + adjacency map."""

    model = "rules"

    def __init__(self, cfg: dict) -> None:
        self.keywords = cfg.get("trade_keywords", {})
        self.adjacencies = cfg.get("adjacencies", {})

    def classify(self, permit: Permit) -> tuple[str, list[Adjacency], float]:
        text = f"{permit.permit_type} {permit.description}".lower()
        best_trade, best_hits = "other", 0
        for trade, words in self.keywords.items():
            hits = sum(1 for w in words if w in text)
            if hits > best_hits:
                best_trade, best_hits = trade, hits
        adj = [
            Adjacency(trade=a["trade"],
                      rationale=f"{best_trade} permit -> {a['trade']} opportunity",
                      est_value_band=a.get("est_value_band", "unknown"))
            for a in self.adjacencies.get(best_trade, [])
        ]
        # Confidence scales with keyword evidence; capped so rules never look sure.
        confidence = 0.0 if best_hits == 0 else min(0.4 + 0.2 * best_hits, 0.85)
        return best_trade, adj, confidence


class AnthropicClassifier:
    model = CLASSIFY_MODEL

    def __init__(self, cfg: dict) -> None:
        import anthropic  # local import; only needed on this path
        self.client = anthropic.Anthropic()
        self.adjacencies = cfg.get("adjacencies", {})

    def classify(self, permit: Permit) -> tuple[str, list[Adjacency], float]:
        prompt = _PROMPT.format(
            permit_type=permit.permit_type, description=permit.description,
            jurisdiction=permit.jurisdiction, valuation=permit.valuation,
            contractor=permit.contractor_name or "NONE",
        )
        msg = self.client.messages.create(
            model=self.model, max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        data = _extract_json(msg.content[0].text)
        adj = [Adjacency(trade=a.get("trade", ""), rationale=a.get("rationale", ""),
                         est_value_band=a.get("est_value_band", "unknown"))
               for a in data.get("adjacencies", [])]
        return data.get("primary_trade", "other"), adj, float(data.get("confidence", 0.5))


def _extract_json(text: str) -> dict:
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        return {}
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return {}


def get_classifier(cfg: dict) -> object:
    """Anthropic if usable, else deterministic rules. Never raises on missing key."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            return AnthropicClassifier(cfg)
        except Exception as exc:  # missing sdk, bad key at init, etc.
            print(f"[classify] falling back to rules ({exc})")
    return RulesClassifier(cfg)
