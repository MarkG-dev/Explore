"""Tests for exclusivity assignment + contractor-sent outreach drafts."""
from permitlead.assign import assign_exclusive, active_pools, region_of
from permitlead.outreach import draft

REGIONS = {"Central": ["Pittsfield", "Lenox"], "North": ["North Adams"]}
CAPS = {"solar": 1, "roofing": 2, "default": 2}
ADJ = {"solar": "solar", "roofing": "roofing", "hvac": "hvac"}

CONTRACTORS = [
    {"id": "s1", "name": "Solar One", "trade": "solar", "town": "Pittsfield", "phone": "1"},
    {"id": "s2", "name": "Solar Two", "trade": "solar", "town": "Lenox", "phone": "2"},
    {"id": "r1", "name": "Roof One", "trade": "roofing", "town": "Pittsfield", "phone": "3"},
]

LEADS = [
    {"lead_id": "L1", "address": "1 A St", "town": "Pittsfield", "primary_trade": "roofing",
     "owner": "K. Pham", "owner_pull": True, "score": 90,
     "adjacencies": [{"trade": "solar", "est_value_band": "10-20k"}], "freshness_days": 3},
    {"lead_id": "L2", "address": "2 B St", "town": "Lenox", "primary_trade": "roofing",
     "owner": "J. Lee", "owner_pull": False, "score": 80,
     "adjacencies": [{"trade": "solar", "est_value_band": "10-20k"}], "freshness_days": 5},
]


def test_cap_limits_active_subscribers():
    active = active_pools(CONTRACTORS, REGIONS, CAPS)
    # both solar subs are Central (Pittsfield, Lenox); cap=1 -> only one is active
    assert len(active[("solar", "Central")]) == 1
    # the roofer pool (cap 2) keeps its single member
    assert len(active[("roofing", "Central")]) == 1


def test_lead_never_double_sold_per_trade():
    assigned = assign_exclusive(LEADS, CONTRACTORS, REGIONS, CAPS, ADJ)
    # collect (lead_id, matched_trade) across all contractors
    seen = {}
    for cid, leads in assigned.items():
        for l in leads:
            key = (l["lead_id"], l["matched_trade"])
            assert key not in seen, f"{key} sold to two contractors"
            seen[key] = cid


def test_roof_permit_becomes_solar_lead():
    assigned = assign_exclusive(LEADS, CONTRACTORS, REGIONS, CAPS, ADJ)
    # a solar sub should receive the roof permit as a solar (adjacency) lead
    solar_leads = assigned["s1"] + assigned["s2"]
    assert any(l["matched_trade"] == "solar" for l in solar_leads)
    # owner-pulled roof permit should also reach the roofer
    assert any(l["matched_trade"] == "roofing" for l in assigned["r1"])


def test_outreach_is_contractor_sent_and_personalized():
    d = draft(LEADS[0], CONTRACTORS[0])
    assert "1 A St" in d["email"]["body"]
    assert CONTRACTORS[0]["name"] in d["email"]["body"]
    assert "never contact the homeowner" in d["channel_note"]
    assert d["sms"] and d["postcard"]
