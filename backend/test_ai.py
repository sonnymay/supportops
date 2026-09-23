"""Unit tests for backend/ai.py's Supabase query helpers.

Focuses on the PostgREST filter injection guard -- ticket_id is user-supplied
(via the /ai/suggest request body) and must be escaped the same way main.py's
routes escape it, per database.escape_filter_value.
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
        return [{"id": "t1", "title": "Printer jam"}]

    monkeypatch.setattr(ai, "db_get", fake_get)

    malicious_id = "t1&status=eq.Closed"
    ticket = ai._fetch_ticket(malicious_id)

    assert ticket == {"id": "t1", "title": "Printer jam"}
    assert captured["table"] == "tickets"
    assert captured["params"] == "id=eq." + database.escape_filter_value(malicious_id)
    assert "&status=eq.Closed" not in captured["params"]


def test_fetch_notes_escapes_postgrest_injection(monkeypatch):
    captured = {}

    def fake_get(table, params=""):
        captured["table"] = table
        captured["params"] = params
        return []

    monkeypatch.setattr(ai, "db_get", fake_get)

    malicious_id = "t1&order=id.asc"
    ai._fetch_notes(malicious_id)

    assert captured["table"] == "ticket_notes"
    expected = (
        "ticket_id=eq." + database.escape_filter_value(malicious_id) + "&order=created_at.asc"
    )
    assert captured["params"] == expected
    assert captured["params"].count("&") == 1


def test_fetch_ticket_raises_when_not_found(monkeypatch):
    monkeypatch.setattr(ai, "db_get", MagicMock(return_value=[]))

    with pytest.raises(ValueError, match="Ticket t1 not found"):
        ai._fetch_ticket("t1")
