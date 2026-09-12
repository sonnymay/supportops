"""Unit tests for backend/ai.py's Supabase filter construction.

Mirrors the escaping coverage in test_database.py to guard against the same
class of PostgREST filter injection via an untrusted ticket_id.
"""

import ai


def test_fetch_ticket_escapes_injected_query_params(monkeypatch):
    captured = {}

    def fake_db_get(table, params=""):
        captured["table"] = table
        captured["params"] = params
        return [{"id": "t1", "title": "Printer down"}]

    monkeypatch.setattr(ai, "db_get", fake_db_get)

    malicious_id = "t1&status=eq.Closed"
    ai._fetch_ticket(malicious_id)

    assert captured["table"] == "tickets"
    assert captured["params"].count("&") == 0
    assert "status=eq.Closed" not in captured["params"]


def test_fetch_notes_escapes_injected_query_params(monkeypatch):
    captured = {}

    def fake_db_get(table, params=""):
        captured["table"] = table
        captured["params"] = params
        return []

    monkeypatch.setattr(ai, "db_get", fake_db_get)

    malicious_id = "t1&status=eq.Closed"
    ai._fetch_notes(malicious_id)

    assert captured["table"] == "ticket_notes"
    assert captured["params"].count("&") == 1  # only the trailing "&order=..." is ours
    assert "status=eq.Closed" not in captured["params"]
    assert captured["params"].endswith("&order=created_at.asc")
