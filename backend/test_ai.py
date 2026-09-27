from unittest.mock import MagicMock

import ai


def test_fetch_ticket_escapes_injected_query_params(monkeypatch):
    fake_db_get = MagicMock(return_value=[{"id": "t1", "title": "x"}])
    monkeypatch.setattr(ai, "db_get", fake_db_get)

    malicious_id = "t1&status=eq.Closed"
    ai._fetch_ticket(malicious_id)

    table, params = fake_db_get.call_args.args
    assert table == "tickets"
    assert params.count("&") == 0, params
    assert "status=eq.Closed" not in params
    assert params == "id=eq." + ai.escape_filter_value(malicious_id)


def test_fetch_notes_escapes_injected_query_params(monkeypatch):
    fake_db_get = MagicMock(return_value=[])
    monkeypatch.setattr(ai, "db_get", fake_db_get)

    malicious_id = "t1&status=eq.Closed"
    ai._fetch_notes(malicious_id)

    table, params = fake_db_get.call_args.args
    assert table == "ticket_notes"
    assert params.count("&") == 1, params
    assert "status=eq.Closed" not in params
    assert (
        params == "ticket_id=eq." + ai.escape_filter_value(malicious_id) + "&order=created_at.asc"
    )
