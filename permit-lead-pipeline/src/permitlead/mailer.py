"""Direct-mail sending scaffold (placeholder for a print-and-mail partner).

Physical mail is the ONE outreach channel we can automate and send ourselves
without TCPA exposure. The plan: a partner (Lob / PostGrid / Click2Mail) prints
and mails a postcard/letter to the permit address via API; the contractor pays a
small per-piece fee by card (our cost + a markup) through a billing provider.

This module is a SAFE SCAFFOLD:
  - Templates render from templates/mail/*.txt (merge fields).
  - The default provider is DryRun — it NEVER sends; it returns what *would* be
    sent + the estimated cost. No mail goes out until a real provider + key are
    configured AND send is explicitly enabled.
  - Real providers (LobProvider) are stubbed with the exact API shape to fill in.

Nothing here charges a card or mails anything yet. Wire a provider + Stripe when
you're ready; see PRICING below.
"""
from __future__ import annotations

import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parents[2] / "templates" / "mail"

# Per-piece economics (placeholder — confirm against the partner's live rates).
# We charge the contractor cost + markup; the delta is our revenue on mail.
PRICING = {
    "postcard": {"partner_cost_usd": 0.73, "price_to_contractor_usd": 1.25},
    "letter":   {"partner_cost_usd": 1.10, "price_to_contractor_usd": 1.75},
}


@dataclass
class MailPiece:
    kind: str          # 'postcard' | 'letter'
    to_name: str
    to_address: str    # the permit property address
    to_town: str
    body: str
    front: str = ""    # postcard headline side
    from_name: str = ""      # the CONTRACTOR (return address / signer)
    from_phone: str = ""


# Natural-language hook per trade (reads well mid-sentence in the templates).
HOOKS = {
    "solar": "since the roof will be freshly done, it's the ideal moment to add solar",
    "hvac": "while the space is open is the cheapest time to upgrade the heating and cooling",
    "roofing": "we can take a quick look at the roof while the project is active",
    "remodel": "we can help with the finish work to tie the whole project together",
}


def render(template_name: str, ctx: dict) -> str:
    """Fill {{merge}} fields in a template file. Missing fields -> empty."""
    text = (TEMPLATES / template_name).read_text()
    return re.sub(r"{{\s*(\w+)\s*}}", lambda m: str(ctx.get(m.group(1), "")), text)


def context(lead: dict, contractor: dict) -> dict:
    """Shared merge context for BOTH contractor-sent drafts and mail pieces."""
    trade = lead.get("matched_trade", lead.get("primary_trade", ""))
    return {
        "owner": (lead.get("owner") or "there").split()[-1],
        "owner_full": lead.get("owner") or "Neighbor",
        "address": lead.get("address", ""),
        "town": lead.get("town", ""),
        "trade": trade,
        "hook": HOOKS.get(trade, "we'd love to help with the next phase of your project"),
        "contractor_name": contractor.get("name", ""),
        "contractor_phone": contractor.get("phone", ""),
    }


def build_piece(kind: str, lead: dict, contractor: dict) -> MailPiece:
    ctx = context(lead, contractor)
    if kind == "postcard":
        return MailPiece("postcard", ctx["owner_full"], ctx["address"], ctx["town"],
                         body=render("postcard_back.txt", ctx),
                         front=render("postcard_front.txt", ctx),
                         from_name=ctx["contractor_name"], from_phone=ctx["contractor_phone"])
    return MailPiece("letter", ctx["owner_full"], ctx["address"], ctx["town"],
                     body=render("letter.txt", ctx),
                     from_name=ctx["contractor_name"], from_phone=ctx["contractor_phone"])


class MailProvider(ABC):
    name = "abstract"

    @abstractmethod
    def send(self, piece: MailPiece) -> dict:
        ...

    def quote(self, piece: MailPiece) -> dict:
        p = PRICING.get(piece.kind, PRICING["postcard"])
        return {"kind": piece.kind, **p,
                "our_margin_usd": round(p["price_to_contractor_usd"] - p["partner_cost_usd"], 2)}


class DryRunProvider(MailProvider):
    """Default. Renders + quotes, sends NOTHING. Safe for CI and demos."""
    name = "dryrun"

    def send(self, piece: MailPiece) -> dict:
        return {"provider": self.name, "status": "not_sent (dry run)",
                "quote": self.quote(piece), "preview": {
                    "to": f"{piece.to_name}, {piece.to_address}, {piece.to_town}",
                    "from": piece.from_name, "front": piece.front, "body": piece.body}}


class LobProvider(MailProvider):
    """STUB for Lob (lob.com). Fill in the real API call when going live.

    Needs LOB_API_KEY. Address verification + template merge are Lob features;
    map MailPiece -> Lob postcard/letter payload. Left un-sent on purpose.
    """
    name = "lob"

    def __init__(self) -> None:
        self.key = os.environ.get("LOB_API_KEY")

    def send(self, piece: MailPiece) -> dict:
        if not self.key:
            return {"provider": self.name, "status": "error: LOB_API_KEY not set"}
        # --- TODO(go-live): real Lob call, e.g.:
        # import httpx
        # httpx.post("https://api.lob.com/v1/postcards", auth=(self.key, ""), data={...})
        return {"provider": self.name, "status": "stub: not wired",
                "quote": self.quote(piece)}


def get_provider() -> MailProvider:
    """Never returns a live sender unless explicitly enabled AND configured."""
    want = os.environ.get("MAIL_PROVIDER", "dryrun").lower()
    enabled = os.environ.get("MAIL_SEND_ENABLED") == "1"
    if want == "lob" and enabled:
        return LobProvider()
    return DryRunProvider()
