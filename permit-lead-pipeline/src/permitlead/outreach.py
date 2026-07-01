"""Tier B — outreach the CONTRACTOR sends themselves (compliant).

Renders email / SMS / postcard copy per lead from templates/mail/*.txt so the
copy lives in one place (shared with mailer.py). The contractor sends email/SMS
from their own number/email; postcards can be auto-mailed via a partner (see
mailer.py) since physical mail is TCPA-exempt. We are NEVER the sender to a
homeowner over phone/email — the sender guard enforces that.
"""
from __future__ import annotations

from . import mailer

SENDER = "contractor"  # DO NOT change to 'platform' for email/SMS (TCPA/CAN-SPAM)


def draft(lead: dict, contractor: dict) -> dict:
    """Return {email:{subject,body}, sms, postcard, mail_quote, channel_note}."""
    if SENDER != "contractor":
        raise ValueError("outreach SENDER must be 'contractor' (compliance)")

    ctx = mailer.context(lead, contractor)
    email_raw = mailer.render("email.txt", ctx)
    subject, _, body = email_raw.partition("\n")   # first line is the subject
    postcard = mailer.build_piece("postcard", lead, contractor)

    return {
        "email": {"subject": subject.strip(), "body": body.strip()},
        "sms": mailer.render("sms.txt", ctx).strip()[:320],
        "postcard": postcard.body.strip(),
        "mail_quote": mailer.DryRunProvider().quote(postcard),  # per-piece cost/price
        "channel_note": ("Send email/text from YOUR account. Postcards can be "
                         "auto-mailed for a small per-piece fee — we never "
                         "contact the homeowner over phone or email directly."),
    }
