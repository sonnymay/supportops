from unittest.mock import MagicMock

import pytest

import ai
import database

# ---------------------------------------------------------------------------
# _fetch_ticket / _fetch_notes -- ticket_id is escaped before hitting PostgREST
# ---------------------------------------------------------------------------


def test_fetch_ticket_escapes_injected_query_params(monkeypatch):
    fake_db_get = MagicMock(return_value=[{"id": "t1", "title": "Printer jam"}])
    monkeypatch.setattr(ai, "db_get", fake_db_get)

    malicious_id = "t1&status=eq.Closed"
    ai._fetch_ticket(malicious_id)

    fake_db_get.assert_called_once_with(
        "tickets", f"id=eq.{database.escape_filter_value(malicious_id)}"
    )
    params = fake_db_get.call_args.args[1]
    assert "&status=eq.Closed" not in params


def test_fetch_notes_escapes_injected_query_params(monkeypatch):
    fake_db_get = MagicMock(return_value=[])
    monkeypatch.setattr(ai, "db_get", fake_db_get)

    malicious_id = "t1&status=eq.Closed"
    ai._fetch_notes(malicious_id)

    fake_db_get.assert_called_once_with(
        "ticket_notes",
        f"ticket_id=eq.{database.escape_filter_value(malicious_id)}&order=created_at.asc",
    )
    params = fake_db_get.call_args.args[1]
    assert params.count("&status=eq.Closed") == 0


def test_fetch_ticket_raises_value_error_when_missing(monkeypatch):
    monkeypatch.setattr(ai, "db_get", MagicMock(return_value=[]))

    with pytest.raises(ValueError, match="not found"):
        ai._fetch_ticket("missing")
