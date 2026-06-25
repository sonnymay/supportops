"""Unit tests for the SupportOps FastAPI backend.
Database (database.db_*) and the ai module are mocked so the suite runs in CI
with no Supabase connection or API keys required.
"""

import sys
import types
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "http://fake.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "fake-key")
    fake_ai = types.ModuleType("ai")
    fake_ai.suggest = MagicMock(return_value="stubbed")
    fake_ai.suggest_for_ticket = MagicMock(return_value={"matches": []})
    sys.modules["ai"] = fake_ai
    import importlib

    import database
    import main

    importlib.reload(database)
    importlib.reload(main)
    return TestClient(main.app), main


# ---------------------------------------------------------------------------
# Search and filter endpoint tests (added for v1.3.0 endpoints)
# ---------------------------------------------------------------------------


def test_search_tickets_returns_matching_rows(client, monkeypatch):
    test_client, main = client
    rows = [{"id": "t1", "title": "Printer down", "description": "Jammed"}]
    captured = {}

    def fake_get(table, params=""):
        captured["table"] = table
        captured["params"] = params
        return rows

    monkeypatch.setattr(main, "db_get", fake_get)

    res = test_client.get("/tickets/search?q=printer")

    assert res.status_code == 200
    assert res.json() == rows
    assert captured["table"] == "tickets"
    assert "printer" in captured["params"].lower()


def test_search_tickets_returns_empty_list_when_no_matches(client, monkeypatch):
    test_client, main = client
    monkeypatch.setattr(main, "db_get", lambda table, params="": [])

    res = test_client.get("/tickets/search?q=nonexistent")

    assert res.status_code == 200
    assert res.json() == []


def test_filter_tickets_by_status(client, monkeypatch):
    test_client, main = client
    rows = [{"id": "t2", "status": "Open", "priority": "High", "assigned_user_id": None}]
    captured = {}

    def fake_get(table, params=""):
        captured["table"] = table
        captured["params"] = params
        return rows

    monkeypatch.setattr(main, "db_get", fake_get)

    res = test_client.get("/tickets/filter?status=Open")

    assert res.status_code == 200
    assert res.json() == rows
    assert captured["table"] == "tickets"
    assert "Open" in captured["params"]


def test_filter_tickets_by_priority(client, monkeypatch):
    test_client, main = client
    rows = [{"id": "t3", "status": "In Progress", "priority": "Critical", "assigned_user_id": "u1"}]
    captured = {}

    def fake_get(table, params=""):
        captured["params"] = params
        return rows

    monkeypatch.setattr(main, "db_get", fake_get)

    res = test_client.get("/tickets/filter?priority=Critical")

    assert res.status_code == 200
    assert res.json() == rows
    assert "Critical" in captured["params"]


def test_filter_tickets_by_assignee(client, monkeypatch):
    test_client, main = client
    rows = [{"id": "t4", "status": "Open", "priority": "Low", "assigned_user_id": "agent-7"}]
    captured = {}

    def fake_get(table, params=""):
        captured["params"] = params
        return rows

    monkeypatch.setattr(main, "db_get", fake_get)

    res = test_client.get("/tickets/filter?assignee=agent-7")

    assert res.status_code == 200
    assert res.json() == rows
    assert "agent-7" in captured["params"]


def test_filter_tickets_with_multiple_params(client, monkeypatch):
    test_client, main = client
    rows = [{"id": "t5", "status": "Open", "priority": "High", "assigned_user_id": "u2"}]
    captured = {}

    def fake_get(table, params=""):
        captured["params"] = params
        return rows

    monkeypatch.setattr(main, "db_get", fake_get)

    res = test_client.get("/tickets/filter?status=Open&priority=High&assignee=u2")

    assert res.status_code == 200
    assert res.json() == rows
    assert "Open" in captured["params"]
    assert "High" in captured["params"]
    assert "u2" in captured["params"]


def test_filter_tickets_returns_empty_list_when_no_matches(client, monkeypatch):
    test_client, main = client
    monkeypatch.setattr(main, "db_get", lambda table, params="": [])

    res = test_client.get("/tickets/filter?status=Resolved")

    assert res.status_code == 200
    assert res.json() == []


def test_health_returns_ok(client):
    test_client, _ = client
    res = test_client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_dependency_health_returns_ok_when_supabase_reachable(client, monkeypatch):
    test_client, main = client
    monkeypatch.setattr(main.database, "is_configured", lambda: True)
    monkeypatch.setattr(main, "db_get", lambda table, params="": [])

    res = test_client.get("/health/dependencies")

    assert res.status_code == 200
    assert res.json() == {
        "status": "ok",
        "supabase": {"configured": True, "reachable": True, "detail": None},
    }


def test_dependency_health_returns_503_when_supabase_missing_config(client, monkeypatch):
    test_client, main = client
    monkeypatch.setattr(main.database, "is_configured", lambda: False)

    res = test_client.get("/health/dependencies")

    assert res.status_code == 503
    assert res.json()["status"] == "error"
    assert res.json()["supabase"]["configured"] is False


def test_dependency_health_returns_503_when_supabase_query_fails(client, monkeypatch):
    test_client, main = client
    monkeypatch.setattr(main.database, "is_configured", lambda: True)
    monkeypatch.setattr(
        main,
        "db_get",
        lambda table, params="": (_ for _ in ()).throw(
            main.DatabaseRequestError("SupportOps database is unavailable.")
        ),
    )

    res = test_client.get("/health/dependencies")

    assert res.status_code == 503
    assert res.json()["status"] == "error"
    assert res.json()["supabase"]["reachable"] is False


def test_get_ticket_not_found_returns_404(client, monkeypatch):
    test_client, main = client
    monkeypatch.setattr(main, "db_get", lambda table, params="": [])
    res = test_client.get("/tickets/missing")
    assert res.status_code == 404
    assert res.json()["detail"] == "Ticket not found"


def test_get_customers_returns_db_rows(client, monkeypatch):
    test_client, main = client
    rows = [{"id": "1", "name": "Acme Inc"}]
    monkeypatch.setattr(main, "db_get", lambda table, params="": rows)
    res = test_client.get("/customers")
    assert res.status_code == 200
    assert res.json() == rows


def test_customer_crud_delegates_to_database(client, monkeypatch):
    test_client, main = client
    calls = []
    monkeypatch.setattr(
        main, "db_post", lambda table, data: calls.append(("post", table, data)) or data
    )
    monkeypatch.setattr(
        main,
        "db_patch",
        lambda table, row_id, data: calls.append(("patch", table, row_id, data)) or data,
    )
    monkeypatch.setattr(
        main,
        "db_delete",
        lambda table, row_id: calls.append(("delete", table, row_id)) or {"deleted": row_id},
    )

    create_res = test_client.post("/customers", json={"name": "Acme", "email": "ops@example.com"})
    update_res = test_client.put("/customers/c1", json={"name": "Acme Updated"})
    delete_res = test_client.delete("/customers/c1")

    assert create_res.status_code == 200
    assert update_res.status_code == 200
    assert delete_res.status_code == 200
    assert calls[0] == (
        "post",
        "customers",
        {"name": "Acme", "email": "ops@example.com", "phone": None, "company": None},
    )
    assert calls[1][0:3] == ("patch", "customers", "c1")
    assert calls[2] == ("delete", "customers", "c1")


def test_device_routes_delegate_to_database(client, monkeypatch):
    test_client, main = client
    rows = [{"id": "d1", "serial_number": "SN-1"}]
    calls = []
    monkeypatch.setattr(main, "db_get", lambda table, params="": rows)
    monkeypatch.setattr(
        main, "db_post", lambda table, data: calls.append(("post", table, data)) or data
    )
    monkeypatch.setattr(
        main,
        "db_patch",
        lambda table, row_id, data: calls.append(("patch", table, row_id, data)) or data,
    )

    list_res = test_client.get("/devices")
    create_res = test_client.post("/devices", json={"serial_number": "SN-1", "model": "Router"})
    update_res = test_client.put("/devices/d1", json={"serial_number": "SN-2"})

    assert list_res.status_code == 200
    assert list_res.json() == rows
    assert create_res.status_code == 200
    assert update_res.status_code == 200
    assert calls[0][0:2] == ("post", "devices")
    assert calls[1][0:3] == ("patch", "devices", "d1")


def test_device_routes_convert_blank_customer_id_to_null(client, monkeypatch):
    test_client, main = client
    calls = []
    monkeypatch.setattr(main, "db_post", lambda table, data: calls.append((table, data)) or data)

    res = test_client.post(
        "/devices", json={"serial_number": "SN-1", "model": "Router", "customer_id": ""}
    )

    assert res.status_code == 200
    assert calls[0] == (
        "devices",
        {
            "serial_number": "SN-1",
            "model": "Router",
            "product_type": None,
            "customer_id": None,
        },
    )


def test_ticket_routes_create_update_and_record_status_history(client, monkeypatch):
    test_client, main = client
    posts = []

    def fake_get(table, params=""):
        if table == "tickets" and params.startswith("id=eq.t1&select=status"):
            return [{"status": "Open"}]
        if table == "tickets" and params.startswith("id=eq.t1"):
            return [{"id": "t1", "status": "Open"}]
        return [{"id": "t1", "title": "Printer down"}]

    monkeypatch.setattr(main, "db_get", fake_get)
    monkeypatch.setattr(main, "db_post", lambda table, data: posts.append((table, data)) or data)
    monkeypatch.setattr(main, "db_patch", lambda table, row_id, data: {"id": row_id, **data})

    list_res = test_client.get("/tickets")
    get_res = test_client.get("/tickets/t1")
    create_res = test_client.post("/tickets", json={"title": "Printer down", "status": "Open"})
    update_res = test_client.put("/tickets/t1", json={"title": "Printer fixed", "status": "Closed"})

    assert list_res.status_code == 200
    assert get_res.status_code == 200
    assert create_res.status_code == 200
    assert update_res.status_code == 200
    assert (
        "ticket_history",
        {"ticket_id": "t1", "old_status": "Open", "new_status": "Closed", "changed_by": "Agent"},
    ) in posts


def test_ticket_routes_convert_blank_relationship_ids_to_null(client, monkeypatch):
    test_client, main = client
    calls = []
    monkeypatch.setattr(main, "db_post", lambda table, data: calls.append((table, data)) or data)

    res = test_client.post(
        "/tickets",
        json={
            "title": "Printer down",
            "customer_id": "",
            "device_id": "",
            "assigned_user_id": "",
        },
    )

    assert res.status_code == 200
    assert calls[0][0] == "tickets"
    assert calls[0][1]["customer_id"] is None
    assert calls[0][1]["device_id"] is None
    assert calls[0][1]["assigned_user_id"] is None


def test_notes_and_history_routes_delegate_to_database(client, monkeypatch):
    test_client, main = client
    monkeypatch.setattr(
        main, "db_get", lambda table, params="": [{"table": table, "params": params}]
    )
    monkeypatch.setattr(main, "db_post", lambda table, data: {"table": table, **data})

    notes_res = test_client.get("/tickets/t1/notes")
    create_note_res = test_client.post("/notes", json={"ticket_id": "t1", "note_text": "Rebooted"})
    history_res = test_client.get("/tickets/t1/history")

    assert notes_res.status_code == 200
    assert notes_res.json()[0]["table"] == "ticket_notes"
    assert create_note_res.status_code == 200
    assert create_note_res.json()["table"] == "ticket_notes"
    assert history_res.status_code == 200
    assert history_res.json()[0]["table"] == "ticket_history"


def test_rma_routes_delegate_to_database(client, monkeypatch):
    test_client, main = client
    calls = []
    monkeypatch.setattr(
        main, "db_get", lambda table, params="": [{"id": "r1", "resolution_status": "Pending"}]
    )
    monkeypatch.setattr(
        main, "db_post", lambda table, data: calls.append(("post", table, data)) or data
    )
    monkeypatch.setattr(
        main,
        "db_patch",
        lambda table, row_id, data: calls.append(("patch", table, row_id, data)) or data,
    )

    list_res = test_client.get("/rmas")
    create_res = test_client.post("/rmas", json={"ticket_id": "t1", "rma_number": "RMA-1"})
    update_res = test_client.put(
        "/rmas/r1", json={"ticket_id": "t1", "rma_number": "RMA-1", "resolution_status": "Shipped"}
    )

    assert list_res.status_code == 200
    assert create_res.status_code == 200
    assert update_res.status_code == 200
    assert calls[0][0:2] == ("post", "rmas")
    assert calls[1][0:3] == ("patch", "rmas", "r1")


def test_dashboard_counts_ticket_and_rma_statuses(client, monkeypatch):
    test_client, main = client

    def fake_get(table, params=""):
        if table == "tickets":
            return [
                {"status": "Open", "priority": "Critical"},
                {"status": "In Progress", "priority": "Medium"},
                {"status": "Closed", "priority": "Low"},
            ]
        return [{"resolution_status": "Pending"}, {"resolution_status": "Resolved"}]

    monkeypatch.setattr(main, "db_get", fake_get)

    res = test_client.get("/dashboard")

    assert res.status_code == 200
    assert res.json() == {
        "open_tickets": 1,
        "in_progress": 1,
        "closed_tickets": 1,
        "critical": 1,
        "rmas_in_progress": 1,
    }


def test_ai_suggest_returns_matches(client):
    test_client, main = client
    main.ai.suggest_for_ticket.return_value = {"matches": [{"ticket_id": "past-1"}]}

    res = test_client.post("/ai/suggest", json={"ticket_id": "t1"})

    assert res.status_code == 200
    assert res.json() == {"matches": [{"ticket_id": "past-1"}]}
    main.ai.suggest_for_ticket.assert_called_with("t1")


@pytest.mark.parametrize(
    ("error", "expected_status"),
    [
        (ValueError("Ticket t1 not found"), 404),
        (RuntimeError("ANTHROPIC_API_KEY is not set"), 503),
        (Exception("boom"), 500),
    ],
)
def test_ai_suggest_maps_errors_to_http_responses(client, error, expected_status):
    test_client, main = client
    main.ai.suggest_for_ticket.side_effect = error

    res = test_client.post("/ai/suggest", json={"ticket_id": "t1"})

    assert res.status_code == expected_status
