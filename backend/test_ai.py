"""Unit tests for backend/ai.py.

database.db_get is mocked so the suite runs in CI with no Supabase connection
or API keys required.
"""

from unittest.mock import MagicMock

import ai


def test_fetch_ticket_escapes_injected_query_params(monkeypatch):
    fake_db_get = MagicMock(return_value=[{"id": "t1", "title": "Issue"}])
    monkeypatch.setattr(ai, "db_get", fake_db_get)

    malicious_id = "t1&status=eq.Closed"
    ai._fetch_ticket(malicious_id)

    params = fake_db_get.call_args.args[1]
    assert params.count("&") == 0, params
    assert "status=eq.Closed" not in params
    assert params == f"id=eq.{ai.escape_filter_value(malicious_id)}"


def test_fetch_notes_escapes_injected_query_params(monkeypatch):
    fake_db_get = MagicMock(return_value=[])
    monkeypatch.setattr(ai, "db_get", fake_db_get)

    malicious_id = "t1,select=*"
    ai._fetch_notes(malicious_id)

    params = fake_db_get.call_args.args[1]
    assert "select=*" not in params
    assert params == f"ticket_id=eq.{ai.escape_filter_value(malicious_id)}&order=created_at.asc"
