from unittest.mock import MagicMock
from urllib.parse import parse_qs, urlsplit

import pytest

import ai
import database


def test_fetch_ticket_escapes_id_before_interpolating(monkeypatch):
    fake_db_get = MagicMock(return_value=[{"id": "t1"}])
    monkeypatch.setattr(ai, "db_get", fake_db_get)

    ai._fetch_ticket("t1&status=eq.Closed")

    fake_db_get.assert_called_once_with("tickets", "id=eq.t1%26status%3Deq.Closed")


def test_fetch_ticket_raises_when_not_found(monkeypatch):
    monkeypatch.setattr(ai, "db_get", MagicMock(return_value=[]))

    with pytest.raises(ValueError, match="Ticket t1 not found"):
        ai._fetch_ticket("t1")


@pytest.mark.parametrize(
    ("ticket_id", "expected_filter"),
    [
        ("t1),status.eq.Closed", "t1%29%2Cstatus.eq.Closed"),
        ("t1&select=*", "t1%26select%3D%2A"),
        ("t1%26select%3D*", "t1%2526select%253D%2A"),
    ],
)
def test_fetch_notes_escapes_ticket_id_before_interpolating(
    monkeypatch, ticket_id, expected_filter
):
    fake_db_get = MagicMock(return_value=[])
    monkeypatch.setattr(ai, "db_get", fake_db_get)

    ai._fetch_notes(ticket_id)

    fake_db_get.assert_called_once_with(
        "ticket_notes",
        f"ticket_id=eq.{expected_filter}&order=created_at.asc",
    )


@pytest.mark.parametrize(
    ("fetch", "table", "expected_query"),
    [
        (ai._fetch_ticket, "tickets", {"id": ["eq.t1&select=*"]}),
        (
            ai._fetch_notes,
            "ticket_notes",
            {"ticket_id": ["eq.t1&select=*"], "order": ["created_at.asc"]},
        ),
    ],
)
def test_fetch_preserves_one_id_filter_at_http_boundary(monkeypatch, fetch, table, expected_query):
    monkeypatch.setattr(database, "SUPABASE_URL", "https://example.invalid")
    monkeypatch.setattr(database, "SUPABASE_KEY", "test-key")
    response = MagicMock(status_code=200, text='[{"id": "t1"}]')
    response.json.return_value = [{"id": "t1"}]
    request = MagicMock(return_value=response)
    monkeypatch.setattr(database.requests, "request", request)

    fetch("t1&select=*")

    request.assert_called_once()
    method, url = request.call_args.args
    prepared_url = database.requests.Request(method, url).prepare().url
    parsed = urlsplit(prepared_url)
    assert method == "GET"
    assert parsed.path == f"/rest/v1/{table}"
    assert parse_qs(parsed.query) == expected_query
