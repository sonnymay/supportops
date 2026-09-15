from unittest.mock import MagicMock

import pytest

import ai
import database

# ---------------------------------------------------------------------------
# _fetch_ticket / _fetch_notes -- ticket_id is escaped before interpolation
#
# POST /ai/suggest passes the caller-supplied ticket_id straight into these
# helpers. Without escaping, a value such as "t1&status=eq.Closed" could
# inject extra PostgREST query parameters, the same filter-injection class
# fixed for the /tickets/search and /tickets/filter endpoints in main.py.
# ---------------------------------------------------------------------------


@pytest.fixture
def fake_request(monkeypatch):
    monkeypatch.setattr(database, "SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setattr(database, "SUPABASE_KEY", "secret")
    response = MagicMock()
    response.status_code = 200
    response.text = "[]"
    response.json.return_value = []
    request = MagicMock(return_value=response)
    monkeypatch.setattr(database.requests, "request", request)
    return request


def test_fetch_ticket_escapes_injected_query_params(fake_request):
    malicious_id = "t1&status=eq.Closed"

    with pytest.raises(ValueError, match="not found"):
        ai._fetch_ticket(malicious_id)

    url = fake_request.call_args.args[1]
    assert url.count("&") == 0, url
    assert "status=eq.Closed" not in url
    assert url.endswith("/rest/v1/tickets?id=eq." + database.escape_filter_value(malicious_id))


def test_fetch_notes_escapes_injected_query_params(fake_request):
    malicious_id = "t1&select=*"

    notes = ai._fetch_notes(malicious_id)

    assert notes == []
    url = fake_request.call_args.args[1]
    assert url.count("&") == 1, url  # only the legitimate trailing &order=... remains
    assert "select=" not in url
    assert "ticket_id=eq." + database.escape_filter_value(malicious_id) in url
