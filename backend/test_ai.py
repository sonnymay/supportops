import pytest

import ai
import database

# ---------------------------------------------------------------------------
# _fetch_ticket / _fetch_notes -- PostgREST filter injection guard
#
# ticket_id flows in from the POST /ai/suggest request body, so it must be
# escaped the same way the {id}-based routes in main.py are (see db_patch /
# db_delete in database.py).
# ---------------------------------------------------------------------------


def test_fetch_ticket_escapes_injected_ticket_id(monkeypatch):
    captured = {}

    def fake_get(table, params=""):
        captured["table"] = table
        captured["params"] = params
        return [{"id": "t1"}]

    monkeypatch.setattr(ai, "db_get", fake_get)

    malicious_id = "t1&status=eq.Closed"
    ai._fetch_ticket(malicious_id)

    assert captured["params"] == "id=eq." + database.escape_filter_value(malicious_id)
    assert "&status=eq.Closed" not in captured["params"]


def test_fetch_notes_escapes_injected_ticket_id(monkeypatch):
    captured = {}

    def fake_get(table, params=""):
        captured["table"] = table
        captured["params"] = params
        return []

    monkeypatch.setattr(ai, "db_get", fake_get)

    malicious_id = "t1&status=eq.Closed"
    ai._fetch_notes(malicious_id)

    expected_prefix = "ticket_id=eq." + database.escape_filter_value(malicious_id)
    assert captured["params"] == expected_prefix + "&order=created_at.asc"
    assert "&status=eq.Closed" not in captured["params"]


def test_fetch_ticket_raises_when_not_found(monkeypatch):
    monkeypatch.setattr(ai, "db_get", lambda table, params="": [])

    with pytest.raises(ValueError, match="not found"):
        ai._fetch_ticket("missing")
