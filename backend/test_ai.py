"""Unit tests for backend/ai.py.

Covers the PostgREST filter-injection guard on ticket_id, mirroring the
escaping fix already applied to the /tickets routes in main.py
(see test_database.py's test_id_helpers_escape_injected_query_params).
"""

from unittest.mock import MagicMock

import pytest

import ai
import database


def test_fetch_ticket_escapes_injected_query_params(monkeypatch):
    fake_db_get = MagicMock(return_value=[{"id": "t1", "title": "Printer jam"}])
    monkeypatch.setattr(ai, "db_get", fake_db_get)

    malicious_id = "t1&status=eq.Closed"
    ai._fetch_ticket(malicious_id)

    table, params = fake_db_get.call_args.args
    assert table == "tickets"
    assert params.count("&") == 0, params
    assert "status=eq.Closed" not in params
    assert params == f"id=eq.{database.escape_filter_value(malicious_id)}"


def test_fetch_notes_escapes_injected_query_params(monkeypatch):
    fake_db_get = MagicMock(return_value=[])
    monkeypatch.setattr(ai, "db_get", fake_db_get)

    malicious_id = "t1)&status=eq.Closed&limit=1"
    ai._fetch_notes(malicious_id)

    table, params = fake_db_get.call_args.args
    assert table == "ticket_notes"
    assert "status=eq.Closed" not in params
    assert params.count("&") == 1, params
    assert params.startswith(f"ticket_id=eq.{database.escape_filter_value(malicious_id)}")
    assert params.endswith("&order=created_at.asc")


def test_fetch_ticket_not_found_raises_value_error(monkeypatch):
    monkeypatch.setattr(ai, "db_get", MagicMock(return_value=[]))

    with pytest.raises(ValueError, match="not found"):
        ai._fetch_ticket("missing")
