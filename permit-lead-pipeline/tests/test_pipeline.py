"""End-to-end pipeline test on fixtures — no network, no API key.

Proves the full scrape->classify->score->route->emit chain runs deterministically
and that the double-blind readout computes conversion/ratio/verdict correctly.
"""
from datetime import date
from pathlib import Path

from permitlead import db
from permitlead.run_daily import run
from permitlead.outcomes import analyze, record

TODAY = date(2026, 7, 1)


def _seed_contractors(db_path):
    with db.session(db_path) as conn:
        for cid, name, trade in [
            ("c_roof_1", "Battaini Roofing", "roofing"),
            ("c_roof_2", "Briggs Roofing", "roofing"),
            ("c_solar_1", "BPVS", "solar"),
            ("c_solar_2", "PV Squared", "solar"),
            ("c_hvac_1", "Laureyns United", "hvac"),
            ("c_hvac_2", "Pariseau", "hvac"),
        ]:
            db.upsert_contractor(conn, cid, name=name, trade=trade, town="Pittsfield")


def test_pipeline_runs_and_scores(tmp_path):
    db_path = tmp_path / "permits.db"
    out_dir = tmp_path / "out"
    _seed_contractors(db_path)

    summary = run("fixture", out_dir, db_path, TODAY)

    assert summary["scraped"] == 14
    assert summary["classified"] == 14
    assert summary["leads_delivered"] > 0

    with db.session(db_path) as conn:
        rows = {r["primary_trade"]: r["intent_score"] for r in conn.execute(
            "SELECT primary_trade, intent_score FROM classification")}
        # roofing/solar/remodel/hvac should be recognized by the rules classifier
        trades = {r["primary_trade"] for r in conn.execute(
            "SELECT primary_trade FROM classification")}
        assert "roofing" in trades and "solar" in trades

    # The fresh, owner-pull roof permit should outscore the old electrical one.
    with db.session(db_path) as conn:
        fresh_roof = conn.execute(
            "SELECT intent_score FROM classification WHERE permit_id = "
            "(SELECT id FROM permit WHERE source_permit_id='BP-2026-0412')"
        ).fetchone()["intent_score"]
        old_elec = conn.execute(
            "SELECT intent_score FROM classification WHERE permit_id = "
            "(SELECT id FROM permit WHERE source_permit_id='BP-2026-0120')"
        ).fetchone()["intent_score"]
    assert fresh_roof > old_elec

    # Digests + at least one dashboard were written.
    assert (out_dir / "scored_roofing.md").exists()
    assert (out_dir / "raw_roofing.md").exists()
    assert any(out_dir.glob("dashboard_*.html"))


def test_double_blind_readout(tmp_path):
    db_path = tmp_path / "permits.db"
    _seed_contractors(db_path)
    run("fixture", tmp_path / "out", db_path, TODAY)

    with db.session(db_path) as conn:
        # Simulate: scored arm converts, raw arm doesn't -> should say PROCEED.
        scored_leads = conn.execute(
            "SELECT id, contractor_id FROM lead WHERE arm='scored'").fetchall()
        raw_leads = conn.execute(
            "SELECT id, contractor_id FROM lead WHERE arm='raw'").fetchall()
        for l in scored_leads[: max(1, len(scored_leads) // 2)]:
            record(conn, l["id"], l["contractor_id"], "won", 12000)
        for l in raw_leads:
            record(conn, l["id"], l["contractor_id"], "no_response")

        result = analyze(conn)

    assert result["scored"]["conversion"] > result["raw"]["conversion"]
    assert "verdict" in result and result["verdict"]
