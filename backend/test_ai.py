"""Tests for ai.py filter construction. Loads the real module under a private name,
since test_main.py stubs ``sys.modules["ai"]``."""

import importlib.util
from pathlib import Path
from unittest.mock import patch

_spec = importlib.util.spec_from_file_location("ai_real", Path(__file__).with_name("ai.py"))
ai_real = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ai_real)


def test_fetch_ticket_escapes_id():
    with patch.object(ai_real, "db_get", return_value=[{"id": "x"}]) as db_get:
        ai_real._fetch_ticket("a&select=*")
    db_get.assert_called_once_with("tickets", "id=eq.a%26select%3D%2A")


def test_fetch_notes_escapes_ticket_id():
    with patch.object(ai_real, "db_get", return_value=[]) as db_get:
        ai_real._fetch_notes("a&limit=1")
    db_get.assert_called_once_with(
        "ticket_notes", "ticket_id=eq.a%26limit%3D1&order=created_at.asc"
    )
