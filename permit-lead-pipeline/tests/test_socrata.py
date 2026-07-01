"""Socrata row->Permit mapping is pure and offline-testable (no network)."""
from permitlead.scrape.socrata import row_to_permit, _iso

FMAP = {
    "permit_id": "permitnumber", "address": "address",
    "permit_type": "permittypedescr", "status": "status",
    "applied_date": "applicationdate", "issued_date": "issueddate",
    "valuation": "totalprojectcost",
}

ROW = {
    "permitnumber": "BLDG-2026-001",
    "address": "10 Main St",
    "permittypedescr": "Solar PV",
    "status": "Issued",
    "applicationdate": "2026-06-01T00:00:00.000",
    "issueddate": "2026-06-05T00:00:00.000",
    "totalprojectcost": "24000",
}


def test_maps_fields_and_parses_dates():
    p = row_to_permit(ROW, "cambridge", FMAP, "Cambridge")
    assert p.source_permit_id == "BLDG-2026-001"
    assert p.jurisdiction == "Cambridge"
    assert p.address == "10 Main St"
    assert p.permit_type == "Solar PV"
    assert p.issued_date == "2026-06-05"
    assert p.applied_date == "2026-06-01"
    assert p.valuation == 24000.0
    assert p.raw is ROW  # original preserved for reprocessing


def test_row_without_permit_id_is_skipped():
    assert row_to_permit({"address": "x"}, "cambridge", FMAP, "Cambridge") is None


def test_iso_handles_socrata_and_plain_dates():
    assert _iso("2026-06-05T00:00:00.000") == "2026-06-05"
    assert _iso("06/05/2026") == "2026-06-05"
    assert _iso("") is None
