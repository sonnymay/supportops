"""Tests for ai.suggest_for_ticket (the real ai module, not the stub used in test_main)."""

import importlib
import sys
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def ai(monkeypatch):
    sys.modules.pop("ai", None)
    module = importlib.import_module("ai")
    yield module
    sys.modules.pop("ai", None)


def test_suggest_excludes_the_ticket_itself(ai, monkeypatch):
    target = {"id": "t1", "title": "Printer jam", "status": "Closed"}
    other = {"id": "t2", "title": "Paper jam", "status": "Resolved"}
    monkeypatch.setattr(ai, "_fetch_ticket", lambda _id: target)
    monkeypatch.setattr(ai, "_fetch_notes", lambda _id: [])
    monkeypatch.setattr(ai, "_fetch_recent_resolved", lambda limit=30: [dict(target), dict(other)])

    captured = {}

    def fake_build(ticket, notes, history):
        captured["history"] = history
        return "prompt"

    monkeypatch.setattr(ai, "_build_prompt", fake_build)
    client = MagicMock()
    client.messages.create.return_value = MagicMock(
        content=[MagicMock(type="text", text='{"matches": []}')]
    )
    monkeypatch.setattr(ai, "_get_client", lambda: client)

    ai.suggest_for_ticket("t1")

    assert [t["id"] for t in captured["history"]] == ["t2"]


def test_suggest_with_only_itself_in_history_returns_note(ai, monkeypatch):
    target = {"id": "t1", "title": "Printer jam", "status": "Closed"}
    monkeypatch.setattr(ai, "_fetch_ticket", lambda _id: target)
    monkeypatch.setattr(ai, "_fetch_notes", lambda _id: [])
    monkeypatch.setattr(ai, "_fetch_recent_resolved", lambda limit=30: [dict(target)])
    monkeypatch.setattr(ai, "_get_client", lambda: pytest.fail("model must not be called"))

    result = ai.suggest_for_ticket("t1")

    assert result["matches"] == []
    assert "No resolved tickets" in result["note"]
