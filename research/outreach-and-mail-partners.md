# AI Outreach Best Practices + Direct-Mail API Partners

> Backs the outreach features in `permit-lead-pipeline/` (`outreach.py`, `mailer.py`, `templates/mail/`). Prepared 2026-07-01. "~" = approximate/third-party-reported; confirm with the vendor. Practical guidance, not legal advice.

## Part A — Best practices for AI-drafted outreach

### What makes local contractor cold outreach convert
The core edge of a permit-triggered lead is **intent + timing** — the homeowner already declared they're doing work, so you catch demand rather than create it. Levers:
- **Speed relative to the permit.** Permits open a short window; homeowners collect bids immediately. Reach out fast; earlier wins. Align seasonal trades (HVAC, roofing) to the season.
- **Hyper-local trust.** The highest-performing home-services angle is the **"we just helped your neighbor at [street]"** mailer — reference a real nearby job/neighborhood, a local phone number, "licensed in [county]."
- **Real personalization, not just `{first_name}`.** Referencing the specific trigger event (the permit/project) reportedly lifts open rates ~40%+ over generic. Name the property, project type, town.
- **One low-pressure CTA.** Every extra ask lowers response. Single low-friction CTA ("reply with a good time" / "text YES for a free estimate"). A **large phone number** matters — still a phone-call business.
- **Length:** short. Email ~4 sentences; SMS 1–2 lines. Subject lines 4–8 words / ~21–40 chars, personalized, non-spammy.
- **Multi-channel + persistence:** mail + email + a compliant call/text lifts contact rates; most conversions take several touches. **Direct mail is the always-allowed backbone.**
- **Response rates:** prospecting direct mail ~2.7–4.4%; home-services postcards ~0.5–3% (roofing/HVAC ~1–3%, higher in-season) — well above cold email/paid search.

### Compliance guardrails (the reason our drafts are contractor-sent)
The **sender** carries the liability — which is exactly why we generate drafts but the contractor sends email/SMS, and why we auto-send only physical mail.

| Channel | Law | Rule the draft/flow must respect |
|---|---|---|
| **SMS / calls** | **TCPA** (+ CTIA, 10DLC) | Strictest — **prior express written consent before the first marketing text.** A permit is NOT consent. Cold-texting = $500–$1,500/message + class actions. **Do not auto-draft cold SMS to non-opted-in permit leads;** SMS only after they reply/opt in. Honor STOP; include brand + STOP/HELP. |
| **Email** | **CAN-SPAM** | Permissive — **no prior consent.** Needs accurate From/subject, honored opt-out (≤10 business days), and the **sender's valid physical postal address** in every email. |
| **Calls/texts** | **Fed + State DNC** | Scrub National + state DNC before any call/text; several states have stricter mini-TCPA statutes. |
| **Physical mail** | **Exempt from TCPA** | TCPA governs *telephone* media (calls/texts/faxes). Physical mail is outside it — **no consent needed.** The key reason direct mail is the safest cold channel. (Still subject to FTC truth-in-advertising; a 2025 CA rule restricts mailed *consumer-financial* solicitations — irrelevant to roofing/HVAC/solar, but check periodically.) |

**Net posture:** Direct mail = green light. Email = green light with CAN-SPAM footer (physical address + unsubscribe). SMS = opted-in only. These are baked into `outreach.py` (the `SENDER='contractor'` guard) and should be enforced in the draft generator so a non-compliant piece can't be sent.

### Template structures (merge fields)
Support: `{owner}` `{address}` `{street_name}` `{neighborhood}` `{city}` `{trade}` `{company}` `{rep_name}` `{phone}` `{email}` `{short_url}` `{offer}` `{license_no}` `{company_address}` `{date}`. (Our `templates/mail/*.txt` implement email/sms/postcard/letter; extend with `{license_no}`/`{company_address}` for the CAN-SPAM footer + local-proof lines.)

- **Email:** subject 4–8 words referencing trade+street; body 4 sentences (context → opportunity → how-you-help → single CTA); **CAN-SPAM footer** (company, physical address, unsubscribe).
- **SMS (opted-in only):** 1–2 lines, brand + STOP.
- **Postcard:** FRONT = one local-proof headline; BACK = owner/address, "we just did a job in {neighborhood}", single offer, **big phone number**, license + address.
- **Letter:** more room for a personal, trust-building note; same single CTA.

## Part B — Direct-mail API partners

| Provider | API / webhooks | Postcard (~/pc) | Letter (~/pc) | Minimums | Addr verify | Merge/templates | Billing |
|---|---|---|---|---|---|---|---|
| **Lob** | Best-in-class REST, strong docs, tracking **webhooks**, HTML templates | ~$0.48 PAYG → $0.55–0.75 | ~$0.69 | **None to start** | CASS, ~$0.04–0.06/lookup | Yes | **PAYG per-piece, credit card, no platform fee on entry tier**; ~$260–550/mo platform fee only at enterprise scale ⚠️ |
| **PostGrid** | Full REST, real-time tracking webhooks, no-code triggers | ~$0.50–0.75 ⚠️ | ~$0.55–0.80 ⚠️ | **None** | CASS **bundled free** | Yes | Pay-per-piece, no minimum; often lower monthly than Lob for smaller senders |
| **Click2Mail** | REST/Batch XML/SOAP, IMb tracking, CASS+NCOA | ~$0.64 retail; **EDDM ~$0.15–0.22 + postage** | ~$1.45 first sheet | **None** | CASS+NCOA | Yes (mail-merge) | PAYG, no monthly; **native USPS EDDM** |
| **Stannp** | REST, webhooks, campaign endpoints | Volume-tiered all-in ⚠️ | Volume-tiered ⚠️ | Free signup, pay per item | Included | Yes | PAYG per item, credit card |
| **PostcardMania** | API (agency-led), less dev-first | ~$0.18 **but** 5,000-pc min + $199+ setup | Quote | **High min (~5,000)** | Agency | Managed | Campaign quotes, not clean PAYG |

**USPS EDDM (saturation):** mail every address on selected carrier routes, **no list/NCOA**. ~$0.260/pc retail (~$0.242 commercial), 200-pc/route minimum, ~7–10 business days. No personalization (no `{owner}`) — a *complement* to targeted per-permit mail. Click2Mail + PostGrid support EDDM via API.

### Recommendation: **Lob primary, PostGrid fallback**
- **Lob:** best API + docs, delivery **webhooks** (surface mailed → in-transit → delivered back to the contractor), HTML templates mapping cleanly to our merge fields, **no minimum**, **PAYG credit-card billing** — matches "small per-piece fee on the contractor's card" without an early platform-fee commitment. Watch the ~$260–550/mo enterprise fee (only at high volume; negotiate before crossing).
- **PostGrid:** same PAYG/no-minimum posture, address verification **bundled free**, often cheaper monthly for smaller senders — the switch if Lob's platform fee bites below ~10k pieces/mo.
- **Click2Mail** if **EDDM saturation** becomes a core SKU. **Avoid PostcardMania** for self-serve (5,000-min + setup = agency engagement).

### Billing model (matches `mailer.PRICING`)
Your platform holds the mail-API account, calls send-per-approved-lead, and **marks up** the provider's per-piece cost (provider ~$0.48–0.75/postcard → bill the contractor's card ~$0.99–1.49). **Run address verification before charging** so contractors aren't billed for undeliverable pieces; surface the delivery **webhook** status in the UI. Keep EDDM as a separate "neighborhood blast" SKU priced off ~$0.24–0.26 postage + print. Charge via Stripe (a Supabase Edge Function on the `mailer` send path — see `backend-architecture-plan.md`).

*Sources: HBWeekly, CloudTalk, Glasshouse (outreach); MessageIQ, ActiveProspect, Infobip, VerticalResponse, TCPAWorld, PublicInput (TCPA/CAN-SPAM); Mailchimp, Mixmax, Autobound (copy); MailPro, LettrLabs, Upswell (direct-mail rates); DirectMail.io, Lob, PostGrid, Click2Mail, Stannp, PostcardMania (providers); CRST, MailPro (EDDM/postage). All per-piece dollar figures are third-party-reported (vendor pages 403'd) — confirm directly before setting margins.*
