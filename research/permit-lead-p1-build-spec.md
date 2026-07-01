# P1 Build Spec — Berkshires Permit-Lead Pipeline + Double-Blind Test Harness

> **Companion to:** `permit-lead-intelligence-handoff.md`. That doc decided *what* and *why* (GO-WITH-CHANGES; the wedge is intent-scored leads; the one experiment that matters is the §9 four-week double-blind lead-quality test). **This doc is the *how*** — a buildable spec for P1 (weeks 1–3) so the double-blind test can start.
>
> **Scope discipline:** Build the *minimum* that lets the double-blind test produce a trustworthy conversion number. Not a CRM. Not a product. Not the OS. The handoff's §7 "hard correction" applies: resist scope creep toward workflow.
>
> **Status:** Spec / not yet built. No live scraping or contact enrichment has been performed. Two items below are **gated on explicit human go-ahead** before any code touches real data (see §7 Compliance Gates).

---

## 0. What P1 must produce (definition of done)

A daily run that, for Berkshire County MA, turns raw public permits into a **scored lead digest** and a **simple dashboard**, split cleanly into two arms so the double-blind test can measure whether the *scored* arm converts better than the *raw* arm.

Concretely, at the end of P1 we can, every morning:
1. Pull new/updated permits from PermitEyes (`permiteyes.us/berkshire`) + Pittsfield's portal.
2. Normalize them into one schema.
3. Classify each: trade, adjacent-trade opportunities, intent score, freshness.
4. Enrich owner contact (email-first) — **gated, see §7**.
5. Emit **two** outputs from the same underlying permits:
   - **Arm A (scored):** ranked, scored, adjacency-annotated, enriched digest + dashboard.
   - **Arm B (raw):** the same permits as a flat list (address, type, date, owner) — no score, no ranking, no adjacency. This is the PermitGrab-style control.
6. Log every lead with a stable ID so contractors' won/lost feedback ties back to arm + score.

---

## 1. Architecture (minimal, boring on purpose)

```
                 ┌─────────────┐
  PermitEyes ───▶│  Scrapers   │──┐
  Pittsfield ───▶│ (per-source)│  │   raw HTML/rows
                 └─────────────┘  ▼
                            ┌───────────┐
                            │ Normalize │  → Permit (canonical schema)
                            └───────────┘
                                  │
                            ┌───────────┐
                            │  Classify │  → trade, adjacencies, intent_score, freshness
                            │  (LLM +   │
                            │  rules)   │
                            └───────────┘
                                  │
                            ┌───────────┐
                            │  Enrich   │  → owner email/phone (GATED)
                            └───────────┘
                                  │
                            ┌───────────┐
                            │  Store    │  → SQLite (leads, scores, arms, outcomes)
                            └───────────┘
                              │        │
                    ┌─────────┘        └─────────┐
              ┌───────────┐              ┌──────────────┐
              │  Digest   │              │  Dashboard   │
              │ (email/MD)│              │ (static HTML)│
              └───────────┘              └──────────────┘
```

**Stack (chosen for speed, not scale):**
- **Language:** Python 3.11.
- **Scrape:** `httpx` + `selectolax`/`BeautifulSoup` for static HTML; Playwright (already installed in this env at `/opt/pw-browsers/chromium`) only if a portal is JS-rendered. Prefer the lightest thing that works.
- **Store:** SQLite (single file, `data/permits.db`). Zero infra. Migrate to Postgres only if P2 needs multi-user.
- **Classify:** Claude via the Anthropic API. Model default: **`claude-haiku-4-5`** for per-permit classification (cheap, high volume), escalate to `claude-sonnet-5` only for ambiguous cases. ~600–900 permits/yr → volume is trivially small; cost is a rounding error.
- **Digest:** render Markdown → HTML email (or just a shared Markdown/HTML file for the trial).
- **Dashboard:** static HTML generated from SQLite (no server needed for the trial; can be a single-page file per contractor).
- **Schedule:** one cron/GitHub Action daily. No queue, no workers.

**Non-goals for P1:** auth, multi-tenant, billing, real CRM, mobile, national coverage, offline-jurisdiction scraping.

---

## 2. Canonical data model

```
Permit
  id                TEXT  PK   # stable: sha1(source + source_permit_id)
  source            TEXT       # 'permiteyes_berkshire' | 'pittsfield'
  source_permit_id  TEXT
  jurisdiction      TEXT       # town/city
  address           TEXT
  parcel_id         TEXT NULL
  permit_type       TEXT       # raw source label
  description       TEXT       # free-text work description
  status            TEXT       # applied / issued / etc.
  applied_date      DATE NULL
  issued_date       DATE NULL
  valuation         REAL NULL  # declared job value if present
  contractor_name   TEXT NULL  # NULL/blank = possible owner-pull (direct lead signal)
  owner_name        TEXT NULL
  raw               JSON       # full original row, for reprocessing
  first_seen        TIMESTAMP
  last_seen         TIMESTAMP

Classification            # 1:1 with Permit (latest)
  permit_id         FK
  primary_trade     TEXT       # roofing/solar/hvac/pool/remodel/electrical/...
  adjacencies       JSON       # [{trade, rationale, est_value_band}]
  intent_score      INTEGER    # 0-100, see §3
  freshness_days    INTEGER    # today - (issued_date or applied_date)
  model             TEXT       # which model produced this
  classified_at     TIMESTAMP

Lead                      # a permit surfaced to a contractor, per arm
  id                TEXT PK
  permit_id         FK
  arm               TEXT       # 'scored' | 'raw'
  trade_bucket      TEXT       # the trade this lead was routed to
  contractor_id     FK NULL    # who received it (test participant)
  delivered_at      TIMESTAMP

Contact                   # GATED enrichment output
  permit_id         FK
  email             TEXT NULL
  phone             TEXT NULL
  contact_type      TEXT       # owner / contractor
  source            TEXT       # how obtained
  confidence        REAL

Outcome                   # the won/lost loop — the proprietary data asset (handoff §7.2)
  lead_id           FK
  contractor_id     FK
  status            TEXT       # contacted / quoted / won / lost / no_response
  job_value         REAL NULL
  noted_at          TIMESTAMP
```

The `Outcome` table is deliberately present in P1 even though the loop's *moat* value is 2–3 years out (handoff §8.3). We capture it from day one because it is (a) the double-blind test's primary metric and (b) un-recreatable if not logged from the start.

---

## 3. Intent scoring (the wedge — what Arm A has and Arm B doesn't)

The scored arm's edge is turning a permit row into *"this is a $X job for trade Y, here's why, here's the owner."* Scoring is deliberately explainable — a contractor must trust it, and we must be able to audit why a lead scored high when we analyze the test.

**`intent_score` (0–100)** = weighted blend of:

| Signal | Weight | Rationale |
|---|---|---|
| Trade-match strength | 30 | Does the permit's work clearly map to a trade we're testing? |
| Adjacency value | 25 | Fan-out potential (roof→solar/gutter). Est. $ band of the adjacent job. |
| Freshness | 20 | Decays with age; a stale permit is worthless (handoff §8.7). Full at ≤7d, ~0 by ~60d. |
| Owner-pull signal | 15 | `contractor_name` blank → homeowner may need a pro = hotter direct lead. |
| Valuation / project size | 10 | Bigger declared value → bigger adjacent opportunity (when present). |

Weights are **config, not code** (`config/scoring.yaml`) so we can tune without redeploy — and so the test analysis can re-score historically.

**Adjacency map** (seed from handoff §3, encode as data):
```
roofing      → [solar, gutters, skylights, insulation]
pool         → [fencing, landscaping, decking, solar_heating]
kitchen/addn → [flooring, countertops, hvac, electrical, paint]
new_const    → [landscaping, security, window_treatments, pest, moving]
(no contractor listed) → direct homeowner lead
```

**Classifier prompt contract** (LLM returns strict JSON, validated):
```json
{
  "primary_trade": "roofing",
  "adjacencies": [
    {"trade": "solar", "rationale": "full roof replacement is prime solar timing", "est_value_band": "10-20k"}
  ],
  "owner_pull": true,
  "confidence": 0.82
}
```
Rules layer computes freshness + final `intent_score` from the LLM fields + structured permit fields. **LLM never sets the final score directly** — keeps it auditable and cheap to re-tune.

---

## 4. The double-blind test harness (§9 — the whole ballgame)

This is the reason P1 exists. Design it so the result is *defensible*, not just directional.

- **Participants:** ~20 contractors, 2–3 trades (roofing, solar, HVAC/remodel).
- **Assignment:** randomize contractor → arm (`scored` | `raw`), stratified by trade so each arm has comparable trade mix. Store assignment; never let a contractor see the other arm.
- **Same underlying permits, different presentation.** Both arms draw from the identical permit pool for the contractor's trade+geo. Arm A adds score/rank/adjacency/enrichment; Arm B is a flat chronological list. This isolates *scoring* as the variable — not coverage, not freshness (both arms same freshness).
- **Primary metric:** conversion = booked job / leads delivered, measured at week 4.
- **Feedback capture:** dead-simple. Each delivered lead gets a one-click `won / lost / no-response` control (email buttons or a one-field form). This *is* the `Outcome` table.
- **Decision gates (from handoff §9):**
  - **≥2× (scored vs raw)** → real wedge, proceed to P2.
  - **~1.3×** → lifestyle business at best.
  - **~1×** → kill.
- **Guardrails against fooling ourselves:**
  - Pre-register the metric + gate *before* looking at data.
  - Track leads-delivered per arm (equal volume, or normalize).
  - Watch for confounds: contractor effort differences, trade seasonality (handoff §8.8), owner≠buyer (§8.4). Log enough to spot them.
  - N≈20 is underpowered for statistical significance — treat the result as a **strong directional signal**, and say so. A 2× effect at N=20 is decision-grade; a 1.3× is noise. Don't over-claim.

---

## 5. Task breakdown (buildable units, roughly ordered)

**Week 1 — data in.**
1. `scrape/permiteyes.py` — pull Berkshire permits; handle pagination; idempotent upsert by `source_permit_id`. Respect robots.txt + rate-limit politely.
2. `scrape/pittsfield.py` — same for Pittsfield's portal (note: Pittsfield migrating PermitEyes→OpenGov mid-2025, handoff §8.6 — build the scraper against whatever is live *now*, isolate source-specific code).
3. `normalize.py` — raw rows → `Permit` schema; SQLite upsert; `first_seen`/`last_seen` tracking.
4. Backfill last ~90 days so the test has volume from day one.

**Week 2 — scoring.**
5. `classify.py` — LLM call per new permit → `Classification`; strict-JSON validation + retry; batch to control cost.
6. `score.py` — rules layer: freshness + weighted blend from `config/scoring.yaml`.
7. `config/scoring.yaml` + adjacency map as data.
8. Spot-check harness: sample 30 permits, eyeball classifications, tune prompt/weights.

**Week 3 — outputs + test rig.**
9. `arms.py` — assign contractors to arms; route leads by trade+geo; write `Lead` rows.
10. `digest.py` — render Arm A (scored) and Arm B (raw) outputs.
11. `dashboard.py` — static HTML per contractor from SQLite.
12. `outcomes.py` — capture won/lost/no-response → `Outcome`.
13. `run_daily.py` — orchestrate scrape→normalize→classify→score→enrich→emit; one cron entry.
14. Pre-register the test doc (metric, gates, arm assignments).

**Gated (do NOT start without §7 go-ahead):**
15. `enrich.py` — owner email/phone. Needs the compliance review first.
16. Any real outbound contact to homeowners.

---

## 6. Cost & effort

- **Infra + LLM + enrichment:** ~$100–300/mo (matches handoff §9). LLM classification of ~600–900 permits/yr is <$5/mo; enrichment + any paid data is the bulk.
- **Build effort:** ~2–3 focused weeks for one engineer to reach "daily digest + dashboard + outcome capture." The double-blind runs 4 weeks on top.
- **Total to a kill/go decision:** ~$1–2k, ~4–12 weeks (matches handoff §9).

---

## 7. Compliance gates (blocking — read before writing enrichment/outreach code)

The handoff's §8.5 is not optional and I will not silently code past it:

1. **Contact enrichment & storage** → CCPA data-broker territory. The handoff flags a ~$2–5k legal review *before taking customers*. For the **test**, prefer using **only the owner name + address already on the public permit**, and email-first outreach the contractor makes themselves, to minimize our data-broker exposure. Building `enrich.py` to accumulate a contact database is **gated on human sign-off**.
2. **Outbound contact (TCPA / Do-Not-Call)** → business numbers mostly exempt, hybrid numbers aren't. In the test, **the contractor contacts the homeowner**, not us — we surface the lead. Keep it that way until legal review says otherwise.
3. **Scraping ToS / rate limits** → PermitEyes/Pittsfield are public portals, but scrape politely (rate-limit, identify, cache) and check each portal's terms. Don't hammer government infrastructure.

**Recommendation:** build steps 1–14 (which touch only public permit data and contractor-facing outputs) now; hold 15–16 until you explicitly approve the compliance posture.

---

## 8. Open decisions I need from you before building

1. **Go-ahead to build steps 1–14** (public-data pipeline + test rig), holding enrichment/outreach (15–16) for compliance sign-off?
2. **Language/stack** — Python + SQLite as specced, or do you have a preference (e.g. Node, or a hosted DB you already use)?
3. **Where should the daily job run** — a GitHub Action on this repo, or your own box? (This env is ephemeral; nothing scheduled here survives.)
4. **Do you actually have the ~20 Berkshires contractors** to recruit, or is finding them part of the job? (Handoff §9.4: "hire for distribution, not engineering" — the trial is worthless without participants.)
5. **Enrichment posture** — comfortable minimizing to public-permit fields for the test, or do you want the full enrichment path (and its legal review) now?
```
