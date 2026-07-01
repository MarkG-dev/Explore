# Berkshire Permit-Lead Pipeline (P1)

Minimal pipeline that turns public Berkshire County building permits into a
**scored lead digest** and a **simple dashboard**, split into two arms so the
[§9 double-blind lead-quality test](../research/permit-lead-p1-build-spec.md)
can measure whether *scored* leads convert better than *raw* ones.

This is P1 from the [build spec](../research/permit-lead-p1-build-spec.md).
It is deliberately **not** a CRM, product, or the "contractor OS" — just enough
to produce a trustworthy conversion number.

## What it does

```
scrape -> normalize -> classify (trade + adjacency) -> score (0-100 intent)
       -> store (SQLite) -> route to arms -> emit scored digest + raw list + dashboards
       -> capture won/lost -> readout (scored vs raw conversion + verdict)
```

- **Arm A (scored):** ranked, scored, adjacency-annotated, "why this lead matters."
- **Arm B (raw):** the *same permits* as a flat chronological list — the PermitGrab-style control.
- Only the *presentation* differs, so the experiment isolates scoring as the variable.

## Run it now (offline, no API key)

```bash
pip install -r requirements.txt
python -m pytest tests/ -q                       # end-to-end on fixtures
python -m permitlead.run_daily --source fixture --date 2026-07-01 --out out/
python -m permitlead.run_daily --db data/permits.db --analyze
```

`out/` gets `scored_<trade>.md`, `raw_<trade>.md`, and `dashboard_<contractor>.html`.

## Scrapers / sources

Each source in `config/sources.yaml` maps to an adapter (registry in
`scrape/__init__.py`). Adding a source = a config block, not Python:

| kind | adapter | use |
|---|---|---|
| `fixture` | FixtureScraper | offline demo/CI data |
| `permiteyes` | PermitEyesScraper | Berkshire portal (Playwright; selectors in config) |
| `socrata` | SocrataScraper | Cambridge/Somerville free open-data APIs |
| `ckan` | CkanScraper | Boston (Analyze Boston) free open-data API |

All API adapters share `httpclient.get` (retry/backoff; 4xx fails fast). The
row→Permit mapping for API sources is a config `field_map` (dataset column →
canonical field). See `research/ma-permit-data-sources.md` for the full MA
sourcing strategy (buy breadth, build the vendor-templated rest).

## Confirming a live source (the "confirm selectors/columns" step)

Run **where the network is open** — your machine or the GitHub Action (this
pipeline's sandbox egress policy blocks these hosts):

```bash
# API sources: prints real column names + flags any field_map that doesn't match
python -m permitlead.inspect_source cambridge --sample 3
# PermitEyes: prints each table's selector guess + header + sample row + forms
python -m permitlead.inspect_source permiteyes_berkshire
```
Paste the confirmed selectors/columns into `config/sources.yaml`, set the source
`enabled: true`, and run. From CI: **Actions → Permit-lead daily → Run workflow
→ source=…, mode=inspect**.

## Going live

1. **Confirm the source** with `inspect_source` (above); fill `config/sources.yaml`.
2. **Optional LLM.** `export ANTHROPIC_API_KEY=...` to use `claude-haiku-4-5` for
   classification; without it the deterministic **rules** classifier runs.
3. **Load contractors** — `python -m permitlead.seed_contractors` (from
   `config/contractors.csv`). Arm assignment / exclusivity is automatic.
4. **Schedule** `run_daily` daily (cron / GitHub Action). This box is ephemeral;
   nothing scheduled here survives.

## ⚠️ Compliance gates (build-spec §7 — not optional)

- **No contact enrichment / outreach code is included by design.** Owner contact
  storage is CCPA data-broker territory; outreach is TCPA/DNC territory. For the
  test, use only the owner name + address already on the public permit, and have
  the **contractor** contact the homeowner — not us — until legal review.
- Scrape politely: `rate_limit_seconds` + honest User-Agent are set in config.
  Don't remove them; don't hammer government portals.

## Layout

```
config/     scoring.yaml (weights/adjacency/keywords), sources.yaml (portals/selectors)
src/permitlead/
  scrape/   base.py (+ FixtureScraper), permiteyes.py, registry
  models.py db.py normalize.py classify.py score.py arms.py digest.py dashboard.py outcomes.py
  run_daily.py   # orchestrator / CLI
fixtures/   sample_permits.json (offline data)
tests/      test_pipeline.py (full chain on fixtures)
```
