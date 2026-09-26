from urllib.parse import quote, unquote

import ai


def test_fetch_ticket_escapes_postgrest_injection(monkeypatch):
    captured = {}

    def fake_get(table, params=""):
        captured["table"] = table
        captured["params"] = params
        return [{"id": "t1"}]

    monkeypatch.setattr(ai, "db_get", fake_get)

    ai._fetch_ticket("t1&status=eq.Closed")

    assert captured["table"] == "tickets"
    assert "&status=eq.Closed" not in captured["params"]
    assert unquote(captured["params"]) == "id=eq.t1&status=eq.Closed"


def test_fetch_notes_escapes_postgrest_injection(monkeypatch):
    captured = {}

    def fake_get(table, params=""):
        captured["table"] = table
        captured["params"] = params
        return []

    monkeypatch.setattr(ai, "db_get", fake_get)

    ai._fetch_notes("t1&status=eq.Closed")

    assert captured["table"] == "ticket_notes"
    assert "&status=eq.Closed" not in captured["params"].removesuffix("&order=created_at.asc")
    assert captured["params"] == (
        f"ticket_id=eq.{quote('t1&status=eq.Closed', safe='')}&order=created_at.asc"
    )
