from unittest.mock import MagicMock

import pytest

import ai
import database


@pytest.fixture
def fake_supabase(monkeypatch):
    monkeypatch.setattr(database, "SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setattr(database, "SUPABASE_KEY", "secret")
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.text = "[]"
    fake_response.json.return_value = []
    fake_request = MagicMock(return_value=fake_response)
    monkeypatch.setattr(database.requests, "request", fake_request)
    return fake_request


# ---------------------------------------------------------------------------
# _fetch_ticket / _fetch_notes -- ticket_id is escaped before interpolation
# into PostgREST filters, mirroring the guard already applied in main.py.
# ---------------------------------------------------------------------------


def test_fetch_ticket_escapes_postgrest_injection(fake_supabase):
    malicious_id = "t1&select=*,customers(email)"

    with pytest.raises(ValueError, match="not found"):
        ai._fetch_ticket(malicious_id)

    url = fake_supabase.call_args.args[1]
    assert url.count("&") == 0, url


def test_fetch_notes_escapes_postgrest_injection(fake_supabase):
    malicious_id = "t1&status=eq.Closed"

    notes = ai._fetch_notes(malicious_id)

    assert notes == []
    url = fake_supabase.call_args.args[1]
    assert url.count("&") == 1, url
    assert "order=created_at.asc" in url
