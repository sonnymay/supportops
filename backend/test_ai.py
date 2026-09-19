from unittest.mock import MagicMock

import pytest

import ai
import database


@pytest.mark.parametrize("helper", ["_fetch_ticket", "_fetch_notes"])
def test_fetch_helpers_escape_injected_ticket_id(monkeypatch, helper):
    """A crafted ticket_id must not be able to append extra PostgREST filters.

    Mirrors the injection guard already required of the /tickets/{id} routes
    in main.py -- ai.py reaches Supabase through the same db_get() helper and
    must escape user-controlled ids the same way.
    """
    captured = {}

    def fake_get(table, params=""):
        captured["table"] = table
        captured["params"] = params
        return [{"id": "t1", "status": "Open"}]

    monkeypatch.setattr(ai, "db_get", fake_get)

    malicious_id = "t1&status=eq.Closed"
    if helper == "_fetch_ticket":
        ai._fetch_ticket(malicious_id)
    else:
        ai._fetch_notes(malicious_id)

    params = captured["params"]
    assert "&status=eq.Closed" not in params
    assert params.split("&", 1)[0] == f"id=eq.{database.escape_filter_value(malicious_id)}" or (
        helper == "_fetch_notes"
        and params.split("&", 1)[0] == f"ticket_id=eq.{database.escape_filter_value(malicious_id)}"
    )


def test_fetch_ticket_not_found_raises_value_error(monkeypatch):
    monkeypatch.setattr(ai, "db_get", MagicMock(return_value=[]))

    with pytest.raises(ValueError, match="Ticket t1 not found"):
        ai._fetch_ticket("t1")
