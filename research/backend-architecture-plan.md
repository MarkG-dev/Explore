# Backend Architecture — do we need Supabase, and how do we get "powerful" later?

**Short answer:** Not yet — but **yes, Supabase is the right next backend**, and the current design is deliberately built to migrate into it cleanly. Don't stand up a backend before the double-blind pilot proves the wedge; the moment it does, Supabase is the move.

---

## 1. Where we are now (and why it's correct for the pilot)

- **Data:** SQLite (`data/permits.db`) — one file, zero infra.
- **Delivery:** the pipeline exports a static `permitleads-data.json`; the app + sales site are static files on **Vercel**.
- **Compute:** a **GitHub Action** runs the pipeline daily and commits refreshed leads.

This is the right amount of backend for ≤~20 pilot contractors. It's free, fast, and has nothing to operate. Adding a database server now would be over-engineering ahead of validation (the handoff's whole point: prove lead quality first, build the machine second).

**Its limits — the triggers to graduate:**
| Need | Static JSON can't do it |
|---|---|
| Contractor **logins / accounts** | no auth |
| Each contractor sees **only their** exclusive leads | JSON is public to anyone with the URL |
| **Live** won/lost writes from many users | JSON is read-only; localStorage doesn't aggregate |
| **Billing** (subscriptions, per-postcard charges) | none |
| **Sending** mail/alerts at scale on a schedule | no server-side actions |

When you hit those — right after the pilot validates — you migrate.

---

## 2. Target: Supabase (recommended)

Supabase is Postgres plus the exact primitives this product needs, in one managed platform:

- **Postgres** — real relational DB; our SQLite schema (`permit`, `classification`, `contractor`, `lead`, `outcome`, `contact`) maps over almost 1:1.
- **Auth** — contractor accounts (magic-link/email) without building auth yourself.
- **Row-Level Security (RLS)** — *the killer feature here.* A policy makes each contractor able to read **only their own** leads. That's precisely the "exclusive, private per contractor" requirement — enforced in the database, not hoped for in the app.
- **Edge Functions** — server-side actions: call the **Lob** mail API, send **alert emails** (Resend/Postmark), handle **Stripe** webhooks.
- **Storage** — postcard PDFs, CSV exports.
- **Realtime** — live dashboard updates when a lead lands or a status changes.
- Generous free tier, scales up, first-class **Vercel** integration.

**Why not the alternatives:**
- *Firebase* — NoSQL; awkward for relational lead/outcome data and reporting.
- *Neon / PlanetScale* — great Postgres/MySQL, but DB-only: you'd still bolt on auth, RLS-equivalent, functions, storage.
- *Raw Postgres + your own API* — most control, most work; not worth it for a small team.
- Supabase gives ~80% of a custom backend for ~20% of the effort.

---

## 3. Target architecture

```
  INGESTION (the pipeline)          SUPABASE (backend)                 FRONT-END (Vercel)
  ┌───────────────────────┐        ┌────────────────────────┐        ┌────────────────────┐
  │ scrapers + bought APIs │──write▶│ Postgres               │◀─read──│ contractor portal  │
  │ normalize→classify→score│       │  permits/leads/outcomes │  (RLS) │ (Next.js or static)│
  │ exclusivity assignment  │       │ Auth (contractor login) │        │ sales site         │
  │ (GH Action → worker)    │       │ RLS: see only your leads│───────▶│ won/lost writes    │
  └───────────────────────┘        │ Edge Functions:         │        └────────────────────┘
                                    │  • Lob mail send        │
                                    │  • alert emails (Resend)│
                                    │  • Stripe billing       │
                                    │ Storage (postcard PDFs) │
                                    └────────────────────────┘
```

Ingestion stays **decoupled** from the app — it just writes rows. The app never scrapes; it reads Postgres through RLS. This is what makes it "powerful" without being fragile.

---

## 4. Migration path (each phase ships independently)

- **Phase 0 — now (done):** SQLite + static JSON + GH Action. Run the pilot.
- **Phase 1 — stand up Supabase:** port the schema (the `db.py` DDL becomes a Postgres migration). Point the pipeline at Supabase via the Python client instead of SQLite. *Small, mechanical change — the models/logic don't move.*
- **Phase 2 — auth + RLS in the app:** contractors log in; RLS policy `lead.contractor_id = auth.uid()` guarantees isolation; won/lost writes go straight to the DB. Retire the public JSON.
- **Phase 3 — server actions:** Edge Functions for **Lob** postcards (already scaffolded in `mailer.py`), **alert emails** (already modeled in `alerts.py`), and **Stripe** for subscriptions + per-postcard charges (the `mailer.PRICING` margin model).
- **Phase 4 — scale ingestion:** move the pipeline off GitHub Actions to a small worker (Railway/Fly/Supabase Cron) once you're driving a **Playwright fleet** across many municipal portals (a cron alone won't hold that).

Everything already written — models, scoring, exclusivity, drafts, mailer — carries forward unchanged. Only the *storage adapter* and *who-runs-it* change.

---

## 5. RLS sketch (the isolation guarantee)

```sql
-- each contractor row links to an auth user
alter table contractor add column auth_uid uuid references auth.users;

alter table lead enable row level security;
create policy "own leads" on lead for select
  using ( contractor_id in (
    select id from contractor where auth_uid = auth.uid() ) );
```
A contractor querying `lead` physically cannot read another's rows. That's how "exclusive" becomes a security property, not a promise.

---

## 6. Where MA permit data comes from (ingestion breadth)

The backend is only as good as what feeds it. MA has **no single statewide permit feed** — it's municipal, across several permitting systems, plus a few big-city open-data sets and commercial aggregators. The concrete source list, coverage, and buy-vs-scrape strategy live in **`ma-permit-data-sources.md`** (companion research). The pipeline's per-source adapter design (`scrape/` registry + config-driven selectors + stable-ID upserts) is built exactly so new MA sources drop in without touching the core.

**Robustness principles already in place / planned:**
- Per-source adapters behind a registry (`scrape/__init__.py`) — a broken portal can't take down the others.
- **Idempotent upserts** on stable IDs (`models.stable_id`) — safe to re-run; no dupes.
- **Buy breadth, scrape the tail:** license an API (e.g. Shovels) for wide coverage, scrape only what it misses (see the MA sources doc).
- Dead-source detection (a source returning 0 rows N days running → alert), and schema-versioned `raw` JSON so anything can be reprocessed.
