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

## Going live

1. **Confirm selectors.** Open `permiteyes.us/berkshire/publicview.php` in a browser,
   inspect the results table, and paste the real CSS selectors into
   `config/sources.yaml` (the portal 403s bare HTTP, so the scraper uses Playwright).
2. **Optional LLM.** `export ANTHROPIC_API_KEY=...` to use `claude-haiku-4-5` for
   classification; without it the deterministic **rules** classifier runs.
3. **Load contractors** into the `contractor` table (name, trade, town) — arm
   assignment is automatic and stratified by trade.
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
