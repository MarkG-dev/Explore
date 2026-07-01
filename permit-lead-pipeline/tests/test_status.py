"""Source-health verdicts for the ops dashboard."""
from datetime import datetime

from permitlead.export_status import _health

NOW = datetime(2026, 7, 1, 12, 0, 0)


def ok_run(finished, rows=10, status="success", error=None):
    return {"finished_at": finished, "rows_scraped": rows, "rows_new": rows,
            "status": status, "error": error}


def test_disabled_and_never():
    assert _health(False, None, NOW) == "disabled"
    assert _health(True, None, NOW) == "never"


def test_ok_when_fresh_with_rows():
    assert _health(True, ok_run("2026-07-01T07:00:00"), NOW) == "ok"


def test_dead_on_error_or_zero_rows():
    assert _health(True, ok_run("2026-07-01T07:00:00", status="error",
                                error="boom"), NOW) == "dead"
    assert _health(True, ok_run("2026-07-01T07:00:00", rows=0), NOW) == "dead"


def test_stale_when_old():
    assert _health(True, ok_run("2026-06-20T07:00:00"), NOW) == "stale"
