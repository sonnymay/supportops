from unittest.mock import MagicMock

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
    fake_response.json.return_value = [{"id": "1"}]
    fake_requests = MagicMock()
    fake_requests.get.return_value = fake_response
    fake_requests.post.return_value = fake_response
    fake_requests.patch.return_value = fake_response
    fake_requests.delete.return_value = fake_response
    monkeypatch.setattr(database, "requests", fake_requests)

    assert database.db_get("tickets", "id=eq.1") == [{"id": "1"}]
    assert database.db_post("tickets", {"title": "Issue"}) == [{"id": "1"}]
    assert database.db_patch("tickets", "1", {"status": "Closed"}) == [{"id": "1"}]
    assert database.db_delete("tickets", "1") == [{"id": "1"}]

    fake_requests.get.assert_called_once_with(
        "https://example.supabase.co/rest/v1/tickets?id=eq.1",
        headers=database.get_headers(),
    )
    fake_requests.post.assert_called_once_with(
        "https://example.supabase.co/rest/v1/tickets",
        headers=database.get_headers(),
        json={"title": "Issue"},
    )
    fake_requests.patch.assert_called_once_with(
        "https://example.supabase.co/rest/v1/tickets?id=eq.1",
        headers=database.get_headers(),
        json={"status": "Closed"},
    )
    fake_requests.delete.assert_called_once_with(
        "https://example.supabase.co/rest/v1/tickets?id=eq.1",
        headers=database.get_headers(),
    )
