from unittest.mock import MagicMock
from urllib.parse import unquote

import pytest
import requests

import database


def test_get_headers_uses_supabase_key(monkeypatch):
    monkeypatch.setattr(database, "SUPABASE_KEY", "secret")

    headers = database.get_headers()

    assert headers["apikey"] == "secret"
    assert headers["Authorization"] == "Bearer secret"
    assert headers["Prefer"] == "return=representation"


def test_database_helpers_call_supabase_rest_api(monkeypatch):
    monkeypatch.setattr(database, "SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setattr(database, "SUPABASE_KEY", "secret")
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.text = '[{"id":"1"}]'
    fake_response.json.return_value = [{"id": "1"}]
    fake_request = MagicMock(return_value=fake_response)
    monkeypatch.setattr(database.requests, "request", fake_request)

    assert database.db_get("tickets", "id=eq.1") == [{"id": "1"}]
    assert database.db_post("tickets", {"title": "Issue"}) == [{"id": "1"}]
    assert database.db_patch("tickets", "1", {"status": "Closed"}) == [{"id": "1"}]
    assert database.db_delete("tickets", "1") == [{"id": "1"}]

    fake_request.assert_any_call(
        "GET",
        "https://example.supabase.co/rest/v1/tickets?id=eq.1",
        headers=database.get_headers(),
        json=None,
        timeout=20,
    )
    fake_request.assert_any_call(
        "POST",
        "https://example.supabase.co/rest/v1/tickets",
        headers=database.get_headers(),
        json={"title": "Issue"},
        timeout=20,
    )
    fake_request.assert_any_call(
        "PATCH",
        "https://example.supabase.co/rest/v1/tickets?id=eq.1",
        headers=database.get_headers(),
        json={"status": "Closed"},
        timeout=20,
    )
    fake_request.assert_any_call(
        "DELETE",
        "https://example.supabase.co/rest/v1/tickets?id=eq.1",
        headers=database.get_headers(),
        json=None,
        timeout=20,
    )


def test_missing_supabase_config_raises_clear_error(monkeypatch):
    monkeypatch.setattr(database, "SUPABASE_URL", "")
    monkeypatch.setattr(database, "SUPABASE_KEY", "")

    with pytest.raises(database.DatabaseConfigError, match="SUPABASE_URL"):
        database.db_get("tickets")


def test_supabase_http_error_raises_database_error(monkeypatch):
    monkeypatch.setattr(database, "SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setattr(database, "SUPABASE_KEY", "secret")
    fake_response = MagicMock()
    fake_response.raise_for_status.side_effect = requests.HTTPError("503")
    monkeypatch.setattr(database.requests, "request", MagicMock(return_value=fake_response))

    with pytest.raises(database.DatabaseRequestError, match="temporarily unavailable"):
        database.db_get("tickets")


@pytest.mark.parametrize(
    "error", [requests.Timeout("timed out"), requests.ConnectionError("offline")]
)
def test_supabase_network_error_raises_database_error(monkeypatch, error):
    monkeypatch.setattr(database, "SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setattr(database, "SUPABASE_KEY", "secret")
    monkeypatch.setattr(database.requests, "request", MagicMock(side_effect=error))

    with pytest.raises(database.DatabaseRequestError, match="temporarily unavailable"):
        database.db_get("tickets")


# ---------------------------------------------------------------------------
# escape_filter_value -- PostgREST filter injection guard
# ---------------------------------------------------------------------------


def test_escape_filter_value_passes_plain_text_through():
    assert database.escape_filter_value("printer") == "printer"
    assert database.escape_filter_value("agent-7") == "agent-7"
    assert (
        database.escape_filter_value("123e4567-e89b-12d3-a456-426614174000")
        == "123e4567-e89b-12d3-a456-426614174000"
    )


def test_escape_filter_value_percent_encodes_query_delimiters():
    escaped = database.escape_filter_value("x,status.like.Closed&select=*&path=/tickets")

    assert escaped == "x%2Cstatus.like.Closed%26select%3D%2A%26path%3D%2Ftickets"


def test_escape_filter_value_quotes_and_escapes_wildcard_pattern():
    escaped = database.escape_filter_value('a,b("c\\d")', wildcard=True)

    assert unquote(escaped) == '"*a,b(\\"c\\\\d\\")*"'
