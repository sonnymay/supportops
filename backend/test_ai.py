"""Unit tests for the ai module's Supabase lookups.

Mirrors the PostgREST filter-injection guards already covered in
test_main.py / test_database.py for the main.py routes.
"""

from unittest.mock import MagicMock

import pytest

import ai
import database


def test_fetch_ticket_escapes_postgrest_injection(monkeypatch):
    captured = {}

    def fake_get(table, params=""):
        captured["table"] = table
        captured["params"] = params
        return [{"id": "t1"}]

    monkeypatch.setattr(ai, "db_get", fake_get)

    malicious_id = "t1&status=eq.Closed"
    ai._fetch_ticket(malicious_id)

    assert captured["table"] == "tickets"
    assert "&status=eq.Closed" not in captured["params"]
    assert captured["params"] == f"id=eq.{database.escape_filter_value(malicious_id)}"


def test_fetch_notes_escapes_postgrest_injection(monkeypatch):
    captured = {}

    def fake_get(table, params=""):
        captured["table"] = table
        captured["params"] = params
        return []

    monkeypatch.setattr(ai, "db_get", fake_get)

    malicious_id = "t1&status=eq.Closed"
    ai._fetch_notes(malicious_id)

    assert captured["table"] == "ticket_notes"
    assert "&status=eq.Closed" not in captured["params"]
    escaped = database.escape_filter_value(malicious_id)
    assert captured["params"] == f"ticket_id=eq.{escaped}&order=created_at.asc"


def test_fetch_ticket_raises_when_not_found(monkeypatch):
    monkeypatch.setattr(ai, "db_get", MagicMock(return_value=[]))

    with pytest.raises(ValueError, match="not found"):
        ai._fetch_ticket("missing")
