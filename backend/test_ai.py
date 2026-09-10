"""Unit tests for backend/ai.py -- PostgREST filter injection guards.

Mirrors the id-escaping coverage in test_database.py / test_main.py: ticket
ids that flow into ai.py's Supabase lookups must be escaped the same way
main.py's routes escape them.
"""

import pytest

import ai


def test_fetch_ticket_escapes_injected_id(monkeypatch):
    captured = {}

    def fake_get(table, params=""):
        captured["table"] = table
        captured["params"] = params
        return [{"id": "t1"}]

    monkeypatch.setattr(ai, "db_get", fake_get)

    ai._fetch_ticket("t1&status=eq.Closed")

    assert captured["table"] == "tickets"
    assert captured["params"] == "id=eq.t1%26status%3Deq.Closed"


def test_fetch_ticket_raises_when_not_found(monkeypatch):
    monkeypatch.setattr(ai, "db_get", lambda table, params="": [])

    with pytest.raises(ValueError):
        ai._fetch_ticket("missing")


def test_fetch_notes_escapes_injected_id(monkeypatch):
    captured = {}

    def fake_get(table, params=""):
        captured["table"] = table
        captured["params"] = params
        return []

    monkeypatch.setattr(ai, "db_get", fake_get)

    ai._fetch_notes("t1&status=eq.Closed")

    assert captured["table"] == "ticket_notes"
    assert captured["params"] == "ticket_id=eq.t1%26status%3Deq.Closed&order=created_at.asc"
