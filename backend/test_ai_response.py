"""Tests for how ai.suggest_for_ticket handles unexpected model output.

test_main.py replaces ``sys.modules["ai"]`` with a stub, so load the real module
directly from its file.
"""

import importlib.util
import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def real_ai(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "http://fake.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "fake-key")
    spec = importlib.util.spec_from_file_location("ai_real", Path(__file__).with_name("ai.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "_fetch_ticket", lambda _id: {"id": "t1", "title": "x"})
    monkeypatch.setattr(module, "_fetch_notes", lambda _id: [])
    monkeypatch.setattr(module, "_fetch_recent_resolved", lambda limit=30: [{"id": "p1"}])
    return module


def _model_says(module, monkeypatch, text):
    block = MagicMock(type="text", text=text)
    client = MagicMock()
    client.messages.create.return_value = MagicMock(content=[block])
    monkeypatch.setattr(module, "_get_client", lambda: client)


@pytest.mark.parametrize("payload", ['{"matches": null}', '{"matches": "none"}', "[1, 2]", "{}"])
def test_unexpected_shape_returns_error_not_exception(real_ai, monkeypatch, payload):
    _model_says(real_ai, monkeypatch, payload)
    result = real_ai.suggest_for_ticket("t1")
    assert result["matches"] == []
    assert result["error"] == "Model returned an unexpected response shape"


def test_valid_matches_are_capped_at_three(real_ai, monkeypatch):
    matches = [{"ticket_id": str(i)} for i in range(5)]
    _model_says(real_ai, monkeypatch, json.dumps({"matches": matches}))
    assert real_ai.suggest_for_ticket("t1") == {"matches": matches[:3]}
