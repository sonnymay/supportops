"""Unit tests for backend/ai.py.

Mirrors the PostgREST filter injection guards in test_database.py: ticket_id
values that flow into ai.py's Supabase queries must be escaped the same way
db_get/db_patch/db_delete escape theirs (see database.escape_filter_value).
"""

from unittest.mock import MagicMock

import pytest

import ai


@pytest.mark.parametrize(
    "fetch_fn,table",
    [
        (ai._fetch_ticket, "tickets"),
        (ai._fetch_notes, "ticket_notes"),
    ],
)
def test_fetch_helpers_escape_injected_ticket_id(monkeypatch, fetch_fn, table):
    captured = {}

    def fake_get(table_name, params=""):
        captured["table"] = table_name
        captured["params"] = params
        return [{"id": "t1", "status": "Open"}]

    monkeypatch.setattr(ai, "db_get", fake_get)

    malicious_id = "t1&status=eq.Closed"
    fetch_fn(malicious_id)

    assert captured["table"] == table
    assert "status=eq.Closed" not in captured["params"]
    assert captured["params"].count("&") == (1 if table == "ticket_notes" else 0)


def test_fetch_ticket_raises_value_error_when_not_found(monkeypatch):
    monkeypatch.setattr(ai, "db_get", MagicMock(return_value=[]))

    with pytest.raises(ValueError):
        ai._fetch_ticket("missing")
