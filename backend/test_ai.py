"""Unit tests for ai.py's Supabase query construction.

Mirrors test_database.py's injection-guard tests: ai.py builds its own
PostgREST filter strings (it fetches tickets/notes directly via db_get
rather than going through main.py's already-escaped endpoints), so it
needs the same escape_filter_value guard on user-supplied ticket ids.
"""

from unittest.mock import MagicMock

import pytest

import ai
import database


@pytest.mark.parametrize("fetch", ["_fetch_ticket", "_fetch_notes"])
def test_fetch_helpers_escape_injected_ticket_id(monkeypatch, fetch):
    monkeypatch.setattr(database, "SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setattr(database, "SUPABASE_KEY", "secret")
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.text = "[]"
    fake_response.json.return_value = []
    fake_request = MagicMock(return_value=fake_response)
    monkeypatch.setattr(database.requests, "request", fake_request)

    malicious_id = "t1&status=eq.Closed"
    if fetch == "_fetch_ticket":
        with pytest.raises(ValueError):
            ai._fetch_ticket(malicious_id)
    else:
        ai._fetch_notes(malicious_id)

    url = fake_request.call_args.args[1]
    assert "status=eq.Closed" not in url
    assert database.escape_filter_value(malicious_id) in url
