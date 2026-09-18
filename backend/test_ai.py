from unittest.mock import MagicMock

import pytest

import ai
import database


@pytest.mark.parametrize("fetcher", ["_fetch_ticket", "_fetch_notes"])
def test_fetchers_escape_injected_ticket_id(monkeypatch, fetcher):
    """A malicious ticket_id must not be able to inject extra PostgREST filters.

    ai.py builds its own filter strings independently of main.py, so it needs the
    same escape_filter_value guard that main.py's endpoints already apply to id
    path parameters.
    """
    fake_db_get = MagicMock(return_value=[{"id": "t1", "status": "Open"}])
    monkeypatch.setattr(ai, "db_get", fake_db_get)

    malicious_id = "t1&status=eq.Closed"
    getattr(ai, fetcher)(malicious_id)

    params = fake_db_get.call_args.args[1]
    assert "status=eq.Closed" not in params
    assert database.escape_filter_value(malicious_id) in params
