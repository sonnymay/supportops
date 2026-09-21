"""Unit tests for backend/ai.py.

Focused on the PostgREST filter-injection guard: ticket_id values must be
escaped the same way main.py's ticket routes escape them (see
test_main.py::test_ticket_id_routes_escape_postgrest_injection).
"""

from urllib.parse import quote

import pytest

import ai


def test_fetch_ticket_escapes_postgrest_injection(monkeypatch):
    captured = {}

    def fake_get(table, params=""):
        captured["table"] = table
        captured["params"] = params
        return [{"id": "t1"}]

    monkeypatch.setattr(ai, "db_get", fake_get)

    # A crafted id that tries to append an extra filter / parameter.
    malicious_id = "t1&status=eq.Closed"

    ai._fetch_ticket(malicious_id)

    assert captured["params"] == f"id=eq.{quote(malicious_id, safe='')}"
    assert "&status=eq.Closed" not in captured["params"]


def test_fetch_notes_escapes_postgrest_injection(monkeypatch):
    captured = {}

    def fake_get(table, params=""):
        captured["table"] = table
        captured["params"] = params
        return []

    monkeypatch.setattr(ai, "db_get", fake_get)

    malicious_id = "t1&limit=1"

    ai._fetch_notes(malicious_id)

    assert captured["params"] == f"ticket_id=eq.{quote(malicious_id, safe='')}&order=created_at.asc"
    assert "&limit=1" not in captured["params"]


def test_fetch_ticket_raises_when_not_found(monkeypatch):
    monkeypatch.setattr(ai, "db_get", lambda table, params="": [])

    with pytest.raises(ValueError):
        ai._fetch_ticket("missing")
