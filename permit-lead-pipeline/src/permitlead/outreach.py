"""Tier B — AI-drafted outreach the CONTRACTOR sends themselves (compliant).

We generate email / SMS / postcard copy per lead; the contractor sends it from
their own number, email, or letterhead. We are NEVER the sender to the
homeowner — that keeps us clear of TCPA (cold SMS) and CAN-SPAM exposure.
The `sender` guard below makes that non-negotiable in code.

Rules templates by default (deterministic, no key). If ANTHROPIC_API_KEY is set
and polish() is called, an LLM can rewrite for tone — still contractor-sent.
"""
from __future__ import annotations

_ADJ_HOOK = {
    "solar": "since the roof will be freshly done, it's the ideal moment to add solar",
    "hvac": "while the space is open is the cheapest time to upgrade the heating/cooling",
    "roofing": "we can take a quick look at the roof while permits are active",
    "remodel": "we can help with the finish work to tie the project together",
}


def _first_line(lead: dict) -> str:
    trade = lead.get("matched_trade", lead.get("primary_trade", "project"))
    hook = _ADJ_HOOK.get(trade, "we'd love to help with the next phase")
    return (f"I saw the permit for work at {lead.get('address','your property')} "
            f"in {lead.get('town','town')} — {hook}.")


def draft(lead: dict, contractor: dict) -> dict:
    """Return {email:{subject,body}, sms, postcard} — all contractor-sent."""
    if _sender_guard() != "contractor":  # defensive; config must keep this
        raise ValueError("outreach.sender must be 'contractor' (compliance)")

    name = contractor.get("name", "your local contractor")
    town = lead.get("town", "the area")
    owner = (lead.get("owner") or "there").split()[-1]
    line = _first_line(lead)

    email_body = (
        f"Hi {owner},\n\n{line}\n\nWe're a local {town}-area company and happy to "
        f"stop by, take a look, and give you a no-pressure quote whenever it's "
        f"convenient.\n\nBest,\n{name}"
    )
    sms = (f"Hi {owner}, {line} We're local — happy to give a free quote if useful. "
           f"— {name}")
    postcard = (f"NEIGHBOR — {line} Call {contractor.get('phone','us')} for a free, "
                f"no-pressure estimate. Local & licensed. — {name}")

    return {
        "email": {"subject": f"About your project at {lead.get('address','')}".strip(),
                  "body": email_body},
        "sms": sms[:320],
        "postcard": postcard,
        "channel_note": "Send from YOUR email/number. We never contact the homeowner directly.",
    }


def _sender_guard() -> str:
    # Kept as a function so a future config load can override, but defaults safe.
    return "contractor"
