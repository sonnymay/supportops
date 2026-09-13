"""Unit tests for ai.py -- PostgREST filter injection guard on ticket_id."""

import pytest

import ai


@pytest.mark.parametrize(
    "fetch",
    [ai._fetch_ticket, ai._fetch_notes],
    ids=["_fetch_ticket", "_fetch_notes"],
)
def test_fetch_helpers_escape_injected_ticket_id(monkeypatch, fetch):
    captured = {}

    def fake_db_get(table, params=""):
        captured["params"] = params
        return [{"id": "t1"}]

    monkeypatch.setattr(ai, "db_get", fake_db_get)

    malicious_id = "t1&status=eq.Closed"
    fetch(malicious_id)

    params = captured["params"]
    assert "&status=eq.Closed" not in params
    assert "status=eq.Closed" not in params
