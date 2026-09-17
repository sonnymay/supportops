from unittest.mock import MagicMock

import pytest

import ai


def test_fetch_ticket_escapes_id_before_interpolating(monkeypatch):
    fake_db_get = MagicMock(return_value=[{"id": "t1"}])
    monkeypatch.setattr(ai, "db_get", fake_db_get)

    ai._fetch_ticket("t1&status=eq.Closed")

    fake_db_get.assert_called_once_with("tickets", "id=eq.t1%26status%3Deq.Closed")


def test_fetch_ticket_raises_when_not_found(monkeypatch):
    monkeypatch.setattr(ai, "db_get", MagicMock(return_value=[]))

    with pytest.raises(ValueError, match="Ticket t1 not found"):
        ai._fetch_ticket("t1")


def test_fetch_notes_escapes_ticket_id_before_interpolating(monkeypatch):
    fake_db_get = MagicMock(return_value=[])
    monkeypatch.setattr(ai, "db_get", fake_db_get)

    ai._fetch_notes("t1),status.eq.Closed")

    fake_db_get.assert_called_once_with(
        "ticket_notes",
        "ticket_id=eq.t1%29%2Cstatus.eq.Closed&order=created_at.asc",
    )
