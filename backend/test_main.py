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
    sys.modules["ai"] = fake_ai
    import importlib
    import database
    import main
    importlib.reload(database)
    importlib.reload(main)
    return TestClient(main.app), main


def test_health_returns_ok(client):
    test_client, _ = client
    res = test_client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}

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
